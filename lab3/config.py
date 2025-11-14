"""
Configuration file for Lab 3: Steel Industry Emissions Analysis
Contains constants, parameters, and data sources for the analysis.
"""

import os

# ==================== PATHS ====================
# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "lab1", "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Input data files
STEEL_PLANTS_FILE = os.path.join(DATA_DIR, "operating_plants.csv")

# Output data files
OPERATIONAL_PLANTS_FILE = os.path.join(OUTPUT_DIR, "operational_plants_2020_2030.csv")
CHINA_PRODUCTION_FILE = os.path.join(OUTPUT_DIR, "china_plant_production.csv")
CHINA_EMISSIONS_FILE = os.path.join(OUTPUT_DIR, "china_plant_emissions.csv")
COMPANY_EMISSIONS_FILE = os.path.join(OUTPUT_DIR, "company_emissions.csv")
PROJECTION_FILE = os.path.join(OUTPUT_DIR, "emissions_projection.csv")

# ==================== ANALYSIS PARAMETERS ====================
# Years to analyze
START_YEAR = 2020
END_YEAR = 2030
ANALYSIS_YEARS = list(range(START_YEAR, END_YEAR + 1))

# Target country for case study
TARGET_COUNTRY = "China"

# ==================== CHINA STEEL DATA ====================
# China's steel production data (million tonnes per year)
# Source: World Steel Association
CHINA_PRODUCTION = {
    2020: 1053.0,
    2021: 1032.8,
    2022: 1013.0,
    2023: 1019.0,
    2024: 1025.0,  # Estimate
    2025: 1030.0,  # Projection
    2026: 1035.0,  # Projection
    2027: 1040.0,  # Projection
    2028: 1045.0,  # Projection
    2029: 1050.0,  # Projection
    2030: 1055.0,  # Projection
}

# China's steel capacity data (million tonnes per year)
# Source: OECD Steel Capacity Report
CHINA_CAPACITY = {
    2020: 1080.0,
    2021: 1100.0,
    2022: 1120.0,
    2023: 1140.0,
    2024: 1160.0,  # Estimate
    2025: 1180.0,  # Projection
    2026: 1200.0,  # Projection
    2027: 1220.0,  # Projection
    2028: 1240.0,  # Projection
    2029: 1260.0,  # Projection
    2030: 1280.0,  # Projection
}

# ==================== UTILIZATION RATES ====================
# Technology-specific utilization rates for China
# More granular approach: different rates for BF-BOF and EAF
CHINA_UTILIZATION_TECH = {
    "BF-BOF": {  # Blast Furnace - Basic Oxygen Furnace (high emissions)
        2020: 0.85,
        2021: 0.84,
        2022: 0.83,
        2023: 0.82,
        2024: 0.81,
        2025: 0.80,
        2026: 0.79,
        2027: 0.78,
        2028: 0.77,
        2029: 0.76,
        2030: 0.75,
    },
    "EAF": {  # Electric Arc Furnace (lower emissions)
        2020: 0.75,
        2021: 0.76,
        2022: 0.77,
        2023: 0.78,
        2024: 0.79,
        2025: 0.80,
        2026: 0.81,
        2027: 0.82,
        2028: 0.83,
        2029: 0.84,
        2030: 0.85,
    },
}

# Overall utilization rate (fallback if technology not specified)
CHINA_UTILIZATION_OVERALL = {
    year: CHINA_PRODUCTION[year] / CHINA_CAPACITY[year]
    for year in ANALYSIS_YEARS
}

# ==================== EMISSION FACTORS ====================
# Emission factors for China by technology (tonnes CO2 per tonne of steel)
# Source: Hasanbeigi et al. reports on steel industry emissions
# These are typical values for Chinese steel production

EMISSION_FACTORS_CHINA = {
    # Primary steelmaking (iron ore based)
    "BF": 2.1,      # Blast Furnace
    "BOF": 1.9,     # Basic Oxygen Furnace
    "BF-BOF": 2.0,  # Combined BF-BOF route
    
    # Secondary steelmaking (scrap based)
    "EAF": 0.5,     # Electric Arc Furnace (with China's grid mix)
    
    # Other technologies
    "DRI": 1.5,     # Direct Reduced Iron
    "OHF": 1.8,     # Open Hearth Furnace
    
    # Default for unspecified
    "OTHER": 1.5,
    "UNKNOWN": 1.8,
}

# ==================== TECHNOLOGY MAPPING ====================
# Map technology strings from dataset to standardized categories
TECHNOLOGY_MAPPING = {
    "BF": "BF-BOF",
    "BOF": "BF-BOF",
    "BF; BOF": "BF-BOF",
    "BF-BOF": "BF-BOF",
    "EAF": "EAF",
    "DRI": "EAF",  # DRI often used with EAF
    "EAF; DRI": "EAF",
    "OHF": "BF-BOF",  # Treat OHF similar to BOF
    "Steel other/unspecified": "OTHER",
}

# ==================== PROJECTION PARAMETERS ====================
# Parameters for emissions projection
PROJECTION_METHODS = [
    "linear",           # Simple linear regression
    "exponential",      # Exponential growth/decay
    "moving_average",   # Moving average trend
]

# Uncertainty quantification parameters
CONFIDENCE_LEVEL = 0.95  # 95% confidence interval
N_BOOTSTRAP_SAMPLES = 1000  # Number of bootstrap samples for uncertainty

# ==================== DATA COLUMN NAMES ====================
# Column names in the steel plants dataset
COL_PLANT_NAME = "Plant name (English)_x"
COL_COUNTRY = "Country/Area_x"
COL_START_DATE = "Start date_x"
COL_RETIRED_DATE = "Retired date"
COL_IDLED_DATE = "Idled date"
COL_TECHNOLOGY = "Main production equipment"
COL_CAPACITY = "Nominal crude steel capacity (ttpa)"
COL_OWNER = "Owner"
COL_PARENT = "Parent"
COL_LATITUDE = "latitude"
COL_LONGITUDE = "longitude"
COL_STATUS = "Status"

# ==================== OUTPUT SETTINGS ====================
# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Display settings
DISPLAY_DECIMALS = 2
LARGE_NUMBER_FORMAT = "{:,.0f}"  # Format for large numbers with commas

# ==================== VISUALIZATION SETTINGS ====================
# Plot settings for future use
PLOT_STYLE = "seaborn-v0_8-darkgrid"
FIGURE_SIZE = (12, 6)
COLOR_PALETTE = "viridis"

