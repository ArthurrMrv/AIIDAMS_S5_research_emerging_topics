import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ---- PAGE CONFIGURATION ----
st.set_page_config(
    page_title="Steel Plants Geospatial Analysis Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(data_dir="data"):
    """Load all datasets with caching for better performance."""
    data = {}
    # Required
    if os.path.exists(os.path.join(data_dir, "operating_plants.csv")):
        data['operating_plants'] = pd.read_csv(os.path.join(data_dir, "operating_plants.csv"))
    else:
        st.error("operating_plants.csv not found. Please run the analysis first.")
        return None
    # Optional
    if os.path.exists(os.path.join(data_dir, "merged_environmental_data.csv")):
        data['merged_environmental'] = pd.read_csv(os.path.join(data_dir, "merged_environmental_data.csv"))
    if os.path.exists(os.path.join(data_dir, "company_aggregation.csv")):
        data['company_aggregation'] = pd.read_csv(os.path.join(data_dir, "company_aggregation.csv"))
    return data

def create_metrics_row(df):
    """Show row of KPIs at the top."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Operating Plants", f"{len(df):,}")
    with col2:
        tc = df['Nominal crude steel capacity (ttpa)'].sum() if 'Nominal crude steel capacity (ttpa)' in df.columns else 0
        st.metric("Total Global Capacity", f"{tc:,.0f} ttpa")
    with col3:
        avgc = df['Nominal crude steel capacity (ttpa)'].mean() if 'Nominal crude steel capacity (ttpa)' in df.columns else 0
        st.metric("Average Plant Capacity", f"{avgc:,.0f} ttpa")
    with col4:
        ncountries = df['Country/Area_x'].nunique() if 'Country/Area_x' in df.columns else 0
        st.metric("Countries with Plants", f"{ncountries}")

def create_geographic_map(df, map_type="scatter"):
    """Create interactive map visualizations."""
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        st.warning("Latitude and longitude columns not found in the data.")
        return None
    df_clean = df.dropna(subset=['latitude', 'longitude'])
    if map_type == "scatter":
        fig = px.scatter_mapbox(
            df_clean,
            lat="latitude", lon="longitude",
            color="Country/Area_x" if "Country/Area_x" in df_clean.columns else None,
            hover_name="Plant name (English)_x" if "Plant name (English)_x" in df_clean.columns else None,
            hover_data={
                "Owner": True,
                "Nominal crude steel capacity (ttpa)": True,
                "latitude": False,
                "longitude": False,
                "Country/Area_x": False
            },
            title="Geographic Distribution of Operating Steel Plants",
            zoom=1, height=600
        )
    elif map_type == "capacity":
        capcol = 'Nominal crude steel capacity (ttpa)'
        df_clean[capcol] = df_clean[capcol].fillna(0)
        fig = px.scatter_mapbox(
            df_clean,
            lat="latitude", lon="longitude",
            size=capcol,
            color="Owner",
            hover_name="Plant name (English)_x" if "Plant name (English)_x" in df_clean.columns else None,
            hover_data={
                "Owner": True,
                capcol: True,
                "latitude": False,
                "longitude": False,
            },
            title="Steel Plants by Capacity and Owner",
            zoom=1, height=600
        )
    elif map_type == "density":
        fig = px.density_mapbox(
            df_clean,
            lat="latitude",
            lon="longitude",
            radius=10,
            center=dict(lat=0, lon=0),
            zoom=0,
            mapbox_style="open-street-map",
            title="Density Heatmap of Steel Plants"
        )
    else:
        return None
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def create_company_charts(company_df):
    """Create company-level visualizations."""
    if company_df.empty:
        return None
    top_companies = company_df.head(20)
    fig_capacity = px.bar(
        top_companies,
        x="Owner",
        y="total_capacity",
        title="Top 20 Companies by Total Crude Steel Capacity (ttpa)",
        labels={'total_capacity': 'Total Capacity (ttpa)', 'Owner': 'Company'}
    )
    fig_capacity.update_layout(xaxis_tickangle=-45)
    fig_plants = px.bar(
        top_companies,
        x="Owner",
        y="number_of_plants",
        title="Top 20 Companies by Number of Operating Steel Plants",
        labels={'number_of_plants': 'Number of Plants', 'Owner': 'Company'}
    )
    fig_plants.update_layout(xaxis_tickangle=-45)
    fig_countries = px.bar(
        top_companies,
        x="Owner",
        y="number_of_countries",
        title="Top 20 Companies by Geographic Spread (Number of Countries)",
        labels={'number_of_countries': 'Number of Countries', 'Owner': 'Company'}
    )
    fig_countries.update_layout(xaxis_tickangle=-45)
    return fig_capacity, fig_plants, fig_countries

def create_country_analysis(df):
    """Create country-level analysis."""
    country_counts = df['Country/Area_x'].value_counts().head(15)
    fig = px.bar(
        x=country_counts.index,
        y=country_counts.values,
        title="Top 15 Countries by Number of Operating Steel Plants",
        labels={'x': 'Country', 'y': 'Number of Plants'}
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def create_environmental_metrics(df):
    """Create environmental data metrics."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_env_value = df['value'].mean() if 'value' in df.columns else 0
        st.metric("Average Environmental Value", f"{avg_env_value:,.0f}")
    with col2:
        max_env_value = df['value'].max() if 'value' in df.columns else 0
        st.metric("Max Environmental Value", f"{max_env_value:,.0f}")
    with col3:
        min_env_value = df['value'].min() if 'value' in df.columns else 0
        st.metric("Min Environmental Value", f"{min_env_value:,.0f}")
    with col4:
        high_risk_plants = len(df[df['value'] > df['value'].quantile(0.75)]) if 'value' in df.columns else 0
        st.metric("High Risk Plants (Top 25%)", f"{high_risk_plants}")

def create_environmental_map(df, map_type="environmental"):
    """Create environmental risk map visualizations."""
    if 'latitude_left' not in df.columns or 'longitude_left' not in df.columns:
        st.warning("Latitude and longitude columns not found in the environmental data.")
        return None
    
    df_clean = df.dropna(subset=['latitude_left', 'longitude_left', 'value'])
    
    if map_type == "environmental":
        fig = px.scatter_mapbox(
            df_clean,
            lat="latitude_left", lon="longitude_left",
            color="value",
            size="value",
            hover_name="Plant name (English)_x" if "Plant name (English)_x" in df_clean.columns else None,
            hover_data={
                "Owner": True,
                "Country/Area_x": True,
                "value": True,
                "Nominal crude steel capacity (ttpa)": True,
                "latitude_left": False,
                "longitude_left": False
            },
            title="Environmental Risk Distribution of Steel Plants",
            color_continuous_scale="Reds",
            zoom=1, height=600
        )
    elif map_type == "capacity_env":
        capcol = 'Nominal crude steel capacity (ttpa)'
        if capcol in df_clean.columns:
            df_clean[capcol] = df_clean[capcol].fillna(0)
            fig = px.scatter_mapbox(
                df_clean,
                lat="latitude_left", lon="longitude_left",
                size=capcol,
                color="value",
                hover_name="Plant name (English)_x" if "Plant name (English)_x" in df_clean.columns else None,
                hover_data={
                    "Owner": True,
                    "value": True,
                    capcol: True,
                    "latitude_left": False,
                    "longitude_left": False
                },
                title="Steel Plants: Capacity vs Environmental Risk",
                color_continuous_scale="Reds",
                zoom=1, height=600
            )
        else:
            return None
    elif map_type == "density_env":
        fig = px.density_mapbox(
            df_clean,
            lat="latitude_left",
            lon="longitude_left",
            z="value",
            radius=10,
            center=dict(lat=0, lon=0),
            zoom=0,
            mapbox_style="open-street-map",
            title="Environmental Risk Density Heatmap"
        )
    else:
        return None
    
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def create_environmental_analysis(df):
    """Create environmental risk analysis charts."""
    if 'value' not in df.columns:
        st.warning("Environmental value data not available.")
        return None, None, None
    
    # Environmental risk distribution
    fig_dist = px.histogram(
        df, x="value",
        title="Distribution of Environmental Risk Values",
        labels={'value': 'Environmental Risk Value', 'count': 'Number of Plants'},
        nbins=30
    )
    
    # Top plants by environmental risk
    top_risk_plants = df.nlargest(20, 'value')
    fig_top_risk = px.bar(
        top_risk_plants,
        x="Plant name (English)_x" if "Plant name (English)_x" in top_risk_plants.columns else "Owner",
        y="value",
        title="Top 20 Plants by Environmental Risk",
        labels={'value': 'Environmental Risk Value', 'Plant name (English)_x': 'Plant Name'},
        color="value",
        color_continuous_scale="Reds"
    )
    fig_top_risk.update_layout(xaxis_tickangle=-45)
    
    # Environmental risk by country
    if 'Country/Area_x' in df.columns:
        country_env = df.groupby('Country/Area_x')['value'].agg(['mean', 'max', 'count']).reset_index()
        country_env = country_env.sort_values('mean', ascending=False).head(15)
        
        fig_country_env = px.bar(
            country_env,
            x="Country/Area_x",
            y="mean",
            title="Average Environmental Risk by Country (Top 15)",
            labels={'mean': 'Average Environmental Risk', 'Country/Area_x': 'Country'},
            color="mean",
            color_continuous_scale="Reds"
        )
        fig_country_env.update_layout(xaxis_tickangle=-45)
    else:
        fig_country_env = None
    
    return fig_dist, fig_top_risk, fig_country_env

def main():
    # Header
    st.markdown('<h1 class="main-header">🏭 Steel Plants Geospatial Analysis Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    # Load
    data = load_data()
    if data is None: st.stop()
    df = data['operating_plants']

    # ---- SIDEBAR FILTERS ----
    st.sidebar.header("🔍 Filters")

    # Country
    countries = ['All'] + sorted(df['Country/Area_x'].dropna().unique().tolist()) if 'Country/Area_x' in df.columns else ['All']
    selected_country = st.sidebar.selectbox("Select Country", countries)
    # Company
    companies = ['All'] + sorted(df['Owner'].dropna().unique().tolist()) if 'Owner' in df.columns else ['All']
    selected_company = st.sidebar.selectbox("Select Company", companies)
    # Capacity
    capcol = 'Nominal crude steel capacity (ttpa)'
    cap_max = int(df[capcol].max()) if capcol in df.columns else 1
    capacity_range = st.sidebar.slider(
        "Capacity Range (ttpa)",
        min_value=0, max_value=cap_max,
        value=(0, cap_max)
    )
    # Real-time Reload Button (extra, for "Real-time updates" feel, gives user explicit refresh)
    if st.sidebar.button("🔄 Reload Data"):
        st.cache_data.clear()
        st.experimental_rerun()

    # ---- FILTERING LOGIC ----
    filtered_df = df.copy()
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country/Area_x'] == selected_country]
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['Owner'] == selected_company]
    filtered_df = filtered_df[
        (filtered_df[capcol] >= capacity_range[0]) &
        (filtered_df[capcol] <= capacity_range[1])
    ] if capcol in filtered_df.columns else filtered_df

    # ---- MAIN CONTENT ----
    st.header("📊 Key Metrics")
    create_metrics_row(filtered_df)
    st.markdown("---")

    # ---- TABS ----
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗺️ Geographic Maps",
        "🏢 Company Analysis",
        "🌍 Country Analysis",
        "🌱 Environmental Analysis",
        "📈 Data Tables",
        "📋 Raw Data"
    ])

    # 1. Interactive Geographic Maps
    with tab1:
        st.header("Geographic Visualizations")
        # Map type: scatter, capacity, density
        map_type = st.selectbox(
            "Select Map Type",
            ["scatter", "capacity", "density"],
            format_func=lambda x: {
                "scatter": "Scatter Map (by Country)",
                "capacity": "Capacity Map (by Owner)",
                "density": "Density Heatmap"
            }[x]
        )
        fig = create_geographic_map(filtered_df, map_type)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Unable to create map. Check if coordinate data is available.")

    # 2. Company Analysis Tab
    with tab2:
        st.header("Company-Level Analysis")
        agg_present = 'company_aggregation' in data and data['company_aggregation'] is not None and not data['company_aggregation'].empty
        if agg_present:
            company_df = data['company_aggregation']
            # Filter by company and/or country
            if selected_company != 'All':
                company_df = company_df[company_df['Owner'] == selected_company]
            if selected_country != 'All':
                country_companies = filtered_df['Owner'].unique()
                company_df = company_df[company_df['Owner'].isin(country_companies)]
            charts = create_company_charts(company_df)
            if charts:
                fig_capacity, fig_plants, fig_countries = charts
                st.plotly_chart(fig_capacity, use_container_width=True)
                st.plotly_chart(fig_plants, use_container_width=True)
                st.plotly_chart(fig_countries, use_container_width=True)
            else:
                st.info("No company data available for filters.")
        else:
            st.warning("Company aggregation data not available.")

    # 3. Country Analysis Tab
    with tab3:
        st.header("Country-Level Analysis")
        fig_country = create_country_analysis(filtered_df)
        st.plotly_chart(fig_country, use_container_width=True)
        # By capacity
        if capcol in filtered_df.columns:
            country_capacity = filtered_df.groupby('Country/Area_x')[capcol].sum().sort_values(ascending=False).head(15)
            fig_capacity_country = px.bar(
                x=country_capacity.index,
                y=country_capacity.values,
                title="Top 15 Countries by Total Steel Capacity (ttpa)",
                labels={'x': 'Country', 'y': 'Total Capacity (ttpa)'}
            )
            fig_capacity_country.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_capacity_country, use_container_width=True)

    # 4. Environmental Analysis Tab
    with tab4:
        st.header("🌱 Environmental Risk Analysis")
        
        # Check if environmental data is available
        env_present = 'merged_environmental' in data and data['merged_environmental'] is not None and not data['merged_environmental'].empty
        
        if env_present:
            env_df = data['merged_environmental'].copy()
            
            # Apply same filters as main data
            if selected_country != 'All':
                env_df = env_df[env_df['Country/Area_x'] == selected_country]
            if selected_company != 'All':
                env_df = env_df[env_df['Owner'] == selected_company]
            if capcol in env_df.columns:
                env_df = env_df[
                    (env_df[capcol] >= capacity_range[0]) &
                    (env_df[capcol] <= capacity_range[1])
                ]
            
            # Environmental metrics
            st.subheader("📊 Environmental Risk Metrics")
            create_environmental_metrics(env_df)
            st.markdown("---")
            
            # Environmental maps
            st.subheader("🗺️ Environmental Risk Maps")
            env_map_type = st.selectbox(
                "Select Environmental Map Type",
                ["environmental", "capacity_env", "density_env"],
                format_func=lambda x: {
                    "environmental": "Environmental Risk Map",
                    "capacity_env": "Capacity vs Environmental Risk",
                    "density_env": "Environmental Risk Density Heatmap"
                }[x]
            )
            
            env_fig = create_environmental_map(env_df, env_map_type)
            if env_fig:
                st.plotly_chart(env_fig, use_container_width=True)
            else:
                st.warning("Unable to create environmental map. Check if coordinate and environmental data is available.")
            
            st.markdown("---")
            
            # Environmental analysis charts
            st.subheader("📈 Environmental Risk Analysis")
            env_charts = create_environmental_analysis(env_df)
            if env_charts:
                fig_dist, fig_top_risk, fig_country_env = env_charts
                
                if fig_dist:
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                if fig_top_risk:
                    st.plotly_chart(fig_top_risk, use_container_width=True)
                
                if fig_country_env:
                    st.plotly_chart(fig_country_env, use_container_width=True)
            
            st.markdown("---")
            
            # Environmental data summary
            st.subheader("📋 Environmental Data Summary")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top 10 Plants by Environmental Risk")
                if 'value' in env_df.columns and 'Plant name (English)_x' in env_df.columns:
                    top_env_plants = env_df.nlargest(10, 'value')[['Plant name (English)_x', 'Owner', 'Country/Area_x', 'value', capcol]].reset_index(drop=True)
                    st.dataframe(top_env_plants, use_container_width=True)
            
            with col2:
                st.subheader("Environmental Risk Statistics")
                if 'value' in env_df.columns:
                    env_stats = env_df['value'].describe()
                    st.dataframe(pd.DataFrame(env_stats), use_container_width=True)
            
            # Environmental risk distribution by region
            if 'Region' in env_df.columns:
                st.subheader("Environmental Risk by Region")
                region_env = env_df.groupby('Region')['value'].agg(['mean', 'max', 'count']).reset_index()
                region_env = region_env.sort_values('mean', ascending=False)
                st.dataframe(region_env, use_container_width=True)
        
        else:
            st.warning("Environmental data not available. Please ensure merged_environmental_data.csv is present in the data directory.")

    # 5. Data Tables Tab
    with tab5:
        st.header("Data Summary Tables")
        col1, col2 = st.columns(2)
        # Top 10 companies by capacity
        with col1:
            st.subheader("Top 10 Companies by Capacity")
            if capcol in filtered_df.columns and 'Owner' in filtered_df.columns:
                top_comp = filtered_df.groupby('Owner')[capcol].sum().sort_values(ascending=False).head(10)
                st.dataframe(top_comp.reset_index(), use_container_width=True)
        # Top 10 countries by plant count
        with col2:
            st.subheader("Top 10 Countries by Plant Count")
            if 'Country/Area_x' in filtered_df.columns:
                top_countries = filtered_df['Country/Area_x'].value_counts().head(10)
                st.dataframe(top_countries.reset_index(), use_container_width=True)
        # Plant Age Distribution
        if 'Plant age (years)' in filtered_df.columns:
            st.subheader("Plant Age Distribution")
            age_stats = filtered_df['Plant age (years)'].describe()
            st.dataframe(pd.DataFrame(age_stats), use_container_width=True)

    # 6. Raw Data Tab
    with tab6:
        st.header("Raw Data Explorer")
        st.subheader("Dataset Information")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Rows", len(filtered_df))
        with col2: st.metric("Total Columns", len(filtered_df.columns))
        with col3: st.metric("Memory Usage", f"{filtered_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        st.subheader("Column Information")
        column_info = pd.DataFrame({
            'Column': filtered_df.columns,
            'Type': filtered_df.dtypes,
            'Non-Null Count': filtered_df.count(),
            'Null Count': filtered_df.isnull().sum()
        })
        st.dataframe(column_info, use_container_width=True)
        st.subheader("Raw Data")
        st.dataframe(filtered_df, use_container_width=True)

    # ---- FOOTER ----
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Steel Plants Geospatial Analysis Dashboard | Data Source: Steel Plants Dataset & LitPop Environmental Data</p>
        <p>Built with Streamlit and Plotly</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
