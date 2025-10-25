# Steel Plants Geospatial Analysis Dashboard

A comprehensive geospatial analysis project that combines steel plant operational data with environmental risk assessments, providing interactive visualizations and company-level aggregations through a Streamlit dashboard.

## 🎯 Project Overview

This project analyzes global steel plant data by integrating:
- **Steel Plant Operations**: Location, capacity, ownership, and operational details
- **Environmental Risk Data**: LitPop environmental indicators for risk assessment
- **Company Aggregations**: Corporate-level analysis and geographic distribution

The analysis is presented through an interactive Streamlit dashboard with multiple visualization types and filtering capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Required packages (see `requirements.txt`)

### Installation
```bash
# Clone or download the project

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit dashboard
streamlit run streamlit.py
```

### Data Preparation
Before running the dashboard, ensure you have the required data files in the `data/` directory:
- `operating_plants.csv` - Main steel plant dataset
- `merged_environmental_data.csv` - Environmental risk data (optional)
- `company_aggregation.csv` - Company-level aggregations (optional)

## 📊 Dashboard Usage

### Main Features
The Streamlit dashboard provides six main tabs:

1. **🗺️ Geographic Maps**: Interactive maps showing plant locations
   - Scatter maps by country
   - Capacity-weighted maps by owner
   - Density heatmaps

2. **🏢 Company Analysis**: Corporate-level insights
   - Top companies by capacity
   - Geographic spread analysis
   - Plant count distributions

3. **🌍 Country Analysis**: National-level statistics
   - Plant count by country
   - Capacity distribution by country

4. **🌱 Environmental Analysis**: Risk assessment (if environmental data available)
   - Environmental risk maps
   - Risk distribution analysis
   - High-risk plant identification

5. **📈 Data Tables**: Summary statistics and top performers

6. **📋 Raw Data**: Complete dataset exploration

### Filtering Options
- **Country Filter**: Select specific countries
- **Company Filter**: Focus on particular companies
- **Capacity Range**: Filter by plant capacity (ttpa)
- **Real-time Reload**: Refresh data without restarting

## 🏗️ Project Architecture

### Data Flow Architecture

```
Raw Data Sources
├── Steel Plants Dataset (operating_plants.csv)
├── LitPop Environmental Data (dataSept2025.xlsx)
└── Generated Aggregations (company_aggregation.csv)

↓ [Data Processing in lab_1.ipynb]

Processed Datasets
├── operating_plants.csv (cleaned plant data)
├── merged_environmental_data.csv (spatial join)
└── company_aggregation.csv (company aggregations)

↓ [Streamlit Dashboard]

Interactive Visualizations
├── Geographic Maps (Plotly)
├── Company Analysis Charts
├── Environmental Risk Maps
└── Data Tables
```

### File Structure
```
project/
├── lab_1.ipynb              # Main analysis notebook
├── streamlit.py             # Dashboard application
├── requirements.txt         # Python dependencies
├── data/                    # Data directory
│   ├── operating_plants.csv
│   ├── merged_environmental_data.csv
│   ├── company_aggregation.csv
│   └── dataSept2025.xlsx
└── README.md               # This file
```

## 📝 Detailed Analysis Workflow (lab_1.ipynb)

### Part 1: Setup and Data Loading
**Hyperparameters:**
- Data source paths
- Coordinate reference system settings
- Missing value handling strategies

**Functions:**
- `pd.read_csv()` - Data loading
- `df.info()` - Data inspection
- `df.describe()` - Statistical summary

**Run Sections:**
1. Import required libraries (pandas, numpy, plotly, geopandas)
2. Load steel plants dataset
3. Inspect data structure and quality

### Part 2: Exploratory Data Analysis (EDA)
**Hyperparameters:**
- Missing value thresholds
- Outlier detection methods
- Statistical significance levels

**Functions:**
- `df.shape` - Dataset dimensions
- `df.isnull().sum()` - Missing value analysis
- `df.groupby().agg()` - Aggregation functions
- `df.value_counts()` - Categorical analysis

**Run Sections:**
1. **Data Overview**: Shape, columns, missing values
2. **Statistical Summary**: Descriptive statistics for numerical columns
3. **Geographic Distribution**: Country and company analysis
4. **Capacity Analysis**: Production capacity insights

### Part 3: Geospatial Visualization
**Hyperparameters:**
- Map zoom levels
- Marker size scaling factors
- Color schemes and palettes
- Mapbox style preferences

**Functions:**
- `px.scatter_mapbox()` - Interactive scatter maps
- `px.density_mapbox()` - Density heatmaps
- `go.Figure()` - Custom map configurations

**Run Sections:**
1. **Basic Scatter Map**: Plant locations by country
2. **Capacity-weighted Map**: Marker size represents capacity
3. **Density Heatmap**: Plant concentration analysis

### Part 4: Environmental Data Integration
**Hyperparameters:**
- Spatial join distance thresholds
- Coordinate precision settings
- Environmental risk scoring weights

**Functions:**
- `geopandas.sjoin_nearest()` - Spatial joins
- `haversine_distance()` - Distance calculations
- `pd.merge()` - Data merging

**Run Sections:**
1. **Load Environmental Data**: LitPop dataset integration
2. **Spatial Join**: Nearest neighbor matching
3. **Merged Visualization**: Environmental risk mapping

### Part 5: Company-Level Aggregation
**Hyperparameters:**
- Aggregation methods (sum, mean, count)
- Geographic spread calculations
- Representative location algorithms

**Functions:**
- `df.groupby().agg()` - Multi-level aggregations
- `df.centroid()` - Geographic centroids
- `df.nunique()` - Unique value counting

**Run Sections:**
1. **Company Metrics**: Total capacity, plant count, countries
2. **Representative Locations**: Centroid calculations
3. **Company Visualization**: Corporate-level mapping

### Part 6: Dashboard Integration
**Hyperparameters:**
- Data export formats (CSV, Parquet)
- Caching strategies
- Performance optimization settings

**Functions:**
- `df.to_csv()` - Data export
- `st.cache_data` - Streamlit caching
- `pd.read_parquet()` - Efficient data loading

**Run Sections:**
1. **Data Export**: Save processed datasets
2. **Dashboard Preparation**: Format data for Streamlit
3. **Performance Optimization**: Caching and data structures

## 🔧 Technical Implementation

### Core Libraries
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations
- **plotly**: Interactive visualizations
- **streamlit**: Web dashboard framework
- **geopandas**: Geospatial data processing (optional)

### Key Functions in streamlit.py

#### Data Loading
```python
@st.cache_data
def load_data(data_dir="data"):
    """Load all datasets with caching for better performance."""
```

#### Visualization Functions
```python
def create_geographic_map(df, map_type="scatter"):
    """Create interactive map visualizations."""
    
def create_company_charts(company_df):
    """Create company-level visualizations."""
    
def create_environmental_map(df, map_type="environmental"):
    """Create environmental risk map visualizations."""
```

#### Analysis Functions
```python
def create_metrics_row(df):
    """Show row of KPIs at the top."""
    
def create_environmental_analysis(df):
    """Create environmental risk analysis charts."""
```

### Performance Optimizations
- **Streamlit Caching**: `@st.cache_data` decorator for data loading
- **Efficient Data Types**: Optimized pandas data types
- **Lazy Loading**: Load data only when needed
- **Memory Management**: Clear cache on data reload

## 📈 Data Sources

### Primary Dataset
- **Steel Plants Dataset**: Global Iron and Steel Plant Tracker
- **Columns**: Plant name, owner, location, capacity, operational details
- **Geographic Coverage**: Global
- **Temporal Coverage**: Current operating plants

### Environmental Dataset
- **LitPop Database**: Population and activity data
- **Integration Method**: Spatial nearest neighbor join
- **Risk Indicators**: Population density and activity levels
- **Coverage**: Global environmental risk assessment

### Generated Datasets
- **Company Aggregations**: Corporate-level metrics
- **Merged Environmental**: Combined plant and environmental data
- **Geographic Analysis**: Country and regional statistics

## 🎛️ Configuration Options

### Dashboard Settings
```python
# Page configuration
st.set_page_config(
    page_title="Steel Plants Geospatial Analysis Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Map Configuration
```python
# Map styling
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0}
)
```

### Filtering Parameters
- Country selection (dropdown)
- Company selection (dropdown)
- Capacity range (slider)
- Map type selection (radio buttons)

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit.py
```

### Production Deployment
1. **Streamlit Cloud**: Direct GitHub integration
2. **Docker**: Containerized deployment
3. **Heroku**: Cloud platform deployment
4. **AWS/GCP**: Cloud infrastructure

### Environment Variables
```bash
# Optional: Set custom data directory
export DATA_DIR="/path/to/data"
```

## 🔍 Troubleshooting

### Common Issues
1. **Missing Data Files**: Ensure all CSV files are in the `data/` directory
2. **Memory Issues**: Use data filtering to reduce dataset size
3. **Map Loading**: Check internet connection for map tiles
4. **Performance**: Enable caching and reduce data size

### Data Requirements
- **Minimum**: `operating_plants.csv` (required)
- **Full Features**: All three CSV files
- **Memory**: ~100MB for full dataset

## 📚 Learning Objectives Achieved

- ✅ Exploratory Data Analysis on geospatial datasets
- ✅ Interactive map creation with Plotly
- ✅ Environmental data integration with spatial joins
- ✅ Company-level data aggregation
- ✅ Streamlit dashboard development
- ✅ Geospatial visualization best practices

## 🔄 Future Enhancements

- **Real-time Data**: API integration for live updates
- **Advanced Analytics**: Machine learning risk prediction
- **Mobile Support**: Responsive design improvements
- **Export Features**: PDF/Excel report generation
- **User Authentication**: Multi-user access control

## 📄 License

This project is part of the AIDAMS Research Emerging Topics course (Lab 1).

## 👥 Contributing

This is an academic project. For questions or improvements, please contact the course instructor.

---

**Built with ❤️ using Streamlit, Plotly, and Python**
