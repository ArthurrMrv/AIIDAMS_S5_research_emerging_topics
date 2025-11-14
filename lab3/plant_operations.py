"""
Plant operations module for determining operational status across years.
Identifies which plants are operational in each year from 2020-2030.
"""

import pandas as pd
import numpy as np
from typing import List
import config


def determine_end_year(row: pd.Series) -> float:
    """
    Determine the end year for a plant based on retired date and idled date.
    If no end date is available, assume the plant is still operating (return NaN).
    
    Parameters
    ----------
    row : pd.Series
        Row from the steel plants dataset.
        
    Returns
    -------
    float
        End year of operation, or NaN if still operating.
    """
    retired_year = row.get('retired_year', np.nan)
    idled_year = row.get('idled_year', np.nan)
    
    # If both are NaN, plant is still operating
    if pd.isna(retired_year) and pd.isna(idled_year):
        return np.nan
    
    # If only one is available, use it
    if pd.isna(retired_year):
        return idled_year
    if pd.isna(idled_year):
        return retired_year
    
    # If both are available, use the earlier one
    return min(retired_year, idled_year)


def is_plant_operational(row: pd.Series, year: int) -> bool:
    """
    Check if a plant is operational in a given year.
    
    A plant is operational if:
    - It started on or before the given year
    - It has not been retired or idled before the given year (or no end date)
    
    Parameters
    ----------
    row : pd.Series
        Row from the steel plants dataset with start_year and end_year.
    year : int
        Year to check operational status.
        
    Returns
    -------
    bool
        True if plant is operational in the given year, False otherwise.
    """
    start_year = row.get('start_year', np.nan)
    end_year = row.get('end_year', np.nan)
    
    # If no start year, we can't determine operational status
    if pd.isna(start_year):
        return False
    
    # Plant must have started on or before the year
    if start_year > year:
        return False
    
    # If no end year (still operating), plant is operational
    if pd.isna(end_year):
        return True
    
    # Plant must not have ended before the year
    return end_year > year


def create_operational_dataset(df: pd.DataFrame, 
                               years: List[int] = config.ANALYSIS_YEARS) -> pd.DataFrame:
    """
    Create a dataset of operational plants for each year in the analysis period.
    
    This expands the dataset so each plant-year combination is a separate row,
    but only for years when the plant is operational.
    
    Parameters
    ----------
    df : pd.DataFrame
        Prepared steel plants dataset.
    years : list of int
        Years to analyze (default from config).
        
    Returns
    -------
    pd.DataFrame
        Dataset with one row per plant-year combination (operational only).
    """
    print("\n" + "=" * 60)
    print("CREATING OPERATIONAL PLANTS DATASET")
    print("=" * 60)
    
    # Add end_year column
    df = df.copy()
    df['end_year'] = df.apply(determine_end_year, axis=1)
    
    # Create list to store operational records
    operational_records = []
    
    # For each plant, determine which years it's operational
    for idx, row in df.iterrows():
        for year in years:
            if is_plant_operational(row, year):
                # Create a record for this plant-year
                record = row.to_dict()
                record['year'] = year
                operational_records.append(record)
    
    # Create DataFrame from records
    df_operational = pd.DataFrame(operational_records)
    
    print(f"Created {len(df_operational)} plant-year operational records")
    print(f"Years covered: {df_operational['year'].min()} to {df_operational['year'].max()}")
    print(f"Unique plants: {df_operational[config.COL_PLANT_NAME].nunique()}")
    
    # Show operational count by year
    print("\nOperational plants by year:")
    year_counts = df_operational.groupby('year').size()
    for year, count in year_counts.items():
        print(f"  {year}: {count} plants")
    
    print("=" * 60)
    
    return df_operational


def get_operational_capacity_by_year(df_operational: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total operational capacity by year.
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset (from create_operational_dataset).
        
    Returns
    -------
    pd.DataFrame
        Summary with year and total capacity.
    """
    if config.COL_CAPACITY not in df_operational.columns:
        raise ValueError(f"Capacity column '{config.COL_CAPACITY}' not found")
    
    capacity_by_year = df_operational.groupby('year').agg({
        config.COL_CAPACITY: 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    capacity_by_year.columns = ['year', 'total_capacity_ttpa', 'plant_count']
    
    # Convert ttpa to million tonnes
    capacity_by_year['total_capacity_mt'] = capacity_by_year['total_capacity_ttpa'] / 1000
    
    return capacity_by_year


def get_operational_capacity_by_technology(df_operational: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate operational capacity by year and technology.
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset.
        
    Returns
    -------
    pd.DataFrame
        Summary with year, technology, and capacity.
    """
    if 'technology_std' not in df_operational.columns:
        raise ValueError("Standardized technology column not found")
    
    capacity_by_tech = df_operational.groupby(['year', 'technology_std']).agg({
        config.COL_CAPACITY: 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    capacity_by_tech.columns = ['year', 'technology', 'total_capacity_ttpa', 'plant_count']
    
    # Convert ttpa to million tonnes
    capacity_by_tech['total_capacity_mt'] = capacity_by_tech['total_capacity_ttpa'] / 1000
    
    return capacity_by_tech


def save_operational_dataset(df_operational: pd.DataFrame, 
                             filepath: str = config.OPERATIONAL_PLANTS_FILE) -> None:
    """
    Save operational plants dataset to CSV.
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset.
    filepath : str
        Path to save the CSV file.
    """
    df_operational.to_csv(filepath, index=False)
    print(f"\nOperational plants dataset saved to: {filepath}")


def load_operational_dataset(filepath: str = config.OPERATIONAL_PLANTS_FILE) -> pd.DataFrame:
    """
    Load previously saved operational plants dataset.
    
    Parameters
    ----------
    filepath : str
        Path to the operational plants CSV file.
        
    Returns
    -------
    pd.DataFrame
        Operational plants dataset.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded operational plants dataset: {len(df)} records")
    return df


def print_operational_summary(df_operational: pd.DataFrame) -> None:
    """
    Print a summary of the operational plants dataset.
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset.
    """
    print("\n" + "=" * 60)
    print("OPERATIONAL PLANTS SUMMARY")
    print("=" * 60)
    
    # Overall statistics
    total_records = len(df_operational)
    unique_plants = df_operational[config.COL_PLANT_NAME].nunique()
    years = sorted(df_operational['year'].unique())
    
    print(f"Total plant-year records: {total_records:,}")
    print(f"Unique plants: {unique_plants:,}")
    print(f"Years covered: {min(years)} - {max(years)}")
    
    # Capacity summary
    capacity_by_year = get_operational_capacity_by_year(df_operational)
    print("\nTotal Operational Capacity by Year:")
    for _, row in capacity_by_year.iterrows():
        print(f"  {int(row['year'])}: {row['total_capacity_mt']:,.1f} million tonnes "
              f"({int(row['plant_count'])} plants)")
    
    # Technology summary
    if 'technology_std' in df_operational.columns:
        print("\nCapacity by Technology (latest year):")
        latest_year = df_operational['year'].max()
        tech_summary = df_operational[df_operational['year'] == latest_year].groupby(
            'technology_std')[config.COL_CAPACITY].sum() / 1000
        for tech, capacity in tech_summary.items():
            print(f"  {tech}: {capacity:,.1f} million tonnes")
    
    print("=" * 60)


if __name__ == "__main__":
    # Test the module
    from data_loader import prepare_steel_data
    
    # Load and prepare China data
    df_china = prepare_steel_data(country=config.TARGET_COUNTRY)
    
    # Create operational dataset
    df_operational = create_operational_dataset(df_china)
    
    # Print summary
    print_operational_summary(df_operational)
    
    # Save to file
    save_operational_dataset(df_operational)

