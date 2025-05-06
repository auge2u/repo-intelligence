#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualization utilities for the Repository Intelligence Tool.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple


def set_plot_style():
    """Set consistent style for plots."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        'figure.figsize': (12, 8),
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans', 'FreeSans', 'sans-serif'],
    })


def create_tech_heatmap(
    data: pd.DataFrame, 
    output_path: str, 
    title: str = "Technology Stack Heatmap",
    figsize: Tuple[int, int] = (16, 10)
) -> str:
    """
    Create a heatmap of technology usage across repositories.
    
    Args:
        data: DataFrame containing tech stack data
        output_path: Path to save the heatmap
        title: Plot title
        figsize: Figure size as (width, height)
        
    Returns:
        Path to the saved heatmap
    """
    set_plot_style()
    
    # Create a matrix of tech usage
    tech_counts = {}
    for _, row in data.iterrows():
        for tech in row.get('tech_stack', []):
            if tech not in tech_counts:
                tech_counts[tech] = {}
            tech_counts[tech][row['name']] = 1
    
    # Convert to DataFrame
    tech_matrix = pd.DataFrame(tech_counts).fillna(0)
    
    if not tech_matrix.empty:
        plt.figure(figsize=figsize)
        sns.heatmap(tech_matrix.T, cmap="YlGnBu", cbar_kws={'label': 'Used'})
        plt.title(title)
        plt.xlabel('Repository')
        plt.ylabel('Technology')
        plt.tight_layout()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    return None


def create_language_distribution(
    data: pd.DataFrame, 
    output_path: str,
    title: str = "Programming Language Distribution",
    figsize: Tuple[int, int] = (10, 8)
) -> str:
    """
    Create a pie chart showing the distribution of programming languages.
    
    Args:
        data: DataFrame containing language data
        output_path: Path to save the chart
        title: Plot title
        figsize: Figure size as (width, height)
        
    Returns:
        Path to the saved chart
    """
    set_plot_style()
    
    # Aggregate language data across repositories
    language_totals = {}
    for _, row in data.iterrows():
        languages = row.get('languages', {})
        for lang, size in languages.items():
            if lang in language_totals:
                language_totals[lang] += size
            else:
                language_totals[lang] = size
    
    if language_totals:
        # Convert to DataFrame for plotting
        lang_df = pd.DataFrame({
            'Language': list(language_totals.keys()),
            'Size': list(language_totals.values())
        })
        
        # Sort by size and take top 10
        lang_df = lang_df.sort_values('Size', ascending=False)
        top_langs = lang_df.head(10).copy()
        
        # Add "Other" category for the rest
        if len(lang_df) > 10:
            other_size = lang_df.iloc[10:]['Size'].sum()
            other_row = pd.DataFrame({
                'Language': ['Other'],
                'Size': [other_size]
            })
            top_langs = pd.concat([top_langs, other_row], ignore_index=True)
        
        # Create pie chart
        plt.figure(figsize=figsize)
        plt.pie(
            top_langs['Size'], 
            labels=top_langs['Language'], 
            autopct='%1.1f%%',
            startangle=90,
            shadow=False
        )
        plt.axis('equal')
        plt.title(title)
        plt.tight_layout()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    return None


def create_repo_timeline(
    data: pd.DataFrame, 
    output_path: str,
    title: str = "Repository Timeline",
    figsize: Tuple[int, int] = (14, 8)
) -> str:
    """
    Create a timeline visualization of repository creation and updates.
    
    Args:
        data: DataFrame containing repository data with dates
        output_path: Path to save the timeline
        title: Plot title
        figsize: Figure size as (width, height)
        
    Returns:
        Path to the saved timeline
    """
    set_plot_style()
    
    # Convert date strings to datetime
    plot_data = data.copy()
    if 'createdAt' in plot_data.columns:
        plot_data['createdAt'] = pd.to_datetime(plot_data['createdAt'])
    if 'updatedAt' in plot_data.columns:
        plot_data['updatedAt'] = pd.to_datetime(plot_data['updatedAt'])
    
    # Sort by creation date
    plot_data = plot_data.sort_values('createdAt')
    
    # Create timeline plot
    plt.figure(figsize=figsize)
    
    # Plot creation dates
    if 'createdAt' in plot_data.columns:
        plt.scatter(
            plot_data['createdAt'], 
            range(len(plot_data)),
            marker='o',
            s=100,
            color='blue',
            label='Created'
        )
    
    # Plot update dates
    if 'updatedAt' in plot_data.columns:
        plt.scatter(
            plot_data['updatedAt'], 
            range(len(plot_data)),
            marker='x',
            s=100,
            color='red',
            label='Last Updated'
        )
    
    # Draw lines connecting creation and update dates
    if 'createdAt' in plot_data.columns and 'updatedAt' in plot_data.columns:
        for i, row in plot_data.iterrows():
            plt.plot(
                [row['createdAt'], row['updatedAt']], 
                [plot_data.index.get_loc(i), plot_data.index.get_loc(i)],
                'k-',
                alpha=0.3
            )
    
    # Set y-axis ticks to repository names
    plt.yticks(range(len(plot_data)), plot_data['name'])
    
    plt.title(title)
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def create_service_usage_chart(
    data: pd.DataFrame, 
    output_path: str,
    title: str = "External Services Usage",
    figsize: Tuple[int, int] = (10, 6)
) -> str:
    """
    Create a bar chart showing external services usage across repositories.
    
    Args:
        data: DataFrame containing services data
        output_path: Path to save the chart
        title: Plot title
        figsize: Figure size as (width, height)
        
    Returns:
        Path to the saved chart
    """
    set_plot_style()
    
    # Count usage of each service
    service_counts = {}
    for _, row in data.iterrows():
        services = row.get('services', {})
        for service, used in services.items():
            if used:
                if service in service_counts:
                    service_counts[service] += 1
                else:
                    service_counts[service] = 1
    
    if service_counts:
        # Convert to DataFrame for plotting
        service_df = pd.DataFrame({
            'Service': list(service_counts.keys()),
            'Count': list(service_counts.values())
        })
        
        # Sort by count
        service_df = service_df.sort_values('Count', ascending=False)
        
        # Create bar chart
        plt.figure(figsize=figsize)
        ax = sns.barplot(x='Service', y='Count', data=service_df)
        
        # Add count labels on top of bars
        for i, count in enumerate(service_df['Count']):
            ax.text(i, count + 0.1, str(count), ha='center')
        
        plt.title(title)
        plt.xlabel('Service')
        plt.ylabel('Number of Repositories')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    return None
