import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================== CONFIG ====================
st.set_page_config(page_title="Superstore Dashboard", layout="wide")

# ==================== LOAD DATA ====================
def map_state_code(state_name):
    state_dict = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
        'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
        'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    return state_dict.get(state_name, None)

@st.cache_data
def load_data():
    df = pd.read_csv("final_data_superstore.csv", encoding='ISO-8859-1', parse_dates=["Order Date", "Ship Date"])
    df["Profit Margin"] = df["Profit"] / df["Sales"]
    df["Profit_Per_Quantity"] = df["Profit"] / df["Quantity"]
    df["Discounted"] = df["Discount"].apply(lambda x: "Yes" if x > 0 else "No")
    df["Order_Month"] = df["Order Date"].dt.strftime("%B")
    df["Order_Year"] = df["Order Date"].dt.year
    df["State Code"] = df["State"].apply(map_state_code)
    return df

df = load_data()

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title("📊 Superstore Navigation")
section = st.sidebar.selectbox("📁 Pilih Halaman:", [
    "Executive Overview",
    "Category & Product",
    "Customer Segmentation",
    "Discount Analysis",
    "Time Series",
    "Geo Profit Map"
])

# ==================== FILTER ====================
st.sidebar.header("🎛️ Filter Data")
regions = st.sidebar.multiselect("Region", df["Region"].unique(), default=df["Region"].unique())
years = st.sidebar.multiselect("Order Year", sorted(df["Order_Year"].unique()), default=sorted(df["Order_Year"].unique()))
categories = st.sidebar.multiselect("Category", df["Category"].unique(), default=df["Category"].unique())
segments = st.sidebar.multiselect("Segment", df["Segment"].unique(), default=df["Segment"].unique())

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Order_Year"].isin(years)) &
    (df["Category"].isin(categories)) &
    (df["Segment"].isin(segments))
]

# ==================== SECTION: EXECUTIVE OVERVIEW ====================
if section == "Executive Overview":
    st.title("📊 Executive Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
    col2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
    col3.metric("Profit Margin", f"{(filtered_df['Profit'].sum()/filtered_df['Sales'].sum()):.2%}")
    col4.metric("Total Orders", f"{filtered_df['Order ID'].nunique()}")

    st.subheader("Profit by Region")
    region_chart = filtered_df.groupby("Region")["Profit"].sum().reset_index()
    fig_region = px.bar(region_chart, x="Region", y="Profit", color="Profit", color_continuous_scale="RdYlGn", template="plotly_white")
    st.plotly_chart(fig_region, use_container_width=True)

    st.subheader("Yearly Sales & Profit")
    yearly = filtered_df.groupby("Order_Year")[["Sales", "Profit"]].sum().reset_index()
    fig_year = px.bar(yearly, x="Order_Year", y=["Sales", "Profit"], barmode="group", template="plotly_white")
    st.plotly_chart(fig_year, use_container_width=True)

# ==================== SECTION: CATEGORY & PRODUCT ====================
elif section == "Category & Product":
    st.title("📦 Category & Product Analysis")
    category_chart = filtered_df.groupby(["Category", "Sub-Category"])[["Sales", "Profit"]].sum().reset_index()
    fig_cat = px.treemap(category_chart, path=["Category", "Sub-Category"], values="Sales", color="Profit", color_continuous_scale="RdYlGn", template="plotly_white")
    st.plotly_chart(fig_cat, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Most Profitable Products")
        top_products = filtered_df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).head(10)
        st.dataframe(top_products.reset_index())
    with col2:
        st.subheader("Top 10 Most Loss-Making Products")
        worst_products = filtered_df.groupby("Product Name")["Profit"].sum().sort_values().head(10)
        st.dataframe(worst_products.reset_index())

# ==================== SECTION: CUSTOMER SEGMENTATION ====================
elif section == "Customer Segmentation":
    st.title("👥 Customer Segmentation")
    seg_chart = filtered_df.groupby("Segment")["Profit"].mean().reset_index()
    fig_seg = px.pie(seg_chart, names="Segment", values="Profit", title="Avg Profit per Segment", template="plotly_white")
    st.plotly_chart(fig_seg, use_container_width=True)

    st.subheader("Top 10 Most Profitable Customers")
    top_customers = filtered_df.groupby("Customer Name")["Profit"].sum().sort_values(ascending=False).head(10)
    st.dataframe(top_customers.reset_index())

# ==================== SECTION: DISCOUNT ANALYSIS ====================
elif section == "Discount Analysis":
    st.title("💸 Discount vs Profit Analysis")
    fig_scatter = px.scatter(filtered_df, x="Discount", y="Profit", color="Category", hover_data=["Product Name"], template="plotly_white")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Discount Distribution")
    fig_hist = px.histogram(filtered_df, x="Discount", nbins=20, title="Distribution of Discounts", template="plotly_white")
    st.plotly_chart(fig_hist, use_container_width=True)

# ==================== SECTION: TIME SERIES ====================
elif section == "Time Series":
    st.title("📈 Monthly Trends")
    monthly = filtered_df.groupby("Order_Month")[["Sales", "Profit"]].sum().reset_index()
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    monthly["Order_Month"] = pd.Categorical(monthly["Order_Month"], categories=month_order, ordered=True)
    monthly = monthly.sort_values("Order_Month")

    fig_month = px.line(monthly, x="Order_Month", y=["Sales", "Profit"], markers=True, template="plotly_white")
    st.plotly_chart(fig_month, use_container_width=True)

# ==================== SECTION: GEO PROFIT MAP ====================
elif section == "Geo Profit Map":
    st.title("🗺️ Profit by State (Map)")
    state_chart = filtered_df.groupby(["State", "State Code"])["Profit"].sum().reset_index()
    fig_map = px.choropleth(
        state_chart,
        locations="State Code",
        locationmode="USA-states",
        color="Profit",
        color_continuous_scale="RdYlGn",
        scope="usa",
        labels={"Profit": "Total Profit"},
        template="plotly_white"
    )
    fig_map.update_layout(title_text="Profit Distribution by U.S. State", title_x=0.5)
    st.plotly_chart(fig_map, use_container_width=True)

st.caption("📊 Dashboard dikembangkan oleh Sahrul Firdaus · Visual enhanced with Plotly · Mode: Strategic + Analytical")