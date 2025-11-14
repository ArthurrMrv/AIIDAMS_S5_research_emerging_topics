"""
Example usage script for Lab 3 modules.
Demonstrates how to use individual modules for custom analysis.
"""

# Example 1: Basic data loading
def example_load_data():
    """Example of loading and exploring the steel data."""
    from data_loader import prepare_steel_data, print_data_summary
    import config
    
    print("\n" + "="*60)
    print("EXAMPLE 1: Loading Steel Data")
    print("="*60)
    
    # Load China data
    df = prepare_steel_data(country=config.TARGET_COUNTRY)
    print_data_summary(df)
    
    return df


# Example 2: Calculate production for a specific year
def example_production_single_year():
    """Example of calculating production for a single year."""
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    import config
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Production for Year 2023")
    print("="*60)
    
    # Load and prepare data
    df = prepare_steel_data(country=config.TARGET_COUNTRY)
    
    # Get operational plants for just 2023
    df_operational = create_operational_dataset(df, years=[2023])
    
    # Calculate production
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    
    # Show results
    total_production = df_production['production_mt'].sum()
    print(f"\nTotal production in 2023: {total_production:,.1f} million tonnes")
    
    # Show top 5 producers
    top_plants = df_production.nlargest(5, 'production_mt')
    print("\nTop 5 producing plants in 2023:")
    for i, (_, row) in enumerate(top_plants.iterrows(), 1):
        print(f"  {i}. {row[config.COL_PLANT_NAME]}: {row['production_mt']:.1f} million tonnes")
    
    return df_production


# Example 3: Analyze a specific company
def example_company_analysis():
    """Example of analyzing a specific company's emissions."""
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    from emissions import calculate_plant_emissions
    import config
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Company-Specific Analysis")
    print("="*60)
    
    # Complete pipeline
    df = prepare_steel_data(country=config.TARGET_COUNTRY)
    df_operational = create_operational_dataset(df)
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    df_emissions = calculate_plant_emissions(df_production)
    
    # Pick a company (use Parent column)
    company_col = config.COL_PARENT if config.COL_PARENT in df_emissions.columns else config.COL_OWNER
    companies = df_emissions[company_col].value_counts().head(1)
    
    if len(companies) > 0:
        target_company = companies.index[0]
        print(f"\nAnalyzing company: {target_company}")
        
        # Filter to this company
        company_data = df_emissions[df_emissions[company_col] == target_company]
        
        # Aggregate by year
        yearly = company_data.groupby('year').agg({
            'production_mt': 'sum',
            'emissions_mt': 'sum',
            config.COL_PLANT_NAME: 'nunique'
        }).reset_index()
        
        print("\nYearly emissions:")
        for _, row in yearly.iterrows():
            print(f"  {int(row['year'])}: {row['emissions_mt']:.2f} million tonnes CO2 "
                  f"from {int(row[config.COL_PLANT_NAME])} plants")
        
        return company_data
    
    return None


# Example 4: Compare different projection methods
def example_projection_comparison():
    """Example of comparing different projection methods."""
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    from emissions import calculate_plant_emissions
    from aggregation import aggregate_by_company_and_year
    from projection import compare_projection_methods
    import config
    
    print("\n" + "="*60)
    print("EXAMPLE 4: Projection Method Comparison")
    print("="*60)
    
    # Complete pipeline to get company data
    df = prepare_steel_data(country=config.TARGET_COUNTRY)
    df_operational = create_operational_dataset(df)
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    df_emissions = calculate_plant_emissions(df_production)
    df_company_year = aggregate_by_company_and_year(df_emissions)
    
    # Pick a company with sufficient data
    company_counts = df_company_year.groupby('company')['year'].nunique()
    companies_with_data = company_counts[company_counts >= 5].index
    
    if len(companies_with_data) > 0:
        target_company = companies_with_data[0]
        print(f"\nComparing projection methods for: {target_company}")
        
        # Compare methods
        projection_years = [2031, 2032, 2033]
        comparison = compare_projection_methods(df_company_year, target_company, projection_years)
        
        print("\nProjected emissions by method:")
        for method in comparison['method'].unique():
            method_data = comparison[comparison['method'] == method]
            print(f"\n  {method.upper()}:")
            for _, row in method_data.iterrows():
                print(f"    {int(row['year'])}: {row['projected_emissions_mt']:.2f} million tonnes CO2")
        
        return comparison
    
    return None


# Example 5: Technology mix analysis
def example_technology_analysis():
    """Example of analyzing technology distribution."""
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    import config
    
    print("\n" + "="*60)
    print("EXAMPLE 5: Technology Mix Analysis")
    print("="*60)
    
    # Load data
    df = prepare_steel_data(country=config.TARGET_COUNTRY)
    df_operational = create_operational_dataset(df)
    
    # Analyze technology distribution by year
    print("\nCapacity by technology and year:")
    tech_summary = df_operational.groupby(['year', 'technology_std']).agg({
        config.COL_CAPACITY: 'sum',
        config.COL_PLANT_NAME: 'count'
    }).reset_index()
    
    for year in sorted(tech_summary['year'].unique()):
        year_data = tech_summary[tech_summary['year'] == year]
        total_capacity = year_data[config.COL_CAPACITY].sum()
        
        print(f"\n  {int(year)}:")
        for _, row in year_data.iterrows():
            capacity_pct = row[config.COL_CAPACITY] / total_capacity * 100
            print(f"    {row['technology_std']}: {row[config.COL_CAPACITY]/1000:.1f} million tonnes "
                  f"({capacity_pct:.1f}%) - {int(row[config.COL_PLANT_NAME])} plants")
    
    return tech_summary


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("LAB 3 USAGE EXAMPLES")
    print("="*80)
    
    try:
        # Run examples
        example_load_data()
        example_production_single_year()
        example_company_analysis()
        example_technology_analysis()
        example_projection_comparison()
        
        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

