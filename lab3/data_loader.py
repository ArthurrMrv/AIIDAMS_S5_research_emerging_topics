"""
Data loading and preparation module for steel industry analysis.
Functions to load and preprocess the steel plants dataset.
"""

import pandas as pd
import numpy as np
from typing import Optional
import config


def load_steel_dataset(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Load the steel plants dataset from CSV file.
    
    Parameters
    ----------
    filepath : str, optional
        Path to the steel plants CSV file. If None, uses default from config.
        
    Returns
    -------
    pd.DataFrame
        Loaded steel plants dataset with basic preprocessing.
    """
    if filepath is None:
        filepath = config.STEEL_PLANTS_FILE
    
    print(f"Loading steel plants dataset from: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    
    print(f"Loaded {len(df)} plants")
    print(f"Columns: {df.shape[1]}")
    
    return df


def preprocess_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess date columns to handle various formats.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw steel plants dataset.
        
    Returns
    -------
    pd.DataFrame
        Dataset with cleaned date columns.
    """
    df = df.copy()
    
    # Convert date columns to datetime
    date_columns = [config.COL_START_DATE, config.COL_RETIRED_DATE, config.COL_IDLED_DATE]
    
    for col in date_columns:
        if col in df.columns:
            # Handle various date formats
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df


def extract_year_from_date(df: pd.DataFrame, date_col: str, year_col: str) -> pd.DataFrame:
    """
    Extract year from a datetime column.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset with date column.
    date_col : str
        Name of the date column.
    year_col : str
        Name for the new year column.
        
    Returns
    -------
    pd.DataFrame
        Dataset with added year column.
    """
    df = df.copy()
    df[year_col] = df[date_col].dt.year
    return df


def clean_capacity_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate capacity data.
    
    Parameters
    ----------
    df : pd.DataFrame
        Steel plants dataset.
        
    Returns
    -------
    pd.DataFrame
        Dataset with cleaned capacity values.
    """
    df = df.copy()
    
    # Convert capacity to numeric
    if config.COL_CAPACITY in df.columns:
        df[config.COL_CAPACITY] = pd.to_numeric(df[config.COL_CAPACITY], errors='coerce')
        
        # Filter out zero or negative capacities
        df = df[df[config.COL_CAPACITY] > 0]
        
        print(f"After capacity cleaning: {len(df)} plants with valid capacity")
    
    return df


def standardize_technology(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize technology names using the mapping from config.
    
    Parameters
    ----------
    df : pd.DataFrame
        Steel plants dataset.
        
    Returns
    -------
    pd.DataFrame
        Dataset with standardized technology column.
    """
    df = df.copy()
    
    if config.COL_TECHNOLOGY in df.columns:
        # Create a new standardized technology column
        df['technology_std'] = df[config.COL_TECHNOLOGY].fillna('UNKNOWN')
        
        # Apply mapping
        for original, standard in config.TECHNOLOGY_MAPPING.items():
            df.loc[df[config.COL_TECHNOLOGY].str.contains(original, case=False, na=False), 
                   'technology_std'] = standard
        
        # For any remaining unmapped technologies, set to OTHER
        mapped_values = set(config.TECHNOLOGY_MAPPING.values())
        df.loc[~df['technology_std'].isin(mapped_values), 'technology_std'] = 'OTHER'
        
        print(f"Technology distribution after standardization:")
        print(df['technology_std'].value_counts())
    
    return df


def filter_by_country(df: pd.DataFrame, country: str = config.TARGET_COUNTRY) -> pd.DataFrame:
    """
    Filter dataset to include only plants from a specific country.
    
    Parameters
    ----------
    df : pd.DataFrame
        Steel plants dataset.
    country : str
        Country name to filter by.
        
    Returns
    -------
    pd.DataFrame
        Filtered dataset with only plants from the specified country.
    """
    df_filtered = df[df[config.COL_COUNTRY] == country].copy()
    
    print(f"Filtered to {country}: {len(df_filtered)} plants")
    
    return df_filtered


def prepare_steel_data(filepath: Optional[str] = None, 
                      country: Optional[str] = None) -> pd.DataFrame:
    """
    Complete data preparation pipeline.
    
    This is the main function that orchestrates all data loading and preprocessing.
    
    Parameters
    ----------
    filepath : str, optional
        Path to steel plants CSV. If None, uses default from config.
    country : str, optional
        Country to filter by. If None, returns all countries.
        
    Returns
    -------
    pd.DataFrame
        Cleaned and prepared steel plants dataset.
    """
    print("=" * 60)
    print("STEEL DATASET PREPARATION")
    print("=" * 60)
    
    # Load data
    df = load_steel_dataset(filepath)
    
    # Preprocess dates
    df = preprocess_dates(df)
    df = extract_year_from_date(df, config.COL_START_DATE, 'start_year')
    df = extract_year_from_date(df, config.COL_RETIRED_DATE, 'retired_year')
    df = extract_year_from_date(df, config.COL_IDLED_DATE, 'idled_year')
    
    # Clean capacity data
    df = clean_capacity_data(df)
    
    # Standardize technology
    df = standardize_technology(df)
    
    # Filter by country if specified
    if country is not None:
        df = filter_by_country(df, country)
    
    print("=" * 60)
    print(f"Data preparation complete: {len(df)} plants ready for analysis")
    print("=" * 60)
    
    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate summary statistics for the dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        Steel plants dataset.
        
    Returns
    -------
    dict
        Dictionary containing summary statistics.
    """
    summary = {
        'total_plants': len(df),
        'total_capacity': df[config.COL_CAPACITY].sum() if config.COL_CAPACITY in df.columns else 0,
        'countries': df[config.COL_COUNTRY].nunique() if config.COL_COUNTRY in df.columns else 0,
        'companies': df[config.COL_OWNER].nunique() if config.COL_OWNER in df.columns else 0,
        'avg_capacity': df[config.COL_CAPACITY].mean() if config.COL_CAPACITY in df.columns else 0,
    }
    
    if 'technology_std' in df.columns:
        summary['technology_distribution'] = df['technology_std'].value_counts().to_dict()
    
    return summary


def print_data_summary(df: pd.DataFrame) -> None:
    """
    Print a formatted summary of the dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        Steel plants dataset.
    """
    summary = get_data_summary(df)
    
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)
    print(f"Total Plants: {summary['total_plants']:,}")
    print(f"Total Capacity: {summary['total_capacity']:,.0f} ttpa")
    print(f"Number of Countries: {summary['countries']}")
    print(f"Number of Companies: {summary['companies']}")
    print(f"Average Plant Capacity: {summary['avg_capacity']:,.0f} ttpa")
    
    if 'technology_distribution' in summary:
        print("\nTechnology Distribution:")
        for tech, count in summary['technology_distribution'].items():
            print(f"  {tech}: {count}")
    
    print("=" * 60)


if __name__ == "__main__":
    # Test the data loading functions
    df = prepare_steel_data()
    print_data_summary(df)
    
    # Test China-specific data
    print("\n\nChina-specific data:")
    df_china = prepare_steel_data(country=config.TARGET_COUNTRY)
    print_data_summary(df_china)

