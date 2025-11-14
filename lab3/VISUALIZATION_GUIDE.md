# Visualization Guide for Lab 3

## Overview

The `visualization.py` module provides comprehensive plotting capabilities for the steel industry emissions analysis. It creates publication-quality figures using matplotlib and seaborn.

## Quick Start

### Run All Visualizations

The easiest way to generate all plots is through the main script:

```bash
# Run complete analysis with plots
python main.py

# Plots will be saved to output/plots/
```

### Skip Plots

If you want to skip visualization (faster execution):

```bash
python main.py --skip-plots
```

### Test Visualizations Only

```bash
# Test visualization module independently
python visualization.py
```

## Available Plots

### 1. Emissions by Year (`plot_emissions_by_year`)

**Description**: Shows total emissions and emissions intensity trends over time.

**Output**: `emissions_by_year.png`

**Features**:
- Left panel: Total annual emissions (line + filled area)
- Right panel: Emissions intensity (tonnes CO₂ per tonne steel)
- Color-coded for clarity

**Usage**:
```python
from visualization import plot_emissions_by_year
fig = plot_emissions_by_year(df_emissions, save=True)
```

### 2. Emissions by Technology (`plot_emissions_by_technology`)

**Description**: Breaks down emissions by production technology.

**Output**: `emissions_by_technology.png`

**Features**:
- Left panel: Stacked area chart (absolute emissions)
- Right panel: Percentage share over time
- Distinguishes BF-BOF (high emissions) vs EAF (low emissions)

**Usage**:
```python
from visualization import plot_emissions_by_technology
fig = plot_emissions_by_technology(df_emissions, save=True)
```

### 3. Top Emitters (`plot_top_emitters`)

**Description**: Horizontal bar chart of top emitting companies.

**Output**: `top_emitters.png`

**Features**:
- Top 10 companies by total emissions (all years)
- Color gradient from light to dark red
- Value labels on bars

**Parameters**:
- `n`: Number of companies to show (default: 10)

**Usage**:
```python
from visualization import plot_top_emitters
fig = plot_top_emitters(df_company_total, n=15, save=True)
```

### 4. Company Trends (`plot_company_trends`)

**Description**: Multi-line time series showing company-level emissions evolution.

**Output**: `company_trends.png`

**Features**:
- Shows top N companies (default: 5)
- Each company as separate line
- Allows comparison of emission trajectories

**Parameters**:
- `companies`: List of specific companies (optional)
- `n_companies`: Number of top companies if companies not specified

**Usage**:
```python
from visualization import plot_company_trends

# Top 5 companies
fig = plot_company_trends(df_company_year, n_companies=5, save=True)

# Specific companies
companies = ['Company A', 'Company B', 'Company C']
fig = plot_company_trends(df_company_year, companies=companies, save=True)
```

### 5. Emissions Projections (`plot_projections`)

**Description**: Shows historical emissions + future projections with uncertainty.

**Output**: `emissions_projections.png`

**Features**:
- Historical data (solid line with markers)
- Projected data (dashed line)
- 95% confidence intervals (shaded area)
- Multiple companies in subplots

**Parameters**:
- `companies`: Companies to plot (optional)
- `n_companies`: Number of companies (default: 3)

**Usage**:
```python
from visualization import plot_projections
fig = plot_projections(df_projections, df_company_year, 
                       n_companies=3, save=True)
```

### 6. Capacity and Utilization (`plot_capacity_utilization`)

**Description**: Shows capacity vs production and utilization rates.

**Output**: `capacity_utilization.png`

**Features**:
- Top panel: Capacity vs production over time
- Bottom panel: Average utilization rate
- Gap between capacity and production visualized

**Usage**:
```python
from visualization import plot_capacity_utilization
fig = plot_capacity_utilization(df_production, save=True)
```

### 7. Technology Transition (`plot_technology_transition`)

**Description**: Visualizes technology mix evolution over time.

**Output**: `technology_transition.png`

**Features**:
- Left panel: Stacked bar chart (absolute capacity)
- Right panel: Line chart (percentage share)
- Shows shift from BF-BOF to EAF over time

**Usage**:
```python
from visualization import plot_technology_transition
fig = plot_technology_transition(df_operational, save=True)
```

### 8. Emission Factors Distribution (`plot_emission_factors_distribution`)

**Description**: Shows distribution of emission factors by technology.

**Output**: `emission_factors.png`

**Features**:
- Left panel: Box plots by technology
- Right panel: Histograms with overlap
- Identifies outliers and variability

**Usage**:
```python
from visualization import plot_emission_factors_distribution
fig = plot_emission_factors_distribution(df_emissions, save=True)
```

## Complete Plot Suite

Generate all plots at once:

```python
from visualization import create_all_plots

figures = create_all_plots(
    df_operational,
    df_production,
    df_emissions,
    df_company_year,
    df_company_total,
    df_projections=df_projections,  # Optional
    save=True
)

# Returns dictionary of figure objects
print(f"Created {len(figures)} plots")
```

## Customization

### Change Plot Style

```python
from visualization import setup_plot_style
import matplotlib.pyplot as plt

# Setup custom style
plt.style.use('seaborn-v0_8-whitegrid')  # Different style
plt.rcParams['figure.figsize'] = (14, 7)  # Larger figures
plt.rcParams['font.size'] = 12  # Larger fonts

# Then create plots
```

### Save to Custom Directory

```python
from visualization import save_figure
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
# ... create your plot ...

save_figure(fig, 'my_custom_plot.png', output_dir='/path/to/directory')
```

### Don't Save, Just Display

```python
from visualization import plot_emissions_by_year
import matplotlib.pyplot as plt

fig = plot_emissions_by_year(df_emissions, save=False)
plt.show()
```

## Output Specifications

All saved plots have:
- **Format**: PNG
- **Resolution**: 300 DPI (publication quality)
- **Size**: 12×6 inches (default, varies by plot type)
- **Location**: `output/plots/` directory

## Dependencies

Required packages (automatically installed with `requirements.txt`):
- `matplotlib>=3.7.0`
- `seaborn>=0.12.0`
- `numpy>=1.24.0`
- `pandas>=2.0.0`

## Tips for Best Results

### 1. Data Quality
Ensure your data has been properly processed:
```python
# Check for missing values
print(df_emissions.isnull().sum())

# Verify required columns exist
required_cols = ['year', 'emissions_mt', 'technology_std']
assert all(col in df_emissions.columns for col in required_cols)
```

### 2. Memory Management
For large datasets, plots may take time:
```python
# Monitor progress
import warnings
warnings.filterwarnings('ignore')  # Suppress matplotlib warnings

# Create plots one at a time if memory is limited
fig1 = plot_emissions_by_year(df_emissions, save=True)
plt.close(fig1)  # Free memory
```

### 3. Publication Quality
For papers/presentations:
```python
import matplotlib.pyplot as plt

# High DPI for presentations
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Larger fonts for readability
plt.rcParams['font.size'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14

# Then create plots
```

## Integration with Analysis Pipeline

The visualization step is integrated into `main.py`:

```
Step 1: Load data
Step 2: Create operational dataset
Step 3: Calculate production
Step 4: Calculate emissions
Step 5: Aggregate by company
Step 6: Project future emissions
Step 7: Create visualizations ← NEW!
```

Visualizations are created after all analysis is complete, ensuring all data is available for plotting.

## Troubleshooting

### Issue: Plots not appearing

**Solution**: Make sure you're not running in a non-GUI environment:
```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

### Issue: Memory errors with large datasets

**Solution**: Create plots individually and close figures:
```python
fig = plot_emissions_by_year(df_emissions, save=True)
plt.close(fig)
```

### Issue: Font rendering problems

**Solution**: Specify a specific font:
```python
plt.rcParams['font.family'] = 'DejaVu Sans'
```

### Issue: Technology column not found

**Solution**: Ensure data has been standardized:
```python
from data_loader import standardize_technology
df = standardize_technology(df)
```

## Examples

### Example 1: Custom Company Analysis

```python
from visualization import plot_company_trends, plot_projections

# Analyze specific companies
my_companies = ['China Baowu Steel', 'Ansteel Group', 'Shougang Group']

# Historical trends
fig1 = plot_company_trends(
    df_company_year, 
    companies=my_companies,
    save=True
)

# With projections
fig2 = plot_projections(
    df_projections,
    df_company_year,
    companies=my_companies,
    save=True
)
```

### Example 2: Technology Focus

```python
from visualization import (
    plot_emissions_by_technology,
    plot_technology_transition,
    plot_emission_factors_distribution
)

# Complete technology analysis
fig1 = plot_emissions_by_technology(df_emissions, save=True)
fig2 = plot_technology_transition(df_operational, save=True)
fig3 = plot_emission_factors_distribution(df_emissions, save=True)
```

### Example 3: Executive Summary

```python
from visualization import (
    plot_emissions_by_year,
    plot_top_emitters,
    plot_capacity_utilization
)

# Key metrics for presentation
fig1 = plot_emissions_by_year(df_emissions, save=True)
fig2 = plot_top_emitters(df_company_total, n=10, save=True)
fig3 = plot_capacity_utilization(df_production, save=True)
```

## Advanced: Creating Custom Plots

Use the data preparation functions and create your own plots:

```python
import matplotlib.pyplot as plt
import seaborn as sns
from visualization import setup_plot_style

# Setup
setup_plot_style()

# Custom plot
fig, ax = plt.subplots(figsize=(10, 6))

# Your custom visualization
sns.scatterplot(
    data=df_emissions,
    x='production_mt',
    y='emissions_mt',
    hue='technology_std',
    size='plant_count',
    ax=ax
)

ax.set_xlabel('Production (million tonnes)')
ax.set_ylabel('Emissions (million tonnes CO₂)')
ax.set_title('Emissions vs Production by Technology')

# Save
fig.savefig('output/plots/custom_plot.png', dpi=300, bbox_inches='tight')
```

## Summary

The visualization module provides:
- ✅ 8 comprehensive plot types
- ✅ Publication-quality output (300 DPI PNG)
- ✅ Automatic integration with analysis pipeline
- ✅ Customizable parameters
- ✅ Easy to extend with custom plots
- ✅ Professional styling with seaborn

All visualizations are designed to effectively communicate the emissions analysis results for academic papers, presentations, and reports.

