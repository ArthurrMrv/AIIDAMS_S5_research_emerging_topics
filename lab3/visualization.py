"""
Visualization module for steel industry emissions analysis.
Creates comprehensive plots for data exploration and presentation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
import os

import config


# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def setup_plot_style():
    """Configure global plotting style."""
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9


def save_figure(fig, filename: str, output_dir: str = None):
    """
    Save figure to file.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save.
    filename : str
        Filename (with extension).
    output_dir : str, optional
        Output directory. If None, uses config.OUTPUT_DIR.
    """
    if output_dir is None:
        output_dir = os.path.join(config.OUTPUT_DIR, 'plots')
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"  Saved: {filepath}")


def plot_emissions_by_year(df_emissions: pd.DataFrame, 
                           save: bool = True) -> plt.Figure:
    """
    Plot total emissions by year.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Emissions dataset with year and emissions columns.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Aggregate by year
    yearly = df_emissions.groupby('year').agg({
        'emissions_mt': 'sum',
        'production_mt': 'sum'
    }).reset_index()
    
    # Calculate intensity
    yearly['intensity'] = (yearly['emissions_mt'] * 1e6) / (yearly['production_mt'] * 1e6)
    
    # Plot 1: Total emissions
    ax1.plot(yearly['year'], yearly['emissions_mt'], 
             marker='o', linewidth=2, markersize=8, color='#e74c3c')
    ax1.fill_between(yearly['year'], yearly['emissions_mt'], 
                     alpha=0.3, color='#e74c3c')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total Emissions (million tonnes CO₂)')
    ax1.set_title('Total Annual Emissions')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Emissions intensity
    ax2.plot(yearly['year'], yearly['intensity'], 
             marker='s', linewidth=2, markersize=8, color='#3498db')
    ax2.fill_between(yearly['year'], yearly['intensity'], 
                     alpha=0.3, color='#3498db')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Emissions Intensity (tonnes CO₂/tonne steel)')
    ax2.set_title('Emissions Intensity Over Time')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'emissions_by_year.png')
    
    return fig


def plot_emissions_by_technology(df_emissions: pd.DataFrame,
                                 save: bool = True) -> plt.Figure:
    """
    Plot emissions by technology type.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Emissions dataset with technology column.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    if 'technology_std' not in df_emissions.columns:
        print("Warning: No technology column found")
        return None
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Aggregate by year and technology
    tech_yearly = df_emissions.groupby(['year', 'technology_std']).agg({
        'emissions_mt': 'sum',
        'production_mt': 'sum'
    }).reset_index()
    
    # Plot 1: Stacked area chart
    pivot_emissions = tech_yearly.pivot(index='year', 
                                        columns='technology_std', 
                                        values='emissions_mt')
    pivot_emissions.plot(kind='area', stacked=True, ax=ax1, alpha=0.7)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Emissions (million tonnes CO₂)')
    ax1.set_title('Emissions by Technology (Stacked)')
    ax1.legend(title='Technology', loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Technology share over time
    tech_share = pivot_emissions.div(pivot_emissions.sum(axis=1), axis=0) * 100
    tech_share.plot(kind='area', stacked=True, ax=ax2, alpha=0.7)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Share of Total Emissions (%)')
    ax2.set_title('Technology Share of Emissions')
    ax2.legend(title='Technology', loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'emissions_by_technology.png')
    
    return fig


def plot_top_emitters(df_company: pd.DataFrame, 
                     n: int = 10,
                     save: bool = True) -> plt.Figure:
    """
    Plot top N emitting companies.
    
    Parameters
    ----------
    df_company : pd.DataFrame
        Company-level emissions data.
    n : int
        Number of top companies to show.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get top emitters
    top_companies = df_company.nlargest(n, 'total_emissions_mt')
    
    # Create horizontal bar chart
    colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(top_companies)))
    bars = ax.barh(range(len(top_companies)), 
                   top_companies['total_emissions_mt'],
                   color=colors)
    
    ax.set_yticks(range(len(top_companies)))
    ax.set_yticklabels(top_companies['company'])
    ax.set_xlabel('Total Emissions (million tonnes CO₂)')
    ax.set_title(f'Top {n} Emitting Companies')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, top_companies['total_emissions_mt'])):
        ax.text(value, bar.get_y() + bar.get_height()/2, 
                f'{value:.1f}', 
                va='center', ha='left', fontsize=8)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'top_emitters.png')
    
    return fig


def plot_company_trends(df_company_year: pd.DataFrame,
                       companies: Optional[List[str]] = None,
                       n_companies: int = 5,
                       save: bool = True) -> plt.Figure:
    """
    Plot emissions trends for specific companies.
    
    Parameters
    ----------
    df_company_year : pd.DataFrame
        Company-year emissions data.
    companies : list of str, optional
        Specific companies to plot. If None, plots top N.
    n_companies : int
        Number of top companies to plot if companies is None.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Select companies
    if companies is None:
        # Get top emitters
        top_emitters = df_company_year.groupby('company')['total_emissions_mt'].sum().nlargest(n_companies)
        companies = top_emitters.index.tolist()
    
    # Plot each company
    for company in companies:
        company_data = df_company_year[df_company_year['company'] == company]
        company_data = company_data.sort_values('year')
        
        ax.plot(company_data['year'], 
                company_data['total_emissions_mt'],
                marker='o', linewidth=2, label=company, alpha=0.8)
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Emissions (million tonnes CO₂)')
    ax.set_title('Company Emissions Trends')
    ax.legend(loc='best', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'company_trends.png')
    
    return fig


def plot_projections(df_projections: pd.DataFrame,
                    df_historical: pd.DataFrame,
                    companies: Optional[List[str]] = None,
                    n_companies: int = 3,
                    save: bool = True) -> plt.Figure:
    """
    Plot emissions projections with historical data and uncertainty.
    
    Parameters
    ----------
    df_projections : pd.DataFrame
        Projections with confidence intervals.
    df_historical : pd.DataFrame
        Historical company-year data.
    companies : list of str, optional
        Companies to plot. If None, plots top N.
    n_companies : int
        Number of companies if companies is None.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    if df_projections.empty:
        print("Warning: No projections to plot")
        return None
    
    # Select companies
    if companies is None:
        top_projected = df_projections.groupby('company')['projected_emissions_mt'].sum().nlargest(n_companies)
        companies = top_projected.index.tolist()
    
    n_plots = len(companies)
    fig, axes = plt.subplots(n_plots, 1, figsize=(12, 4*n_plots))
    
    if n_plots == 1:
        axes = [axes]
    
    for ax, company in zip(axes, companies):
        # Historical data
        hist_data = df_historical[df_historical['company'] == company].sort_values('year')
        proj_data = df_projections[df_projections['company'] == company].sort_values('year')
        
        # Plot historical
        ax.plot(hist_data['year'], hist_data['total_emissions_mt'],
                'o-', linewidth=2, markersize=8, label='Historical', color='#2c3e50')
        
        # Plot projection
        ax.plot(proj_data['year'], proj_data['projected_emissions_mt'],
                's--', linewidth=2, markersize=6, label='Projected', color='#e74c3c')
        
        # Confidence interval
        ax.fill_between(proj_data['year'],
                       proj_data['lower_bound_mt'],
                       proj_data['upper_bound_mt'],
                       alpha=0.2, color='#e74c3c', label='95% CI')
        
        ax.set_xlabel('Year')
        ax.set_ylabel('Emissions (million tonnes CO₂)')
        ax.set_title(f'{company} - Emissions Projection')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'emissions_projections.png')
    
    return fig


def plot_capacity_utilization(df_production: pd.DataFrame,
                              save: bool = True) -> plt.Figure:
    """
    Plot capacity and utilization trends.
    
    Parameters
    ----------
    df_production : pd.DataFrame
        Production dataset with capacity and utilization.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Aggregate by year
    yearly = df_production.groupby('year').agg({
        config.COL_CAPACITY: 'sum',
        'production_ttpa': 'sum',
        'utilization_rate': 'mean'
    }).reset_index()
    
    # Convert to million tonnes
    yearly['capacity_mt'] = yearly[config.COL_CAPACITY] / 1000
    yearly['production_mt'] = yearly['production_ttpa'] / 1000
    
    # Plot 1: Capacity and production
    ax1.plot(yearly['year'], yearly['capacity_mt'], 
             marker='o', linewidth=2, label='Capacity', color='#3498db')
    ax1.plot(yearly['year'], yearly['production_mt'], 
             marker='s', linewidth=2, label='Production', color='#2ecc71')
    ax1.fill_between(yearly['year'], yearly['capacity_mt'], 
                     yearly['production_mt'], alpha=0.2, color='#95a5a6')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Million Tonnes')
    ax1.set_title('Steel Capacity and Production')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Utilization rate
    ax2.plot(yearly['year'], yearly['utilization_rate'] * 100,
             marker='o', linewidth=2, color='#e67e22')
    ax2.fill_between(yearly['year'], yearly['utilization_rate'] * 100,
                     alpha=0.3, color='#e67e22')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Utilization Rate (%)')
    ax2.set_title('Average Capacity Utilization Rate')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 100])
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'capacity_utilization.png')
    
    return fig


def plot_technology_transition(df_operational: pd.DataFrame,
                               save: bool = True) -> plt.Figure:
    """
    Plot technology transition over time (capacity by technology).
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset with technology.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    if 'technology_std' not in df_operational.columns:
        print("Warning: No technology column found")
        return None
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Aggregate by year and technology
    tech_yearly = df_operational.groupby(['year', 'technology_std']).agg({
        config.COL_CAPACITY: 'sum'
    }).reset_index()
    
    tech_yearly['capacity_mt'] = tech_yearly[config.COL_CAPACITY] / 1000
    
    # Plot 1: Absolute capacity
    pivot_capacity = tech_yearly.pivot(index='year', 
                                       columns='technology_std', 
                                       values='capacity_mt')
    pivot_capacity.plot(kind='bar', stacked=True, ax=ax1, alpha=0.8)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Capacity (million tonnes)')
    ax1.set_title('Technology Capacity Over Time')
    ax1.legend(title='Technology', loc='upper left')
    ax1.grid(True, alpha=0.3, axis='y')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Percentage share
    tech_share = pivot_capacity.div(pivot_capacity.sum(axis=1), axis=0) * 100
    tech_share.plot(kind='line', marker='o', ax=ax2, linewidth=2)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Share of Total Capacity (%)')
    ax2.set_title('Technology Share Over Time')
    ax2.legend(title='Technology', loc='best')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'technology_transition.png')
    
    return fig


def plot_emission_factors_distribution(df_emissions: pd.DataFrame,
                                       save: bool = True) -> plt.Figure:
    """
    Plot distribution of emission factors.
    
    Parameters
    ----------
    df_emissions : pd.DataFrame
        Emissions dataset with emission factors.
    save : bool
        Whether to save the figure.
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    if 'technology_std' not in df_emissions.columns:
        print("Warning: No technology column found")
        return None
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Box plot by technology
    df_emissions.boxplot(column='emission_factor', by='technology_std', ax=ax1)
    ax1.set_xlabel('Technology')
    ax1.set_ylabel('Emission Factor (tonnes CO₂/tonne steel)')
    ax1.set_title('Emission Factors by Technology')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Plot 2: Histogram
    for tech in df_emissions['technology_std'].unique():
        tech_data = df_emissions[df_emissions['technology_std'] == tech]
        ax2.hist(tech_data['emission_factor'], bins=20, alpha=0.5, label=tech)
    
    ax2.set_xlabel('Emission Factor (tonnes CO₂/tonne steel)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Distribution of Emission Factors')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save:
        save_figure(fig, 'emission_factors.png')
    
    return fig


def create_all_plots(df_operational: pd.DataFrame,
                    df_production: pd.DataFrame,
                    df_emissions: pd.DataFrame,
                    df_company_year: pd.DataFrame,
                    df_company_total: pd.DataFrame,
                    df_projections: Optional[pd.DataFrame] = None,
                    save: bool = True) -> dict:
    """
    Create all visualization plots.
    
    Parameters
    ----------
    df_operational : pd.DataFrame
        Operational plants dataset.
    df_production : pd.DataFrame
        Production dataset.
    df_emissions : pd.DataFrame
        Emissions dataset.
    df_company_year : pd.DataFrame
        Company-year aggregations.
    df_company_total : pd.DataFrame
        Total company aggregations.
    df_projections : pd.DataFrame, optional
        Projections dataset.
    save : bool
        Whether to save figures.
        
    Returns
    -------
    dict
        Dictionary of created figures.
    """
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    
    setup_plot_style()
    figures = {}
    
    print("\n1. Emissions by year...")
    figures['emissions_year'] = plot_emissions_by_year(df_emissions, save)
    
    print("2. Emissions by technology...")
    figures['emissions_tech'] = plot_emissions_by_technology(df_emissions, save)
    
    print("3. Top emitters...")
    figures['top_emitters'] = plot_top_emitters(df_company_total, n=10, save=save)
    
    print("4. Company trends...")
    figures['company_trends'] = plot_company_trends(df_company_year, n_companies=5, save=save)
    
    print("5. Capacity and utilization...")
    figures['capacity_util'] = plot_capacity_utilization(df_production, save)
    
    print("6. Technology transition...")
    figures['tech_transition'] = plot_technology_transition(df_operational, save)
    
    print("7. Emission factors distribution...")
    figures['emission_factors'] = plot_emission_factors_distribution(df_emissions, save)
    
    if df_projections is not None and not df_projections.empty:
        print("8. Emissions projections...")
        figures['projections'] = plot_projections(df_projections, df_company_year, 
                                                  n_companies=3, save=save)
    
    print("\n" + "=" * 60)
    print(f"Created {len(figures)} visualizations")
    if save:
        plots_dir = os.path.join(config.OUTPUT_DIR, 'plots')
        print(f"Saved to: {plots_dir}")
    print("=" * 60)
    
    return figures


if __name__ == "__main__":
    # Test the visualization module
    print("Testing visualization module...")
    
    from data_loader import prepare_steel_data
    from plant_operations import create_operational_dataset
    from utilization import calculate_plant_production
    from emissions import calculate_plant_emissions
    from aggregation import aggregate_by_company_and_year, aggregate_by_company_total
    
    # Load data
    df_china = prepare_steel_data(country=config.TARGET_COUNTRY)
    df_operational = create_operational_dataset(df_china)
    df_production = calculate_plant_production(df_operational, use_technology_rates=True)
    df_emissions = calculate_plant_emissions(df_production)
    df_company_year = aggregate_by_company_and_year(df_emissions)
    df_company_total = aggregate_by_company_total(df_emissions)
    
    # Create all plots
    figures = create_all_plots(
        df_operational,
        df_production,
        df_emissions,
        df_company_year,
        df_company_total,
        save=True
    )
    
    print("\nVisualization module test complete!")

