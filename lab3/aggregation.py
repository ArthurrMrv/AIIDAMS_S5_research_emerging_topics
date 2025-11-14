"""
Company-level aggregation module.
Aggregates plant-level emissions and production at the company level.
"""

import pandas as pd
import numpy as np
from typing import Optional, List
import config


def aggregate_by_company_and_year(df_emissions: pd.DataFrame,
                                  company_col: str = config.COL_PARENT) -> pd.DataFrame:
    """
    Aggregate emissions and production by company and year.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Plant-level emissions dataset.
    company_col : str
        Column name for company identifier (Parent or Owner).
        
    Returns
    -------
    pd.DataFrame
        Company-year level aggregated data.
    """
    print("\n" + "=" * 60)
    print("AGGREGATING TO COMPANY LEVEL")
    print("=" * 60)
    
    # Use Parent if available, otherwise use Owner
    if company_col not in df_emissions.columns:
        company_col = config.COL_OWNER
    
    if company_col not in df_emissions.columns:
        raise ValueError(f"Neither Parent nor Owner column found")
    
    df = df_emissions.copy()
    
    # Fill missing company names
    df[company_col] = df[company_col].fillna('Unknown')
    df['company'] = df[company_col]
    
    # Aggregate by company and year
    agg_dict = {
        'emissions_mt': 'sum',
        'production_mt': 'sum',
        config.COL_CAPACITY: 'sum',
        'utilization_rate': 'mean',
        config.COL_PLANT_NAME: 'nunique',
    }
    
    # Add technology distribution if available
    if 'technology_std' in df.columns:
        # Count plants by technology for each company-year
        pass  # Will handle separately
    
    company_year = df.groupby(['company', 'year']).agg(agg_dict).reset_index()
    
    company_year.columns = ['company', 'year', 'total_emissions_mt', 
                           'total_production_mt', 'total_capacity_ttpa',
                           'avg_utilization_rate', 'plant_count']
    
    # Calculate emissions intensity
    company_year['emissions_intensity'] = np.where(
        company_year['total_production_mt'] > 0,
        company_year['total_emissions_mt'] * 1_000_000 / 
        (company_year['total_production_mt'] * 1_000_000),
        0
    )
    
    # Convert capacity to million tonnes
    company_year['total_capacity_mt'] = company_year['total_capacity_ttpa'] / 1000
    
    print(f"Aggregated to {company_year['company'].nunique()} companies")
    print(f"Years: {company_year['year'].min()} to {company_year['year'].max()}")
    print(f"Total records: {len(company_year)}")
    
    print("=" * 60)
    
    return company_year


def aggregate_by_company_total(df_emissions: pd.DataFrame,
                               company_col: str = config.COL_PARENT) -> pd.DataFrame:
    """
    Aggregate emissions and production by company (all years combined).
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Plant-level emissions dataset.
    company_col : str
        Column name for company identifier.
        
    Returns
    -------
    pd.DataFrame
        Company-level aggregated data (all years).
    """
    # Use Parent if available, otherwise use Owner
    if company_col not in df_emissions.columns:
        company_col = config.COL_OWNER
    
    if company_col not in df_emissions.columns:
        raise ValueError(f"Neither Parent nor Owner column found")
    
    df = df_emissions.copy()
    df[company_col] = df[company_col].fillna('Unknown')
    df['company'] = df[company_col]
    
    # Aggregate by company
    agg_dict = {
        'emissions_mt': 'sum',
        'production_mt': 'sum',
        config.COL_CAPACITY: 'sum',
        'utilization_rate': 'mean',
        config.COL_PLANT_NAME: 'nunique',
        'year': ['min', 'max', 'nunique']
    }
    
    company_total = df.groupby('company').agg(agg_dict).reset_index()
    
    # Flatten column names
    company_total.columns = ['company', 'total_emissions_mt', 'total_production_mt',
                            'total_capacity_ttpa', 'avg_utilization_rate', 'plant_count',
                            'first_year', 'last_year', 'year_count']
    
    # Calculate emissions intensity
    company_total['emissions_intensity'] = np.where(
        company_total['total_production_mt'] > 0,
        company_total['total_emissions_mt'] * 1_000_000 / 
        (company_total['total_production_mt'] * 1_000_000),
        0
    )
    
    # Convert capacity to million tonnes
    company_total['total_capacity_mt'] = company_total['total_capacity_ttpa'] / 1000
    
    # Sort by total emissions
    company_total = company_total.sort_values('total_emissions_mt', ascending=False)
    
    return company_total


def get_company_technology_mix(df_emissions: pd.DataFrame,
                               company_col: str = config.COL_PARENT) -> pd.DataFrame:
    """
    Get technology mix (capacity share) for each company.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Plant-level emissions dataset with technology column.
    company_col : str
        Column name for company identifier.
        
    Returns
    -------
    pd.DataFrame
        Company-technology mix data.
    """
    if 'technology_std' not in df_emissions.columns:
        raise ValueError("Technology column not found")
    
    # Use Parent if available, otherwise use Owner
    if company_col not in df_emissions.columns:
        company_col = config.COL_OWNER
    
    if company_col not in df_emissions.columns:
        raise ValueError(f"Neither Parent nor Owner column found")
    
    df = df_emissions.copy()
    df['company'] = df[company_col].fillna('Unknown')
    
    # Calculate capacity by company and technology
    tech_mix = df.groupby(['company', 'technology_std']).agg({
        config.COL_CAPACITY: 'sum',
        'production_mt': 'sum',
        'emissions_mt': 'sum'
    }).reset_index()
    
    # Calculate total capacity per company
    company_totals = tech_mix.groupby('company')[config.COL_CAPACITY].sum().reset_index()
    company_totals.columns = ['company', 'total_capacity']
    
    # Merge and calculate shares
    tech_mix = tech_mix.merge(company_totals, on='company')
    tech_mix['capacity_share'] = tech_mix[config.COL_CAPACITY] / tech_mix['total_capacity']
    
    return tech_mix


def get_top_emitters(df_company: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N companies by emissions.
    
    Parameters
    ----------
    df_company : pd.DataFrame
        Company-level aggregated data.
    n : int
        Number of top companies to return.
        
    Returns
    -------
    pd.DataFrame
        Top N companies by emissions.
    """
    return df_company.nlargest(n, 'total_emissions_mt')


def calculate_company_emissions_trend(df_company_year: pd.DataFrame,
                                      min_years: int = 5) -> pd.DataFrame:
    """
    Calculate emissions trend (growth rate) for each company.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year level data.
    min_years : int
        Minimum number of years required to calculate trend.
        
    Returns
    -------
    pd.DataFrame
        Company-level data with trend information.
    """
    trends = []
    
    for company in df_company_year['company'].unique():
        company_data = df_company_year[df_company_year['company'] == company].copy()
        company_data = company_data.sort_values('year')
        
        if len(company_data) < min_years:
            continue
        
        # Calculate linear trend
        years = company_data['year'].values
        emissions = company_data['total_emissions_mt'].values
        
        # Simple linear regression
        x = years - years.min()
        y = emissions
        
        if len(x) > 1:
            # Calculate slope
            slope = np.polyfit(x, y, 1)[0]
            
            # Calculate percentage change
            first_emission = company_data.iloc[0]['total_emissions_mt']
            last_emission = company_data.iloc[-1]['total_emissions_mt']
            
            if first_emission > 0:
                pct_change = ((last_emission - first_emission) / first_emission) * 100
            else:
                pct_change = 0
            
            avg_emissions = emissions.mean()
            
            trends.append({
                'company': company,
                'trend_slope': slope,
                'pct_change': pct_change,
                'avg_emissions_mt': avg_emissions,
                'first_year': years.min(),
                'last_year': years.max(),
                'n_years': len(company_data)
            })
    
    return pd.DataFrame(trends)


def save_company_aggregations(df_company_year: pd.DataFrame,
                              df_company_total: Optional[pd.DataFrame] = None,
                              filepath_year: str = config.COMPANY_EMISSIONS_FILE,
                              filepath_total: Optional[str] = None) -> None:
    """
    Save company-level aggregations to CSV.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year level data.
    df_company_total : pd.DataFrame, optional
        Company total (all years) data.
    filepath_year : str
        Path to save company-year data.
    filepath_total : str, optional
        Path to save company total data.
    """
    import os
    
    df_company_year.to_csv(filepath_year, index=False)
    print(f"Company-year emissions saved to: {filepath_year}")
    
    if df_company_total is not None:
        if filepath_total is None:
            filepath_total = os.path.join(config.OUTPUT_DIR, 'company_emissions_total.csv')
        df_company_total.to_csv(filepath_total, index=False)
        print(f"Company total emissions saved to: {filepath_total}")


def load_company_aggregations(filepath: str = config.COMPANY_EMISSIONS_FILE) -> pd.DataFrame:
    """
    Load previously saved company aggregations.
    
    Parameters
    ----------
    filepath : str
        Path to the company aggregations CSV file.
        
    Returns
    -------
    pd.DataFrame
        Company aggregations dataset.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded company aggregations: {len(df)} records")
    return df


def print_company_summary(df_company_year: pd.DataFrame,
                         df_company_total: Optional[pd.DataFrame] = None) -> None:
    """
    Print detailed company-level summary.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year level data.
    df_company_total : pd.DataFrame, optional
        Company total data.
    """
    print("\n" + "=" * 60)
    print("COMPANY-LEVEL AGGREGATION SUMMARY")
    print("=" * 60)
    
    n_companies = df_company_year['company'].nunique()
    total_emissions = df_company_year['total_emissions_mt'].sum()
    
    print(f"Number of Companies: {n_companies}")
    print(f"Total Emissions (all companies, all years): {total_emissions:,.2f} million tonnes CO2")
    
    # Top emitters
    print("\nTop 10 Companies by Total Emissions (all years):")
    if df_company_total is not None:
        top_companies = df_company_total.head(10)
    else:
        company_totals = df_company_year.groupby('company')['total_emissions_mt'].sum().sort_values(ascending=False)
        top_companies = company_totals.head(10)
        
    if isinstance(top_companies, pd.Series):
        for i, (company, emissions) in enumerate(top_companies.items(), 1):
            pct = emissions / total_emissions * 100
            print(f"  {i}. {company}: {emissions:,.2f} million tonnes CO2 ({pct:.1f}%)")
    else:
        for i, (_, row) in enumerate(top_companies.iterrows(), 1):
            pct = row['total_emissions_mt'] / total_emissions * 100
            print(f"  {i}. {row['company']}: {row['total_emissions_mt']:,.2f} million tonnes CO2 ({pct:.1f}%)")
    
    # Emissions by year (aggregated across all companies)
    print("\nTotal Emissions by Year (all companies):")
    yearly_total = df_company_year.groupby('year')['total_emissions_mt'].sum()
    for year, emissions in yearly_total.items():
        print(f"  {int(year)}: {emissions:,.2f} million tonnes CO2")
    
    print("=" * 60)


if __name__ == "__main__":
    # Test the module
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    from emissions import calculate_plant_emissions
    
    # Load China data
    df_china = prepare_steel_data(country=config.TARGET_COUNTRY)
    
    # Create operational dataset
    df_operational = create_operational_dataset(df_china)
    
    # Calculate production
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    
    # Calculate emissions
    df_emissions = calculate_plant_emissions(df_production)
    
    # Aggregate by company
    df_company_year = aggregate_by_company_and_year(df_emissions)
    df_company_total = aggregate_by_company_total(df_emissions)
    
    # Print summary
    print_company_summary(df_company_year, df_company_total)
    
    # Save to files
    save_company_aggregations(df_company_year, df_company_total)

