"""
Utilization rate and production calculation module.
Computes plant-level production based on capacity and utilization rates.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import config


def get_utilization_rate(year: int, 
                         technology: str = None,
                         country: str = config.TARGET_COUNTRY) -> float:
    """
    Get utilization rate for a specific year and technology.
    
    Parameters
    ----------
    year : int
        Year for which to get utilization rate.
    technology : str, optional
        Technology type ('BF-BOF' or 'EAF'). If None, returns overall rate.
    country : str
        Country (currently only China is supported).
        
    Returns
    -------
    float
        Utilization rate (between 0 and 1).
    """
    if country != "China":
        raise ValueError(f"Utilization rates only configured for China, got: {country}")
    
    if technology is not None and technology in config.CHINA_UTILIZATION_TECH:
        return config.CHINA_UTILIZATION_TECH[technology].get(year, 0.8)  # Default to 0.8
    else:
        return config.CHINA_UTILIZATION_OVERALL.get(year, 0.8)  # Default to 0.8


def calculate_country_utilization_rate(year: int, 
                                       country: str = config.TARGET_COUNTRY) -> Dict[str, float]:
    """
    Calculate country-level utilization rate from production and capacity data.
    
    Parameters
    ----------
    year : int
        Year for calculation.
    country : str
        Country name.
        
    Returns
    -------
    dict
        Dictionary with overall and technology-specific utilization rates.
    """
    if country != "China":
        raise ValueError(f"Data only available for China")
    
    production = config.CHINA_PRODUCTION.get(year, 0)
    capacity = config.CHINA_CAPACITY.get(year, 1)
    
    utilization_overall = production / capacity if capacity > 0 else 0
    
    result = {
        'year': year,
        'production_mt': production,
        'capacity_mt': capacity,
        'utilization_overall': utilization_overall,
    }
    
    # Add technology-specific rates
    for tech in ['BF-BOF', 'EAF']:
        result[f'utilization_{tech.replace("-", "_").lower()}'] = get_utilization_rate(
            year, tech, country
        )
    
    return result


def calculate_plant_production(df_operational: pd.DataFrame,
                               use_technology_rates: bool = True) -> pd.DataFrame:
    """
    Calculate plant-level production based on capacity and utilization rates.
    
    Production = Capacity × Utilization Rate
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset with year and capacity columns.
    use_technology_rates : bool
        If True, use technology-specific utilization rates.
        If False, use overall country utilization rate.
        
    Returns
    -------
    pd.DataFrame
        Dataset with added production column (in ttpa and million tonnes).
    """
    print("\n" + "=" * 60)
    print("CALCULATING PLANT-LEVEL PRODUCTION")
    print("=" * 60)
    
    df = df_operational.copy()
    
    # Initialize production columns
    df['utilization_rate'] = 0.0
    df['production_ttpa'] = 0.0
    
    # Calculate production for each plant-year
    for idx, row in df.iterrows():
        year = row['year']
        capacity = row[config.COL_CAPACITY]
        
        # Get appropriate utilization rate
        if use_technology_rates and 'technology_std' in df.columns:
            technology = row['technology_std']
            utilization = get_utilization_rate(year, technology)
        else:
            utilization = get_utilization_rate(year, None)
        
        # Calculate production
        production = capacity * utilization
        
        df.at[idx, 'utilization_rate'] = utilization
        df.at[idx, 'production_ttpa'] = production
    
    # Convert to million tonnes
    df['production_mt'] = df['production_ttpa'] / 1000
    
    print(f"Calculated production for {len(df)} plant-year records")
    print(f"\nProduction summary:")
    print(f"  Total production: {df['production_mt'].sum():,.1f} million tonnes")
    print(f"  Average utilization rate: {df['utilization_rate'].mean():.2%}")
    print(f"  Min utilization rate: {df['utilization_rate'].min():.2%}")
    print(f"  Max utilization rate: {df['utilization_rate'].max():.2%}")
    
    print("=" * 60)
    
    return df


def get_production_summary_by_year(df_production: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize production by year.
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Dataset with production data.
        
    Returns
    -------
    pd.DataFrame
        Summary with year, total production, and average utilization.
    """
    summary = df_production.groupby('year').agg({
        'production_mt': 'sum',
        'utilization_rate': 'mean',
        config.COL_CAPACITY: 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    summary.columns = ['year', 'total_production_mt', 'avg_utilization', 
                      'total_capacity_ttpa', 'plant_count']
    
    # Add capacity in million tonnes
    summary['total_capacity_mt'] = summary['total_capacity_ttpa'] / 1000
    
    return summary


def get_production_summary_by_technology(df_production: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize production by year and technology.
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Dataset with production data and technology column.
        
    Returns
    -------
    pd.DataFrame
        Summary with year, technology, production, and utilization.
    """
    if 'technology_std' not in df_production.columns:
        raise ValueError("Technology column not found")
    
    summary = df_production.groupby(['year', 'technology_std']).agg({
        'production_mt': 'sum',
        'utilization_rate': 'mean',
        config.COL_CAPACITY: 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    summary.columns = ['year', 'technology', 'total_production_mt', 
                      'avg_utilization', 'total_capacity_ttpa', 'plant_count']
    
    summary['total_capacity_mt'] = summary['total_capacity_ttpa'] / 1000
    
    return summary


def compare_with_reported_production(df_production: pd.DataFrame,
                                     country: str = config.TARGET_COUNTRY) -> pd.DataFrame:
    """
    Compare calculated production with reported country-level data.
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Dataset with calculated production.
    country : str
        Country name.
        
    Returns
    -------
    pd.DataFrame
        Comparison table with calculated vs reported production.
    """
    if country != "China":
        raise ValueError("Comparison only available for China")
    
    # Get calculated production by year
    calculated = get_production_summary_by_year(df_production)
    
    # Add reported production data
    calculated['reported_production_mt'] = calculated['year'].map(config.CHINA_PRODUCTION)
    calculated['production_difference_mt'] = (calculated['total_production_mt'] - 
                                              calculated['reported_production_mt'])
    calculated['production_difference_pct'] = (
        calculated['production_difference_mt'] / calculated['reported_production_mt'] * 100
    )
    
    return calculated


def save_production_data(df_production: pd.DataFrame,
                        filepath: str = config.CHINA_PRODUCTION_FILE) -> None:
    """
    Save production dataset to CSV.
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Production dataset.
    filepath : str
        Path to save the CSV file.
    """
    df_production.to_csv(filepath, index=False)
    print(f"\nProduction data saved to: {filepath}")


def load_production_data(filepath: str = config.CHINA_PRODUCTION_FILE) -> pd.DataFrame:
    """
    Load previously saved production dataset.
    
    Parameters
    ----------
    filepath : str
        Path to the production CSV file.
        
    Returns
    -------
    pd.DataFrame
        Production dataset.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded production data: {len(df)} records")
    return df


def print_production_summary(df_production: pd.DataFrame) -> None:
    """
    Print detailed production summary.
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Production dataset.
    """
    print("\n" + "=" * 60)
    print("PRODUCTION SUMMARY")
    print("=" * 60)
    
    # Overall summary
    total_production = df_production['production_mt'].sum()
    avg_utilization = df_production['utilization_rate'].mean()
    
    print(f"Total Production (all years): {total_production:,.1f} million tonnes")
    print(f"Average Utilization Rate: {avg_utilization:.2%}")
    
    # Yearly summary
    print("\nProduction by Year:")
    yearly = get_production_summary_by_year(df_production)
    for _, row in yearly.iterrows():
        print(f"  {int(row['year'])}: {row['total_production_mt']:,.1f} million tonnes "
              f"(utilization: {row['avg_utilization']:.2%})")
    
    # Technology summary (if available)
    if 'technology_std' in df_production.columns:
        print("\nProduction by Technology (all years):")
        tech_summary = df_production.groupby('technology_std')['production_mt'].sum()
        for tech, prod in tech_summary.items():
            pct = prod / total_production * 100
            print(f"  {tech}: {prod:,.1f} million tonnes ({pct:.1f}%)")
    
    # Comparison with reported data
    print("\nComparison with Reported National Production:")
    comparison = compare_with_reported_production(df_production)
    for _, row in comparison.iterrows():
        print(f"  {int(row['year'])}: "
              f"Calculated = {row['total_production_mt']:,.1f} mt, "
              f"Reported = {row['reported_production_mt']:,.1f} mt, "
              f"Difference = {row['production_difference_pct']:+.1f}%")
    
    print("=" * 60)


if __name__ == "__main__":
    # Test the module
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    
    # Load China data
    df_china = prepare_steel_data(country=config.TARGET_COUNTRY)
    
    # Create operational dataset
    df_operational = create_operational_dataset(df_china)
    
    # Calculate production
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    
    # Print summary
    print_production_summary(df_production)
    
    # Save to file
    save_production_data(df_production)

