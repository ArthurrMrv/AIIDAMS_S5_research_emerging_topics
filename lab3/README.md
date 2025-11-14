# Lab 3: Steel Industry Emissions Analysis - China Case Study

A comprehensive analysis of steel plant emissions in China, including plant-level production calculation, emissions estimation using technology-specific emission factors, company-level aggregation, and future emissions projections with uncertainty quantification.

## 🎯 Project Overview

This project implements a complete emissions analysis pipeline for the Chinese steel industry:

1. **Data Preparation**: Load and process steel plant operational data
2. **Operational Analysis**: Determine which plants are operating in each year (2020-2030)
3. **Production Calculation**: Calculate plant-level production using capacity and utilization rates
4. **Emissions Estimation**: Compute emissions using technology-specific emission factors
5. **Company Aggregation**: Aggregate plant-level data to company level
6. **Future Projections**: Project company emissions into the future with uncertainty quantification

## 📊 Methodology

### Utilization Rates
- **Country-level**: Based on World Steel Association production data and OECD capacity reports
- **Technology-specific**: Different rates for BF-BOF (blast furnace) and EAF (electric arc furnace)
- **Declining BF-BOF utilization**: 85% (2020) → 75% (2030)
- **Increasing EAF utilization**: 75% (2020) → 85% (2030)

### Emission Factors
Based on Hasanbeigi et al. reports for Chinese steel production:
- **BF-BOF (primary steelmaking)**: 2.0 tonnes CO2 per tonne steel
- **EAF (secondary steelmaking)**: 0.5 tonnes CO2 per tonne steel
- **DRI**: 1.5 tonnes CO2 per tonne steel
- **Other/Unknown**: 1.8 tonnes CO2 per tonne steel

### Projection Methods
- **Linear Regression**: Simple trend extrapolation
- **Exponential**: Growth/decay modeling
- **Moving Average**: Recent trend-based projection
- **Uncertainty Quantification**: Bootstrap resampling with 95% confidence intervals

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Steel plants dataset from Lab 1

### Installation
```bash
# Navigate to lab3 directory
cd lab3

# Install dependencies
pip install -r requirements.txt
```

### Running the Analysis
```bash
# Run complete analysis (with plots)
python main.py

# Skip projection step
python main.py --skip-projection

# Skip visualization plots
python main.py --skip-plots

# Custom projection years
python main.py --projection-years 2031 2032 2033 2034 2035

# Use exponential projection
python main.py --projection-method exponential

# Don't use technology-specific rates
python main.py --no-tech-rates

# Combine options
python main.py --projection-method exponential --skip-plots
```

## 📁 Project Structure

```
lab3/
├── config.py                    # Configuration and constants
├── data_loader.py              # Data loading and preprocessing
├── plant_operations.py         # Operational status determination
├── utilization.py              # Production calculation
├── emissions.py                # Emissions calculation
├── aggregation.py              # Company-level aggregation
├── projection.py               # Future emissions projection
├── visualization.py            # Plotting and visualizations
├── main.py                     # Main orchestration script
├── example_usage.py            # Usage examples
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── output/                     # Generated output files
    ├── operational_plants_2020_2030.csv
    ├── china_plant_production.csv
    ├── china_plant_emissions.csv
    ├── company_emissions.csv
    ├── emissions_by_year.csv
    ├── emissions_by_technology.csv
    ├── emissions_by_company.csv
    ├── emissions_projection.csv
    └── plots/                  # Visualization outputs
        ├── emissions_by_year.png
        ├── emissions_by_technology.png
        ├── top_emitters.png
        ├── company_trends.png
        ├── capacity_utilization.png
        ├── technology_transition.png
        ├── emission_factors.png
        └── emissions_projections.png
```

## 🔧 Module Descriptions

### config.py
Central configuration file containing:
- File paths and directories
- Analysis parameters (years, country)
- China steel production and capacity data
- Technology-specific utilization rates
- Emission factors by technology
- Projection parameters

### data_loader.py
Functions for loading and preprocessing steel plant data:
- `load_steel_dataset()`: Load raw data
- `preprocess_dates()`: Clean date columns
- `clean_capacity_data()`: Validate capacity values
- `standardize_technology()`: Map technology names
- `prepare_steel_data()`: Complete preparation pipeline

### plant_operations.py
Determine operational status for each year:
- `is_plant_operational()`: Check if plant operates in given year
- `create_operational_dataset()`: Generate plant-year records
- `determine_end_year()`: Calculate plant closure year

### utilization.py
Calculate plant-level production:
- `get_utilization_rate()`: Get technology-specific rates
- `calculate_plant_production()`: Compute production = capacity × utilization
- `compare_with_reported_production()`: Validate against national data

### emissions.py
Calculate plant-level emissions:
- `get_emission_factor()`: Get technology-specific factors
- `calculate_plant_emissions()`: Compute emissions = production × factor
- `export_emissions_summary_tables()`: Generate summary reports

### aggregation.py
Aggregate to company level:
- `aggregate_by_company_and_year()`: Company-year aggregation
- `aggregate_by_company_total()`: Total company aggregation
- `get_company_technology_mix()`: Technology distribution

### projection.py
Project future emissions:
- `linear_projection()`: Linear trend projection
- `exponential_projection()`: Exponential growth/decay
- `moving_average_projection()`: Recent trend extrapolation
- `bootstrap_projection()`: Uncertainty quantification
- `project_all_companies()`: Batch projection

### visualization.py
Create comprehensive plots and visualizations:
- `plot_emissions_by_year()`: Annual emissions trends
- `plot_emissions_by_technology()`: Technology-specific emissions
- `plot_top_emitters()`: Top emitting companies
- `plot_company_trends()`: Company-specific time series
- `plot_projections()`: Future projections with uncertainty
- `plot_capacity_utilization()`: Capacity and utilization trends
- `plot_technology_transition()`: Technology mix evolution
- `plot_emission_factors_distribution()`: Emission factor analysis
- `create_all_plots()`: Generate complete visualization suite

### main.py
Orchestration script that runs the complete pipeline.

## 📈 Output Files

### 1. operational_plants_2020_2030.csv
Plant-year level data showing operational status for each year.
**Columns**: All plant attributes + year + operational status

### 2. china_plant_production.csv
Plant-year level production data.
**Columns**: Plant info + year + capacity + utilization_rate + production

### 3. china_plant_emissions.csv
Plant-year level emissions data.
**Columns**: Plant info + year + production + emission_factor + emissions

### 4. company_emissions.csv
Company-year level aggregated emissions.
**Columns**: company + year + total_emissions + total_production + plant_count

### 5. emissions_by_year.csv
Annual emissions summary.
**Columns**: year + total_emissions + emissions_intensity + plant_count

### 6. emissions_by_technology.csv
Emissions breakdown by technology and year.
**Columns**: year + technology + emissions + production + emission_factor

### 7. emissions_by_company.csv
Total company emissions (all years).
**Columns**: company + total_emissions + production + avg_emission_factor

### 8. emissions_projection.csv
Future emissions projections with confidence intervals.
**Columns**: company + year + projected_emissions + lower_bound + upper_bound

### 9. plots/ directory
Visualization outputs (PNG format, 300 DPI):
- **emissions_by_year.png**: Total emissions and intensity trends
- **emissions_by_technology.png**: Stacked area and share by technology
- **top_emitters.png**: Horizontal bar chart of top 10 companies
- **company_trends.png**: Multi-line plot of company emissions over time
- **capacity_utilization.png**: Capacity vs production and utilization rates
- **technology_transition.png**: Technology capacity evolution
- **emission_factors.png**: Distribution and boxplots by technology
- **emissions_projections.png**: Historical + projected with confidence intervals

## 📊 Key Results

### Production Analysis
- Total production calculated from capacity and utilization rates
- Comparison with reported national statistics
- Technology-specific production trends

### Emissions Analysis
- Plant-level emissions by technology
- Company-level aggregation
- Temporal trends (2020-2030)

### Future Projections
- Company-level emissions forecasts
- Uncertainty quantification (95% CI)
- Multiple projection methods available

## 🔍 Data Sources

### Input Data
- **Steel Plants Dataset**: From Lab 1 (Global Steel Plant Tracker)
- **Production Data**: World Steel Association reports
- **Capacity Data**: OECD Steel Capacity Database
- **Emission Factors**: Hasanbeigi et al. (2016) "Bottom-Up Energy Analysis of Chinese Iron and Steel Industry"

### References
1. World Steel Association (2024). "Steel Statistical Yearbook"
2. OECD (2024). "Steel Capacity Report"
3. Hasanbeigi, A., et al. (2016). "Bottom-Up Energy Analysis of Chinese Iron and Steel Industry"
4. Global Energy Monitor. "Global Steel Plant Tracker"

## 🎛️ Configuration Options

### Analysis Period
Modify `START_YEAR` and `END_YEAR` in `config.py` to change analysis period.

### Utilization Rates
Edit `CHINA_UTILIZATION_TECH` dictionary in `config.py` to adjust rates:
```python
CHINA_UTILIZATION_TECH = {
    "BF-BOF": {2020: 0.85, 2021: 0.84, ...},
    "EAF": {2020: 0.75, 2021: 0.76, ...}
}
```

### Emission Factors
Modify `EMISSION_FACTORS_CHINA` in `config.py`:
```python
EMISSION_FACTORS_CHINA = {
    "BF-BOF": 2.0,
    "EAF": 0.5,
    ...
}
```

### Projection Parameters
Adjust in `config.py`:
```python
CONFIDENCE_LEVEL = 0.95
N_BOOTSTRAP_SAMPLES = 1000
```

## 🧪 Testing Individual Modules

Each module can be run independently for testing:

```bash
# Test data loading
python data_loader.py

# Test operational dataset creation
python plant_operations.py

# Test production calculation
python utilization.py

# Test emissions calculation
python emissions.py

# Test company aggregation
python aggregation.py

# Test projections
python projection.py

# Test visualizations
python visualization.py
```

## 📊 Visualizations

The `visualization.py` module creates publication-quality plots using matplotlib and seaborn:

### Available Plots

1. **Emissions Trends** (`plot_emissions_by_year`)
   - Line plot of total annual emissions
   - Emissions intensity over time
   
2. **Technology Analysis** (`plot_emissions_by_technology`)
   - Stacked area chart of emissions by technology
   - Technology share evolution
   
3. **Company Rankings** (`plot_top_emitters`)
   - Horizontal bar chart of top emitters
   - Color-coded by emission level
   
4. **Company Trends** (`plot_company_trends`)
   - Multi-line time series for top companies
   - Comparative emissions trajectories
   
5. **Projections** (`plot_projections`)
   - Historical data + future projections
   - 95% confidence intervals shaded
   
6. **Capacity & Utilization** (`plot_capacity_utilization`)
   - Capacity vs production over time
   - Utilization rate trends
   
7. **Technology Transition** (`plot_technology_transition`)
   - Technology capacity evolution
   - Share of total capacity
   
8. **Emission Factors** (`plot_emission_factors_distribution`)
   - Boxplots by technology
   - Distribution histograms

### Customization

All plots can be customized through function parameters:
```python
from visualization import plot_emissions_by_year

# Create custom plot
fig = plot_emissions_by_year(df_emissions, save=False)
plt.show()

# Or save with custom settings
fig = plot_emissions_by_year(df_emissions, save=True)
```

## 📚 Learning Objectives

- ✅ Data preparation and cleaning for emissions analysis
- ✅ Temporal analysis (operational status across years)
- ✅ Technology-specific utilization rates
- ✅ Emissions factor methodology
- ✅ Multi-level aggregation (plant → company)
- ✅ Time series projection methods
- ✅ Uncertainty quantification
- ✅ Function-oriented code organization

## 🔄 Future Enhancements

- **Spatial Analysis**: Geographic clustering of emissions
- **Scenario Analysis**: Different decarbonization pathways
- **Technology Transitions**: Model BF-BOF to EAF shifts
- **Economic Analysis**: Cost implications of emission reductions
- **Visualization**: Interactive dashboards with plotly/streamlit
- **API Development**: REST API for emissions queries

## 🤝 Contributing

This is an academic project for the AIDAMS Research & Emerging Topics course (Lab 3).

## 📄 License

This project is part of academic coursework. Data sources should be properly cited when used.

---

**Note**: Emission factors and utilization rates are based on literature values and should be validated with local data for production use.

**Built with ❤️ using Python, pandas, and numpy**

