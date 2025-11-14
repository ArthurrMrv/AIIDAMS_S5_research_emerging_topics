"""
Main script for Lab 3: Steel Industry Emissions Analysis - China Case Study

This script orchestrates the complete analysis pipeline:
1. Load and prepare steel plant data
2. Create operational plants dataset (2020-2030)
3. Calculate plant-level production using utilization rates
4. Calculate plant-level emissions using emission factors
5. Aggregate emissions at company level
6. Project company emissions into the future

Usage:
    python main.py [--skip-projection] [--projection-years 2031 2032 2033]
"""

import argparse
import sys
from datetime import datetime

# Import our modules
import config
from data_loader import prepare_steel_data, print_data_summary
from plant_operations import (
    create_operational_dataset, 
    print_operational_summary,
    save_operational_dataset
)
from utilization import (
    calculate_plant_production,
    print_production_summary,
    save_production_data
)
from emissions import (
    calculate_plant_emissions,
    print_emissions_summary,
    save_emissions_data,
    export_emissions_summary_tables
)
from aggregation import (
    aggregate_by_company_and_year,
    aggregate_by_company_total,
    print_company_summary,
    save_company_aggregations
)
from projection import (
    project_all_companies,
    print_projection_summary,
    save_projections
)


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_full_analysis(projection_years: list = None, 
                     skip_projection: bool = False,
                     use_technology_rates: bool = True,
                     projection_method: str = 'linear') -> dict:
    """
    Run the complete emissions analysis pipeline.
    
    Parameters
    ----------
    projection_years : list, optional
        Years to project emissions. If None, uses default.
    skip_projection : bool
        If True, skips the projection step.
    use_technology_rates : bool
        If True, uses technology-specific utilization rates.
    projection_method : str
        Projection method ('linear', 'exponential', 'moving_average').
        
    Returns
    -------
    dict
        Dictionary containing all analysis results.
    """
    results = {}
    
    # Start time
    start_time = datetime.now()
    
    print_header("LAB 3: STEEL INDUSTRY EMISSIONS ANALYSIS - CHINA CASE STUDY")
    print(f"Analysis started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target country: {config.TARGET_COUNTRY}")
    print(f"Analysis period: {config.START_YEAR} - {config.END_YEAR}")
    
    # ========== STEP 1: Load and prepare data ==========
    print_header("STEP 1: DATA LOADING AND PREPARATION")
    df_steel = prepare_steel_data(country=config.TARGET_COUNTRY)
    print_data_summary(df_steel)
    results['steel_data'] = df_steel
    
    # ========== STEP 2: Create operational plants dataset ==========
    print_header("STEP 2: CREATE OPERATIONAL PLANTS DATASET (2020-2030)")
    df_operational = create_operational_dataset(df_steel, years=config.ANALYSIS_YEARS)
    print_operational_summary(df_operational)
    save_operational_dataset(df_operational)
    results['operational_plants'] = df_operational
    
    # ========== STEP 3: Calculate plant-level production ==========
    print_header("STEP 3: CALCULATE PLANT-LEVEL PRODUCTION")
    print(f"Using technology-specific rates: {use_technology_rates}")
    df_production = calculate_plant_production(
        df_operational, 
        use_technology_rates=use_technology_rates
    )
    print_production_summary(df_production)
    save_production_data(df_production)
    results['production'] = df_production
    
    # ========== STEP 4: Calculate plant-level emissions ==========
    print_header("STEP 4: CALCULATE PLANT-LEVEL EMISSIONS")
    df_emissions = calculate_plant_emissions(df_production)
    print_emissions_summary(df_emissions)
    save_emissions_data(df_emissions)
    export_emissions_summary_tables(df_emissions)
    results['emissions'] = df_emissions
    
    # ========== STEP 5: Aggregate at company level ==========
    print_header("STEP 5: AGGREGATE EMISSIONS AT COMPANY LEVEL")
    df_company_year = aggregate_by_company_and_year(df_emissions)
    df_company_total = aggregate_by_company_total(df_emissions)
    print_company_summary(df_company_year, df_company_total)
    save_company_aggregations(df_company_year, df_company_total)
    results['company_year'] = df_company_year
    results['company_total'] = df_company_total
    
    # ========== STEP 6: Project future emissions ==========
    if not skip_projection:
        print_header("STEP 6: PROJECT FUTURE EMISSIONS")
        
        if projection_years is None:
            projection_years = [2031, 2032, 2033, 2034, 2035]
        
        print(f"Projecting to years: {projection_years}")
        
        df_projections = project_all_companies(
            df_company_year,
            projection_years=projection_years,
            method=projection_method,
            min_historical_years=3,
            use_bootstrap=False  # Set to True for more robust but slower analysis
        )
        
        if not df_projections.empty:
            print_projection_summary(df_projections)
            save_projections(df_projections)
            results['projections'] = df_projections
        else:
            print("Warning: No projections generated (insufficient data)")
    else:
        print_header("STEP 6: PROJECTION SKIPPED")
        print("Projection step was skipped as requested.")
    
    # ========== Summary ==========
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header("ANALYSIS COMPLETE")
    print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration:.2f} seconds")
    print(f"\nOutput files saved to: {config.OUTPUT_DIR}")
    print("\nGenerated files:")
    print(f"  1. {config.OPERATIONAL_PLANTS_FILE}")
    print(f"  2. {config.CHINA_PRODUCTION_FILE}")
    print(f"  3. {config.CHINA_EMISSIONS_FILE}")
    print(f"  4. {config.COMPANY_EMISSIONS_FILE}")
    if not skip_projection:
        print(f"  5. {config.PROJECTION_FILE}")
    
    print("\nKey Results:")
    print(f"  Total plants analyzed: {len(df_steel)}")
    print(f"  Plant-year records: {len(df_operational)}")
    print(f"  Total production: {df_production['production_mt'].sum():,.1f} million tonnes")
    print(f"  Total emissions: {df_emissions['emissions_mt'].sum():,.2f} million tonnes CO2")
    print(f"  Companies analyzed: {df_company_year['company'].nunique()}")
    
    if 'projections' in results and not results['projections'].empty:
        final_year = results['projections']['year'].max()
        final_emissions = results['projections'][
            results['projections']['year'] == final_year
        ]['projected_emissions_mt'].sum()
        print(f"  Projected emissions ({final_year}): {final_emissions:,.2f} million tonnes CO2")
    
    print("=" * 80)
    
    return results


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Steel Industry Emissions Analysis - China Case Study'
    )
    parser.add_argument(
        '--skip-projection', 
        action='store_true',
        help='Skip the emissions projection step'
    )
    parser.add_argument(
        '--projection-years',
        nargs='+',
        type=int,
        default=None,
        help='Years to project (e.g., 2031 2032 2033)'
    )
    parser.add_argument(
        '--projection-method',
        type=str,
        default='linear',
        choices=['linear', 'exponential', 'moving_average'],
        help='Projection method to use'
    )
    parser.add_argument(
        '--no-tech-rates',
        action='store_true',
        help='Do not use technology-specific utilization rates'
    )
    
    args = parser.parse_args()
    
    try:
        # Run the analysis
        results = run_full_analysis(
            projection_years=args.projection_years,
            skip_projection=args.skip_projection,
            use_technology_rates=not args.no_tech_rates,
            projection_method=args.projection_method
        )
        
        print("\n✓ Analysis completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

