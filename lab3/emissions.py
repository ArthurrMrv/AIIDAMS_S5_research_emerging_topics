"""
Emissions calculation module for steel plants.
Calculates plant-level emissions based on production and emission factors.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import config


def get_emission_factor(technology: str, country: str = config.TARGET_COUNTRY) -> float:
    """
    Get emission factor for a specific technology and country.
    
    Emission factor is in tonnes CO2 per tonne of steel produced.
    
    Parameters
    ----------
    technology : str
        Standardized technology type.
    country : str
        Country name (currently only China is configured).
        
    Returns
    -------
    float
        Emission factor in tonnes CO2 per tonne steel.
    """
    if country != "China":
        raise ValueError(f"Emission factors only configured for China")
    
    # Get emission factor from config
    emission_factor = config.EMISSION_FACTORS_CHINA.get(technology, None)
    
    # If not found, try to find a partial match
    if emission_factor is None:
        for key, value in config.EMISSION_FACTORS_CHINA.items():
            if key in technology or technology in key:
                emission_factor = value
                break
    
    # If still not found, use UNKNOWN default
    if emission_factor is None:
        emission_factor = config.EMISSION_FACTORS_CHINA['UNKNOWN']
        print(f"Warning: Unknown technology '{technology}', using default emission factor")
    
    return emission_factor


def calculate_plant_emissions(df_production: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate plant-level emissions based on production and emission factors.
    
    Emissions = Production × Emission Factor
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Dataset with plant-level production data.
        
    Returns
    -------
    pd.DataFrame
        Dataset with added emissions columns.
    """
    print("\n" + "=" * 60)
    print("CALCULATING PLANT-LEVEL EMISSIONS")
    print("=" * 60)
    
    df = df_production.copy()
    
    # Initialize emission columns
    df['emission_factor'] = 0.0
    df['emissions_tonnes'] = 0.0
    
    # Calculate emissions for each plant-year
    for idx, row in df.iterrows():
        if 'technology_std' in df.columns:
            technology = row['technology_std']
        else:
            technology = 'UNKNOWN'
        
        production_ttpa = row['production_ttpa']
        
        # Get emission factor
        emission_factor = get_emission_factor(technology)
        
        # Calculate emissions (in tonnes CO2)
        emissions = production_ttpa * emission_factor
        
        df.at[idx, 'emission_factor'] = emission_factor
        df.at[idx, 'emissions_tonnes'] = emissions
    
    # Convert to million tonnes CO2
    df['emissions_mt'] = df['emissions_tonnes'] / 1_000_000
    
    print(f"Calculated emissions for {len(df)} plant-year records")
    print(f"\nEmissions summary:")
    print(f"  Total emissions: {df['emissions_mt'].sum():,.2f} million tonnes CO2")
    print(f"  Average emission factor: {df['emission_factor'].mean():.2f} t CO2/t steel")
    print(f"  Min emission factor: {df['emission_factor'].min():.2f} t CO2/t steel")
    print(f"  Max emission factor: {df['emission_factor'].max():.2f} t CO2/t steel")
    
    print("=" * 60)
    
    return df


def get_emissions_summary_by_year(df_emissions: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize emissions by year.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Dataset with emissions data.
        
    Returns
    -------
    pd.DataFrame
        Summary with year, total emissions, and average emission factor.
    """
    summary = df_emissions.groupby('year').agg({
        'emissions_mt': 'sum',
        'emission_factor': 'mean',
        'production_mt': 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    summary.columns = ['year', 'total_emissions_mt', 'avg_emission_factor',
                      'total_production_mt', 'plant_count']
    
    # Calculate emissions intensity (CO2 per tonne of steel)
    summary['emissions_intensity'] = (
        summary['total_emissions_mt'] * 1_000_000 / 
        (summary['total_production_mt'] * 1_000_000)
    )
    
    return summary


def get_emissions_summary_by_technology(df_emissions: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize emissions by year and technology.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Dataset with emissions data and technology column.
        
    Returns
    -------
    pd.DataFrame
        Summary with year, technology, emissions, and emission factors.
    """
    if 'technology_std' not in df_emissions.columns:
        raise ValueError("Technology column not found")
    
    summary = df_emissions.groupby(['year', 'technology_std']).agg({
        'emissions_mt': 'sum',
        'emission_factor': 'mean',
        'production_mt': 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    summary.columns = ['year', 'technology', 'total_emissions_mt', 
                      'avg_emission_factor', 'total_production_mt', 'plant_count']
    
    return summary


def get_emissions_by_company(df_emissions: pd.DataFrame,
                             company_col: str = config.COL_PARENT) -> pd.DataFrame:
    """
    Summarize emissions by company (parent organization).
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Dataset with emissions data.
    company_col : str
        Column name for company (Parent or Owner).
        
    Returns
    -------
    pd.DataFrame
        Summary with company and total emissions.
    """
    # Use Parent if available, otherwise use Owner
    if company_col not in df_emissions.columns:
        company_col = config.COL_OWNER
    
    if company_col not in df_emissions.columns:
        raise ValueError(f"Neither Parent nor Owner column found")
    
    # Fill missing company names
    df = df_emissions.copy()
    df[company_col] = df[company_col].fillna('Unknown')
    
    summary = df.groupby(company_col).agg({
        'emissions_mt': 'sum',
        'production_mt': 'sum',
        'emission_factor': 'mean',
        config.COL_PLANT_NAME: 'nunique',
        'year': 'nunique'
    }).reset_index()
    
    summary.columns = ['company', 'total_emissions_mt', 'total_production_mt',
                      'avg_emission_factor', 'plant_count', 'year_count']
    
    # Sort by emissions
    summary = summary.sort_values('total_emissions_mt', ascending=False)
    
    return summary


def calculate_emissions_intensity(df_emissions: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate emissions intensity (CO2 per unit of production).
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Dataset with emissions and production data.
        
    Returns
    -------
    pd.DataFrame
        Dataset with added emissions intensity column.
    """
    df = df_emissions.copy()
    
    # Calculate intensity (tonnes CO2 per tonne steel)
    df['emissions_intensity'] = np.where(
        df['production_ttpa'] > 0,
        df['emissions_tonnes'] / df['production_ttpa'],
        0
    )
    
    return df


def save_emissions_data(df_emissions: pd.DataFrame,
                       filepath: str = config.CHINA_EMISSIONS_FILE) -> None:
    """
    Save emissions dataset to CSV.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Emissions dataset.
    filepath : str
        Path to save the CSV file.
    """
    df_emissions.to_csv(filepath, index=False)
    print(f"\nEmissions data saved to: {filepath}")


def load_emissions_data(filepath: str = config.CHINA_EMISSIONS_FILE) -> pd.DataFrame:
    """
    Load previously saved emissions dataset.
    
    Parameters
    ----------
    filepath : str
        Path to the emissions CSV file.
        
    Returns
    -------
    pd.DataFrame
        Emissions dataset.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded emissions data: {len(df)} records")
    return df


def print_emissions_summary(df_emissions: pd.DataFrame) -> None:
    """
    Print detailed emissions summary.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Emissions dataset.
    """
    print("\n" + "=" * 60)
    print("EMISSIONS SUMMARY")
    print("=" * 60)
    
    # Overall summary
    total_emissions = df_emissions['emissions_mt'].sum()
    total_production = df_emissions['production_mt'].sum()
    avg_intensity = total_emissions * 1_000_000 / (total_production * 1_000_000)
    
    print(f"Total Emissions (all years): {total_emissions:,.2f} million tonnes CO2")
    print(f"Total Production (all years): {total_production:,.1f} million tonnes steel")
    print(f"Average Emissions Intensity: {avg_intensity:.2f} t CO2 / t steel")
    
    # Yearly summary
    print("\nEmissions by Year:")
    yearly = get_emissions_summary_by_year(df_emissions)
    for _, row in yearly.iterrows():
        print(f"  {int(row['year'])}: {row['total_emissions_mt']:,.2f} million tonnes CO2 "
              f"(intensity: {row['emissions_intensity']:.2f} t CO2/t steel)")
    
    # Technology summary (if available)
    if 'technology_std' in df_emissions.columns:
        print("\nEmissions by Technology (all years):")
        tech_summary = df_emissions.groupby('technology_std').agg({
            'emissions_mt': 'sum',
            'production_mt': 'sum',
            'emission_factor': 'mean'
        })
        for tech, row in tech_summary.iterrows():
            pct = row['emissions_mt'] / total_emissions * 100
            print(f"  {tech}: {row['emissions_mt']:,.2f} million tonnes CO2 ({pct:.1f}%) - "
                  f"EF: {row['emission_factor']:.2f} t CO2/t steel")
    
    # Top emitters
    print("\nTop 10 Companies by Total Emissions:")
    company_summary = get_emissions_by_company(df_emissions)
    for i, (_, row) in enumerate(company_summary.head(10).iterrows(), 1):
        print(f"  {i}. {row['company']}: {row['total_emissions_mt']:,.2f} million tonnes CO2 "
              f"({row['plant_count']} plants)")
    
    print("=" * 60)


def export_emissions_summary_tables(df_emissions: pd.DataFrame,
                                   output_dir: str = config.OUTPUT_DIR) -> None:
    """
    Export various emissions summary tables to CSV files.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Emissions dataset.
    output_dir : str
        Directory to save summary files.
    """
    import os
    
    # Yearly summary
    yearly = get_emissions_summary_by_year(df_emissions)
    yearly.to_csv(os.path.join(output_dir, 'emissions_by_year.csv'), index=False)
    
    # Technology summary
    if 'technology_std' in df_emissions.columns:
        tech = get_emissions_summary_by_technology(df_emissions)
        tech.to_csv(os.path.join(output_dir, 'emissions_by_technology.csv'), index=False)
    
    # Company summary
    company = get_emissions_by_company(df_emissions)
    company.to_csv(os.path.join(output_dir, 'emissions_by_company.csv'), index=False)
    
    print(f"\nEmissions summary tables exported to: {output_dir}")


if __name__ == "__main__":
    # Test the module
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    
    # Load China data
    df_china = prepare_steel_data(country=config.TARGET_COUNTRY)
    
    # Create operational dataset
    df_operational = create_operational_dataset(df_china)
    
    # Calculate production
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    
    # Calculate emissions
    df_emissions = calculate_plant_emissions(df_production)
    
    # Print summary
    print_emissions_summary(df_emissions)
    
    # Save to file
    save_emissions_data(df_emissions)
    
    # Export summary tables
    export_emissions_summary_tables(df_emissions)

