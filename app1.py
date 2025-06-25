import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==================== CONFIG ====================
st.set_page_config(page_title="Superstore Dashboard", layout="wide", initial_sidebar_state="expanded")

# ==================== LOAD DATA ====================
@st.cache_data
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
    df["Order_Day"] = df["Order Date"].dt.day # Added for consistency with your column list
    df["Order_Year"] = df["Order Date"].dt.year
    df["State Code"] = df["State"].apply(map_state_code)

    # Categorize discount levels for better analysis
    bins = [-0.01, 0.001, 0.2, 0.5, 1.0] # 0 for no discount, 0-0.2 low, 0.2-0.5 medium, >0.5 high
    labels = ['No Discount', 'Low Discount', 'Medium Discount', 'High Discount']
    df['Discount_Level'] = pd.cut(df['Discount'], bins=bins, labels=labels, right=True)

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
all_regions = sorted(df["Region"].unique())
all_years = sorted(df["Order_Year"].unique())
all_categories = sorted(df["Category"].unique())
all_segments = sorted(df["Segment"].unique())

selected_regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)
selected_years = st.sidebar.multiselect("Order Year", all_years, default=all_years)
selected_categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)
selected_segments = st.sidebar.multiselect("Segment", all_segments, default=all_segments)

filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["Order_Year"].isin(selected_years)) &
    (df["Category"].isin(selected_categories)) &
    (df["Segment"].isin(selected_segments))
]

# Get previous year data for delta calculation in KPIs
prev_year_df = pd.DataFrame()
if selected_years and len(selected_years) == 1 and (min(all_years) < selected_years[0]):
    prev_year = selected_years[0] - 1
    prev_year_df = df[
        (df["Region"].isin(selected_regions)) &
        (df["Order_Year"] == prev_year) &
        (df["Category"].isin(selected_categories)) &
        (df["Segment"].isin(selected_segments))
    ]

# ==================== SECTION: EXECUTIVE OVERVIEW ====================
if section == "Executive Overview":
    st.title("📊 Executive Overview - Performance Metrics")

    # KPI Cards with Delta
    current_sales = filtered_df['Sales'].sum()
    current_profit = filtered_df['Profit'].sum()
    current_profit_margin = current_profit / current_sales if current_sales else 0
    current_orders = filtered_df['Order ID'].nunique()

    prev_sales = prev_year_df['Sales'].sum() if not prev_year_df.empty else 0
    prev_profit = prev_year_df['Profit'].sum() if not prev_year_df.empty else 0
    prev_profit_margin = prev_profit / prev_sales if prev_sales else 0
    prev_orders = prev_year_df['Order ID'].nunique() if not prev_year_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"${current_sales:,.0f}", delta=f"{(current_sales - prev_sales):,.0f}" if prev_sales else None)
    with col2:
        st.metric("Total Profit", f"${current_profit:,.0f}", delta=f"{(current_profit - prev_profit):,.0f}" if prev_profit else None)
    with col3:
        st.metric("Profit Margin", f"{current_profit_margin:.2%}", delta=f"{(current_profit_margin - prev_profit_margin):.2%}" if prev_profit_margin else None)
    with col4:
        st.metric("Total Orders", f"{current_orders}", delta=f"{(current_orders - prev_orders)}" if prev_orders else None)

    st.markdown("---")

    col_exec1, col_exec2 = st.columns(2)
    with col_exec1:
        with st.expander("📈 Yearly Sales & Profit Trends", expanded=True):
            yearly_summary = filtered_df.groupby("Order_Year")[["Sales", "Profit"]].sum().reset_index()
            fig_year = px.bar(yearly_summary, x="Order_Year", y=["Sales", "Profit"],
                              barmode="group",
                              title="Sales and Profit by Year",
                              labels={"Order_Year": "Year", "value": "Amount ($)"},
                              color_discrete_map={'Sales': '#4285F4', 'Profit': '#34A853'}, # Google colors
                              template="plotly_white",
                              hover_data={"Order_Year": True, "value": ":,.0f"})
            fig_year.update_layout(height=400)
            st.plotly_chart(fig_year, use_container_width=True)

    with col_exec2:
        with st.expander("📍 Profit by Region", expanded=True):
            region_summary = filtered_df.groupby("Region")["Profit"].sum().reset_index()
            fig_region = px.bar(region_summary, x="Region", y="Profit",
                                 color="Profit", color_continuous_scale="RdYlGn",
                                 title="Profit Distribution by Region",
                                 labels={"Profit": "Total Profit ($)"},
                                 template="plotly_white",
                                 hover_data={"Profit": ":,.0f"})
            fig_region.update_layout(height=400)
            st.plotly_chart(fig_region, use_container_width=True)
    
    st.markdown("---")

    col_exec3, col_exec4 = st.columns(2)
    with col_exec3:
        with st.expander("🗓️ Monthly Sales & Profit Trends", expanded=True):
            monthly_summary = filtered_df.groupby("Order_Month")[["Sales", "Profit"]].sum().reindex(
                ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            ).reset_index()
            fig_month = px.line(monthly_summary, x="Order_Month", y=["Sales", "Profit"],
                                markers=True,
                                title="Monthly Sales and Profit Trends",
                                labels={"Order_Month": "Month", "value": "Amount ($)"},
                                color_discrete_map={'Sales': '#4285F4', 'Profit': '#34A853'},
                                template="plotly_white",
                                hover_data={"Order_Month": True, "value": ":,.0f"})
            fig_month.update_layout(height=400)
            st.plotly_chart(fig_month, use_container_width=True)
    
    with col_exec4:
        with st.expander("👥 Sales & Profit by Customer Segment", expanded=True):
            segment_summary = filtered_df.groupby("Segment")[["Sales", "Profit"]].sum().reset_index()
            fig_segment = px.bar(segment_summary, x="Segment", y=["Sales", "Profit"],
                                 barmode="group",
                                 title="Sales and Profit by Customer Segment",
                                 labels={"value": "Amount ($)"},
                                 color_discrete_map={'Sales': '#4285F4', 'Profit': '#34A853'},
                                 template="plotly_white",
                                 hover_data={"value": ":,.0f"})
            fig_segment.update_layout(height=400)
            st.plotly_chart(fig_segment, use_container_width=True)

# ==================== SECTION: CATEGORY & PRODUCT ====================
elif section == "Category & Product":
    st.title("📦 Category & Product Analysis")

    with st.expander("Hierarchical Sales & Profit by Category and Sub-Category", expanded=True):
        category_summary = filtered_df.groupby(["Category", "Sub-Category"])[["Sales", "Profit"]].sum().reset_index()
        fig_cat_treemap = px.treemap(category_summary, path=["Category", "Sub-Category"], values="Sales",
                                     color="Profit", color_continuous_scale="RdYlGn",
                                     title="Sales & Profit by Category and Sub-Category (Treemap)",
                                     template="plotly_white",
                                     hover_data={"Sales": ":,.0f", "Profit": ":,.0f"})
        fig_cat_treemap.update_layout(height=600)
        st.plotly_chart(fig_cat_treemap, use_container_width=True)

    col_prod1, col_prod2 = st.columns(2)
    with col_prod1:
        with st.expander("🔝 Top 10 Most Profitable Products", expanded=True):
            top_products = filtered_df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).head(10).reset_index()
            fig_top_prod = px.bar(top_products, x="Profit", y="Product Name", orientation="h",
                                  title="Top 10 Most Profitable Products",
                                  labels={"Profit": "Total Profit ($)", "Product Name": "Product"},
                                  color="Profit", color_continuous_scale="Greens",
                                  template="plotly_white",
                                  hover_data={"Profit": ":,.0f"})
            fig_top_prod.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_top_prod, use_container_width=True)

    with col_prod2:
        with st.expander("⬇️ Top 10 Most Loss-Making Products", expanded=True):
            worst_products = filtered_df.groupby("Product Name")["Profit"].sum().sort_values(ascending=True).head(10).reset_index()
            fig_worst_prod = px.bar(worst_products, x="Profit", y="Product Name", orientation="h",
                                    title="Top 10 Most Loss-Making Products",
                                    labels={"Profit": "Total Profit ($)", "Product Name": "Product"},
                                    color="Profit", color_continuous_scale="Reds_r", # Reversed reds for losses
                                    template="plotly_white",
                                    hover_data={"Profit": ":,.0f"})
            fig_worst_prod.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            st.plotly_chart(fig_worst_prod, use_container_width=True)
    
    with st.expander("🔥 Profitability Heatmap by Sub-Category", expanded=True):
        sub_category_pivot = filtered_df.pivot_table(index="Sub-Category", columns="Category", values="Profit", aggfunc="sum").fillna(0)
        fig_heatmap = px.imshow(sub_category_pivot,
                                 labels=dict(x="Category", y="Sub-Category", color="Profit"),
                                 x=sub_category_pivot.columns,
                                 y=sub_category_pivot.index,
                                 color_continuous_scale="RdYlGn",
                                 title="Profitability Heatmap by Sub-Category and Category",
                                 text_auto=".2s", # Show values on heatmap
                                 aspect="auto")
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)


# ==================== SECTION: CUSTOMER SEGMENTATION ====================
elif section == "Customer Segmentation":
    st.title("👥 Customer Segmentation Analysis")

    col_cust1, col_cust2 = st.columns(2)
    with col_cust1:
        with st.expander("📊 Average Profit per Segment", expanded=True):
            avg_profit_seg = filtered_df.groupby("Segment")["Profit"].mean().reset_index()
            fig_avg_profit_seg = px.pie(avg_profit_seg, names="Segment", values="Profit",
                                        title="Average Profit per Customer Segment",
                                        template="plotly_white",
                                        hover_data={"Profit": ":,.2f"})
            fig_avg_profit_seg.update_traces(textinfo='percent+label', pull=[0.05 if s == avg_profit_seg['Segment'].max() else 0 for s in avg_profit_seg['Segment']])
            st.plotly_chart(fig_avg_profit_seg, use_container_width=True)

    with col_cust2:
        with st.expander("📈 Total Sales per Segment", expanded=True):
            total_sales_seg = filtered_df.groupby("Segment")["Sales"].sum().reset_index()
            fig_total_sales_seg = px.bar(total_sales_seg, x="Segment", y="Sales",
                                         title="Total Sales by Customer Segment",
                                         labels={"Sales": "Total Sales ($)"},
                                         color="Sales", color_continuous_scale="Blues",
                                         template="plotly_white",
                                         hover_data={"Sales": ":,.0f"})
            st.plotly_chart(fig_total_sales_seg, use_container_width=True)

    with st.expander("💰 Top 10 Most Profitable Customers", expanded=True):
        top_customers = filtered_df.groupby("Customer Name")["Profit"].sum().sort_values(ascending=False).head(10).reset_index()
        fig_top_cust = px.bar(top_customers, x="Profit", y="Customer Name", orientation="h",
                              title="Top 10 Most Profitable Customers",
                              labels={"Profit": "Total Profit ($)", "Customer Name": "Customer"},
                              color="Profit", color_continuous_scale="Greens",
                              template="plotly_white",
                              hover_data={"Profit": ":,.0f"})
        fig_top_cust.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top_cust, use_container_width=True)

# ==================== SECTION: DISCOUNT ANALYSIS ====================
elif section == "Discount Analysis":
    st.title("💸 Discount vs. Performance Analysis")

    col_disc1, col_disc2 = st.columns(2)
    with col_disc1:
        with st.expander("📉 Profit Margin vs. Discount by Category", expanded=True):
            fig_scatter_profit_margin = px.scatter(filtered_df, x="Discount", y="Profit Margin", color="Category",
                                                   hover_name="Product Name",
                                                   title="Profit Margin vs. Discount by Product Category",
                                                   labels={"Discount": "Discount Rate", "Profit Margin": "Profit Margin"},
                                                   trendline="ols", # Add a trendline
                                                   template="plotly_white",
                                                   hover_data={"Sales": ":,.0f", "Profit": ":,.0f", "Discount": ":.2%"})
            st.plotly_chart(fig_scatter_profit_margin, use_container_width=True)

    with col_disc2:
        with st.expander("📊 Discount Distribution", expanded=True):
            fig_hist_discount = px.histogram(filtered_df, x="Discount", nbins=20,
                                             title="Distribution of Discount Rates",
                                             labels={"Discount": "Discount Rate"},
                                             template="plotly_white")
            st.plotly_chart(fig_hist_discount, use_container_width=True)
    
    with st.expander("📈 Average Sales & Profit by Discount Level", expanded=True):
        discount_level_summary = filtered_df.groupby('Discount_Level')[['Sales', 'Profit']].mean().reset_index()
        fig_avg_disc_level = px.bar(discount_level_summary, x='Discount_Level', y=['Sales', 'Profit'],
                                    barmode='group',
                                    title="Average Sales & Profit by Discount Level",
                                    labels={"value": "Average Amount ($)", "Discount_Level": "Discount Level"},
                                    color_discrete_map={'Sales': '#4285F4', 'Profit': '#34A853'},
                                    template="plotly_white",
                                    hover_data={"value": ":,.0f"})
        st.plotly_chart(fig_avg_disc_level, use_container_width=True)


# ==================== SECTION: TIME SERIES ====================
elif section == "Time Series":
    st.title("📈 Time Series Analysis")

    time_series_metric = st.selectbox("Select Metric for Time Series:", ["Sales", "Profit", "Profit Margin"])

    with st.expander(f"🗓️ Monthly {time_series_metric} Trends", expanded=True):
        monthly_trends = filtered_df.groupby("Order_Month")[[time_series_metric]].sum().reindex(
            ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        ).reset_index()
        
        # Adjust y-axis label based on selected metric
        y_label = "Amount ($)"
        if time_series_metric == "Profit Margin":
            y_label = "Profit Margin (%)"

        fig_monthly_trend = px.line(monthly_trends, x="Order_Month", y=time_series_metric,
                                    markers=True,
                                    title=f"Monthly {time_series_metric} Trends",
                                    labels={"Order_Month": "Month", time_series_metric: y_label},
                                    template="plotly_white",
                                    hover_data={time_series_metric: ":,.2f" if time_series_metric == "Profit Margin" else ":,.0f"})
        st.plotly_chart(fig_monthly_trend, use_container_width=True)
    
    with st.expander(f"📊 Yearly {time_series_metric} Trends", expanded=True):
        yearly_trends = filtered_df.groupby("Order_Year")[[time_series_metric]].sum().reset_index()
        
        # Adjust y-axis label based on selected metric
        y_label = "Amount ($)"
        if time_series_metric == "Profit Margin":
            y_label = "Profit Margin (%)"

        fig_yearly_trend = px.line(yearly_trends, x="Order_Year", y=time_series_metric,
                                    markers=True,
                                    title=f"Yearly {time_series_metric} Trends",
                                    labels={"Order_Year": "Year", time_series_metric: y_label},
                                    template="plotly_white",
                                    hover_data={time_series_metric: ":,.2f" if time_series_metric == "Profit Margin" else ":,.0f"})
        st.plotly_chart(fig_yearly_trend, use_container_width=True)

# ==================== SECTION: GEO PROFIT MAP ====================
elif section == "Geo Profit Map":
    st.title("🗺️ Profit Distribution by State (Map)")

    with st.expander("📍 Profit by State on U.S. Map", expanded=True):
        state_summary = filtered_df.groupby(["State", "State Code"])["Profit"].sum().reset_index()
        fig_map = px.choropleth(
            state_summary,
            locations="State Code",
            locationmode="USA-states",
            color="Profit",
            color_continuous_scale="RdYlGn",
            scope="usa",
            labels={"Profit": "Total Profit ($)"},
            title="Total Profit Distribution by U.S. State",
            template="plotly_white",
            hover_data={"State": True, "Profit": ":,.0f"} # Added State name to hover
        )
        fig_map.update_layout(title_x=0.5)
        st.plotly_chart(fig_map, use_container_width=True)

st.caption("📊 Dashboard dikembangkan oleh Sahrul Firdaus · Visual enhanced with Plotly · Mode: Strategic + Analytical")