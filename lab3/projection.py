"""
Emissions projection module.
Projects company-level emissions into the future with uncertainty quantification.
Borrows ideas from uncertainty quantification methodologies.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

import config


def linear_projection(x: np.ndarray, y: np.ndarray, 
                     future_x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simple linear regression projection with confidence intervals.
    
    Parameters
    ----------
    x : np.ndarray
        Historical years (as numeric values).
    y : np.ndarray
        Historical emissions values.
    future_x : np.ndarray
        Future years to project.
        
    Returns
    -------
    tuple of (predictions, std_errors)
        Predicted values and standard errors.
    """
    # Fit linear regression
    coeffs = np.polyfit(x, y, 1)
    poly = np.poly1d(coeffs)
    
    # Predict future values
    predictions = poly(future_x)
    
    # Calculate residuals and standard error
    fitted = poly(x)
    residuals = y - fitted
    n = len(x)
    
    if n > 2:
        # Standard error of prediction
        mse = np.sum(residuals**2) / (n - 2)
        x_mean = np.mean(x)
        sxx = np.sum((x - x_mean)**2)
        
        # Standard error for each prediction
        std_errors = np.sqrt(mse * (1 + 1/n + (future_x - x_mean)**2 / sxx))
    else:
        std_errors = np.zeros_like(future_x)
    
    return predictions, std_errors


def exponential_projection(x: np.ndarray, y: np.ndarray,
                          future_x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Exponential growth/decay projection.
    
    Fits: y = a * exp(b * x)
    
    Parameters
    ----------
    x : np.ndarray
        Historical years.
    y : np.ndarray
        Historical emissions values.
    future_x : np.ndarray
        Future years to project.
        
    Returns
    -------
    tuple of (predictions, std_errors)
        Predicted values and standard errors.
    """
    # Avoid log of negative or zero values
    if np.any(y <= 0):
        # Fall back to linear
        return linear_projection(x, y, future_x)
    
    # Transform to linear: log(y) = log(a) + b*x
    log_y = np.log(y)
    coeffs = np.polyfit(x, log_y, 1)
    
    # Predict
    log_predictions = coeffs[0] * future_x + coeffs[1]
    predictions = np.exp(log_predictions)
    
    # Estimate standard errors (simplified)
    fitted_log = coeffs[0] * x + coeffs[1]
    residuals = log_y - fitted_log
    mse = np.mean(residuals**2)
    std_errors = predictions * np.sqrt(mse)  # Approximate
    
    return predictions, std_errors


def moving_average_projection(x: np.ndarray, y: np.ndarray,
                              future_x: np.ndarray,
                              window: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Moving average based projection.
    
    Uses recent trend (moving average) to project forward.
    
    Parameters
    ----------
    x : np.ndarray
        Historical years.
    y : np.ndarray
        Historical emissions values.
    future_x : np.ndarray
        Future years to project.
    window : int
        Window size for moving average.
        
    Returns
    -------
    tuple of (predictions, std_errors)
        Predicted values and standard errors.
    """
    if len(y) < window:
        # Fall back to mean
        predictions = np.full_like(future_x, np.mean(y), dtype=float)
        std_errors = np.full_like(future_x, np.std(y), dtype=float)
        return predictions, std_errors
    
    # Calculate moving average trend
    recent_values = y[-window:]
    recent_x = x[-window:]
    
    # Fit linear trend to recent data
    if len(recent_values) > 1:
        coeffs = np.polyfit(recent_x - recent_x[0], recent_values, 1)
        slope = coeffs[0]
        last_value = recent_values[-1]
        
        # Project forward
        predictions = last_value + slope * (future_x - x[-1])
        
        # Standard error based on recent volatility
        std_errors = np.full_like(future_x, np.std(recent_values), dtype=float)
    else:
        predictions = np.full_like(future_x, recent_values[-1], dtype=float)
        std_errors = np.zeros_like(future_x)
    
    return predictions, std_errors


def bootstrap_projection(x: np.ndarray, y: np.ndarray,
                         future_x: np.ndarray,
                         method: str = 'linear',
                         n_bootstrap: int = config.N_BOOTSTRAP_SAMPLES) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Bootstrap resampling for uncertainty quantification.
    
    Parameters
    ----------
    x : np.ndarray
        Historical years.
    y : np.ndarray
        Historical emissions values.
    future_x : np.ndarray
        Future years to project.
    method : str
        Projection method ('linear', 'exponential', 'moving_average').
    n_bootstrap : int
        Number of bootstrap samples.
        
    Returns
    -------
    tuple of (predictions, lower_bound, upper_bound)
        Mean predictions and confidence interval bounds.
    """
    n = len(x)
    predictions_all = []
    
    # Select projection function
    if method == 'linear':
        proj_func = linear_projection
    elif method == 'exponential':
        proj_func = exponential_projection
    elif method == 'moving_average':
        proj_func = moving_average_projection
    else:
        proj_func = linear_projection
    
    # Bootstrap resampling
    for _ in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n, size=n, replace=True)
        x_boot = x[indices]
        y_boot = y[indices]
        
        # Sort by x to maintain time ordering
        sort_idx = np.argsort(x_boot)
        x_boot = x_boot[sort_idx]
        y_boot = y_boot[sort_idx]
        
        # Project
        pred, _ = proj_func(x_boot, y_boot, future_x)
        predictions_all.append(pred)
    
    predictions_all = np.array(predictions_all)
    
    # Calculate statistics
    predictions = np.mean(predictions_all, axis=0)
    lower_bound = np.percentile(predictions_all, (1 - config.CONFIDENCE_LEVEL) / 2 * 100, axis=0)
    upper_bound = np.percentile(predictions_all, (1 + config.CONFIDENCE_LEVEL) / 2 * 100, axis=0)
    
    return predictions, lower_bound, upper_bound


def project_company_emissions(df_company_year: pd.DataFrame,
                              company: str,
                              projection_years: List[int],
                              method: str = 'linear',
                              use_bootstrap: bool = True) -> pd.DataFrame:
    """
    Project emissions for a single company.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year level emissions data.
    company : str
        Company name.
    projection_years : list of int
        Years to project (e.g., [2031, 2032, 2033]).
    method : str
        Projection method.
    use_bootstrap : bool
        Whether to use bootstrap for uncertainty quantification.
        
    Returns
    -------
    pd.DataFrame
        Projected emissions with confidence intervals.
    """
    # Get historical data for this company
    company_data = df_company_year[df_company_year['company'] == company].copy()
    company_data = company_data.sort_values('year')
    
    if len(company_data) < 2:
        # Not enough data to project
        return pd.DataFrame()
    
    # Extract historical data
    x = company_data['year'].values.astype(float)
    y = company_data['total_emissions_mt'].values
    future_x = np.array(projection_years, dtype=float)
    
    # Project
    if use_bootstrap:
        predictions, lower, upper = bootstrap_projection(x, y, future_x, method)
        std_errors = (upper - lower) / (2 * 1.96)  # Approximate std error
    else:
        if method == 'linear':
            predictions, std_errors = linear_projection(x, y, future_x)
        elif method == 'exponential':
            predictions, std_errors = exponential_projection(x, y, future_x)
        elif method == 'moving_average':
            predictions, std_errors = moving_average_projection(x, y, future_x)
        else:
            predictions, std_errors = linear_projection(x, y, future_x)
        
        # Calculate confidence intervals
        z_score = stats.norm.ppf((1 + config.CONFIDENCE_LEVEL) / 2)
        lower = predictions - z_score * std_errors
        upper = predictions + z_score * std_errors
    
    # Create results DataFrame
    results = pd.DataFrame({
        'company': company,
        'year': projection_years,
        'projected_emissions_mt': predictions,
        'lower_bound_mt': lower,
        'upper_bound_mt': upper,
        'std_error': std_errors,
        'method': method,
        'historical_years': len(company_data)
    })
    
    return results


def project_all_companies(df_company_year: pd.DataFrame,
                         projection_years: List[int] = [2031, 2032, 2033, 2034, 2035],
                         method: str = 'linear',
                         min_historical_years: int = 3,
                         use_bootstrap: bool = False) -> pd.DataFrame:
    """
    Project emissions for all companies.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year level emissions data.
    projection_years : list of int
        Years to project.
    method : str
        Projection method.
    min_historical_years : int
        Minimum years of historical data required to project.
    use_bootstrap : bool
        Whether to use bootstrap (slower but more robust).
        
    Returns
    -------
    pd.DataFrame
        Projected emissions for all companies.
    """
    print("\n" + "=" * 60)
    print("PROJECTING FUTURE EMISSIONS")
    print("=" * 60)
    print(f"Method: {method}")
    print(f"Projection years: {projection_years}")
    print(f"Use bootstrap: {use_bootstrap}")
    
    all_projections = []
    
    companies = df_company_year['company'].unique()
    
    for i, company in enumerate(companies, 1):
        # Check if enough historical data
        company_data = df_company_year[df_company_year['company'] == company]
        n_years = company_data['year'].nunique()
        
        if n_years < min_historical_years:
            continue
        
        # Project
        projection = project_company_emissions(
            df_company_year, company, projection_years, method, use_bootstrap
        )
        
        if not projection.empty:
            all_projections.append(projection)
        
        if i % 10 == 0:
            print(f"  Processed {i}/{len(companies)} companies...")
    
    if not all_projections:
        print("No projections generated (insufficient data)")
        return pd.DataFrame()
    
    # Combine all projections
    df_projections = pd.concat(all_projections, ignore_index=True)
    
    print(f"\nProjected emissions for {df_projections['company'].nunique()} companies")
    print(f"Total projection records: {len(df_projections)}")
    print("=" * 60)
    
    return df_projections


def compare_projection_methods(df_company_year: pd.DataFrame,
                               company: str,
                               projection_years: List[int]) -> pd.DataFrame:
    """
    Compare different projection methods for a single company.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year level emissions data.
    company : str
        Company name.
    projection_years : list of int
        Years to project.
        
    Returns
    -------
    pd.DataFrame
        Comparison of different methods.
    """
    methods = ['linear', 'exponential', 'moving_average']
    comparisons = []
    
    for method in methods:
        projection = project_company_emissions(
            df_company_year, company, projection_years, method, use_bootstrap=False
        )
        if not projection.empty:
            comparisons.append(projection)
    
    if not comparisons:
        return pd.DataFrame()
    
    return pd.concat(comparisons, ignore_index=True)


def save_projections(df_projections: pd.DataFrame,
                    filepath: str = config.PROJECTION_FILE) -> None:
    """
    Save projections to CSV.
    
    Parameters
    ----------
    df_projections : pd.DataFrame
        Projections dataset.
    filepath : str
        Path to save the CSV file.
    """
    df_projections.to_csv(filepath, index=False)
    print(f"\nProjections saved to: {filepath}")


def load_projections(filepath: str = config.PROJECTION_FILE) -> pd.DataFrame:
    """
    Load previously saved projections.
    
    Parameters
    ----------
    filepath : str
        Path to the projections CSV file.
        
    Returns
    -------
    pd.DataFrame
        Projections dataset.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded projections: {len(df)} records")
    return df


def print_projection_summary(df_projections: pd.DataFrame) -> None:
    """
    Print summary of projections.
    
    Parameters
    ----------
    df_projections : pd.DataFrame
        Projections dataset.
    """
    print("\n" + "=" * 60)
    print("PROJECTION SUMMARY")
    print("=" * 60)
    
    n_companies = df_projections['company'].nunique()
    years = sorted(df_projections['year'].unique())
    
    print(f"Companies projected: {n_companies}")
    print(f"Projection years: {years}")
    
    # Total projected emissions by year
    print("\nTotal Projected Emissions (all companies):")
    yearly = df_projections.groupby('year').agg({
        'projected_emissions_mt': 'sum',
        'lower_bound_mt': 'sum',
        'upper_bound_mt': 'sum'
    })
    
    for year, row in yearly.iterrows():
        print(f"  {int(year)}: {row['projected_emissions_mt']:,.2f} million tonnes CO2 "
              f"(95% CI: [{row['lower_bound_mt']:,.2f}, {row['upper_bound_mt']:,.2f}])")
    
    # Top projected emitters (final year)
    final_year = max(years)
    print(f"\nTop 10 Projected Emitters in {final_year}:")
    final_year_data = df_projections[df_projections['year'] == final_year].sort_values(
        'projected_emissions_mt', ascending=False
    ).head(10)
    
    for i, (_, row) in enumerate(final_year_data.iterrows(), 1):
        print(f"  {i}. {row['company']}: {row['projected_emissions_mt']:,.2f} million tonnes CO2")
    
    print("=" * 60)


if __name__ == "__main__":
    # Test the module
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    from emissions import calculate_plant_emissions
    from aggregation import aggregate_by_company_and_year
    
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
    
    # Project emissions
    projection_years = [2031, 2032, 2033, 2034, 2035]
    df_projections = project_all_companies(
        df_company_year, 
        projection_years=projection_years,
        method='linear',
        use_bootstrap=False
    )
    
    # Print summary
    print_projection_summary(df_projections)
    
    # Save to file
    save_projections(df_projections)

