#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Repository analysis module for the Repository Intelligence Tool.

This module analyzes extracted repository data and generates insights.
"""

import os
import json
import re
import pandas as pd
from typing import Dict, List, Any, Optional, Set
from collections import Counter

from src.utils.config import parse_args, load_config, create_output_dirs
from src.utils.visualization import (
    create_tech_heatmap,
    create_language_distribution,
    create_repo_timeline,
    create_service_usage_chart
)


def load_repo_data(data_dir: str, org: str, repo_name: str) -> Dict[str, Any]:
    """
    Load repository data from JSON file.
    
    Args:
        data_dir: Data directory
        org: Organization name
        repo_name: Repository name
        
    Returns:
        Repository data dictionary
    """
    repo_data_path = os.path.join(data_dir, 'raw', org, repo_name, 'repo_data.json')
    try:
        with open(repo_data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data for {org}/{repo_name}: {e}")
        return {}


def detect_tech_stack(repo_data: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """
    Detect technology stack from repository data.
    
    Args:
        repo_data: Repository data dictionary
        config: Configuration dictionary
        
    Returns:
        List of detected technologies
    """
    tech_stack = set()
    
    # Extract from languages
    if 'languages' in repo_data and repo_data['languages']:
        for lang in repo_data['languages'].keys():
            tech_stack.add(lang.lower())
    
    # Extract from README and techbragging
    content = repo_data.get('readme', '') + ' ' + repo_data.get('techbragging', '')
    content = content.lower()
    
    # Look for keywords
    keywords = config['analysis']['tech_stack']['keywords']
    for keyword in keywords:
        if re.search(r'\\b' + re.escape(keyword.lower()) + r'\\b', content):
            tech_stack.add(keyword.lower())
    
    # Detect frameworks from content
    frameworks = {
        'react': ['react', 'jsx', 'react-dom', 'react native', 'nextjs', 'next.js'],
        'vue': ['vue', 'vuejs', 'vue.js', 'nuxt'],
        'angular': ['angular', 'angularjs', 'ng-'],
        'django': ['django', 'djangorestframework'],
        'flask': ['flask', 'flask-'],
        'fastapi': ['fastapi', 'fast-api'],
        'express': ['express', 'expressjs', 'express.js'],
        'spring': ['spring boot', 'spring framework'],
        'aws': ['aws', 'amazon web services', 's3', 'ec2', 'lambda', 'dynamodb'],
        'azure': ['azure', 'microsoft azure'],
        'gcp': ['gcp', 'google cloud', 'google cloud platform'],
        'kubernetes': ['kubernetes', 'k8s', 'kubectl'],
        'docker': ['docker', 'containerization', 'containerised'],
        'terraform': ['terraform', 'terragrunt'],
        'mongodb': ['mongodb', 'mongo'],
        'postgresql': ['postgresql', 'postgres'],
        'mysql': ['mysql'],
        'redis': ['redis'],
        'graphql': ['graphql', 'apollo'],
        'tailwind': ['tailwind', 'tailwindcss', 'tailwind css'],
        'bootstrap': ['bootstrap css', 'bootstrap framework'],
        'webpack': ['webpack'],
        'vite': ['vite'],
        'jest': ['jest', 'jest testing'],
        'cypress': ['cypress', 'cypress.io'],
        'github actions': ['github actions', 'github workflow'],
    }
    
    for tech, keywords in frameworks.items():
        for keyword in keywords:
            if keyword in content:
                tech_stack.add(tech)
                break
    
    return list(tech_stack)


def estimate_project_maturity(repo_data: Dict[str, Any]) -> str:
    """
    Estimate project maturity based on available signals.
    
    Args:
        repo_data: Repository data dictionary
        
    Returns:
        Maturity level (Alpha, Beta, Production-Ready, Legacy)
    """
    # Default maturity level
    maturity = "Unknown"
    
    # Get config files
    config_files = repo_data.get('config_files', [])
    config_file_paths = [f.get('path', '').lower() for f in config_files]
    
    # Check for deployment configurations
    deploy_files = [f for f in config_file_paths if 'deploy' in f or 'production' in f 
                  or 'kubernetes' in f or 'k8s' in f or 'cloudflare' in f]
    
    # Check for testing
    test_files = [f for f in config_file_paths if 'test' in f or 'jest' in f 
                or 'cypress' in f or 'spec' in f]
    
    # Check for CI/CD
    cicd_files = [f for f in config_file_paths if '.github/workflows' in f or 'gitlab-ci' in f 
                or 'jenkins' in f or 'circleci' in f or 'travis' in f]
    
    # Check README for maturity indicators
    readme = repo_data.get('readme', '').lower()
    
    has_contributing = 'contributing' in readme or 'CONTRIBUTING.md' in config_file_paths
    has_changelog = 'changelog' in readme or 'CHANGELOG.md' in config_file_paths
    has_version = bool(re.search(r'version \d+\.\d+', readme))
    
    # Check for services
    services = repo_data.get('services', {})
    has_monitoring = services.get('sentry', False)
    has_security = services.get('snyk', False)
    
    # Determine maturity level
    if deploy_files and test_files and cicd_files and has_version:
        if has_contributing and has_changelog and has_monitoring and has_security:
            maturity = "Production-Ready"
        elif deploy_files:
            maturity = "Beta"
        else:
            maturity = "Alpha"
    elif not deploy_files and not test_files and 'archived' in readme:
        maturity = "Legacy"
    elif deploy_files:
        maturity = "Beta"
    else:
        maturity = "Alpha"
            
    return maturity


def analyze_repositories(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Analyze repository data and generate a DataFrame with insights.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        DataFrame containing repository analysis
    """
    # Paths
    data_dir = config['output']['data_dir']
    processed_dir = os.path.join(data_dir, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    all_repos = []
    
    # Process each organization
    for org in config['organizations']:
        print(f"\nAnalyzing repositories for organization: {org}")
        
        # Get repository list
        org_repos_path = os.path.join(data_dir, 'raw', org, 'repos.json')
        try:
            with open(org_repos_path, 'r') as f:
                repos = json.load(f)
        except Exception as e:
            print(f"Error loading repositories for {org}: {e}")
            continue
        
        # Analyze each repository
        for repo_info in repos:
            repo_name = repo_info['name']
            print(f"  Analyzing {org}/{repo_name}")
            
            # Load repository data
            repo_data = load_repo_data(data_dir, org, repo_name)
            if not repo_data:
                continue
            
            # Extract base info
            repo_analysis = {
                'org': org,
                'name': repo_name,
                'description': repo_data.get('metadata', {}).get('description', ''),
                'url': repo_info.get('url', ''),
                'createdAt': repo_info.get('createdAt', ''),
                'updatedAt': repo_info.get('updatedAt', ''),
                'homepage': repo_data.get('metadata', {}).get('homepageUrl', ''),
            }
            
            # Detect tech stack
            tech_stack = detect_tech_stack(repo_data, config)
            repo_analysis['tech_stack'] = tech_stack
            
            # Get languages
            repo_analysis['languages'] = repo_data.get('languages', {})
            
            # Detect services
            repo_analysis['services'] = repo_data.get('services', {})
            
            # Estimate maturity
            repo_analysis['maturity'] = estimate_project_maturity(repo_data)
            
            # Extract summary
            readme = repo_data.get('readme', '')
            summary = ""
            if readme:
                # Try to get the first paragraph
                paragraphs = readme.split('\n\n')
                if paragraphs:
                    # Skip heading if it exists
                    first_paragraph = paragraphs[0]
                    if first_paragraph.startswith('#'):
                        if len(paragraphs) > 1:
                            first_paragraph = paragraphs[1]
                        else:
                            first_paragraph = ""
                    
                    # Clean up markdown
                    summary = re.sub(r'[#*`_]+', '', first_paragraph).strip()
                    
                    # Truncate if too long
                    if len(summary) > 200:
                        summary = summary[:197] + "..."
            
            repo_analysis['summary'] = summary
            
            # Add to repos list
            all_repos.append(repo_analysis)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_repos)
    
    # Save to CSV
    df.to_csv(os.path.join(processed_dir, 'repositories.csv'), index=False)
    
    # Save to JSON
    with open(os.path.join(processed_dir, 'repositories.json'), 'w') as f:
        json.dump(all_repos, f, indent=2)
    
    return df


def generate_visualizations(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Generate visualizations based on repository analysis.
    
    Args:
        df: DataFrame containing repository analysis
        config: Configuration dictionary
    """
    visuals_dir = config['output']['visuals_dir']
    os.makedirs(visuals_dir, exist_ok=True)
    
    print("\nGenerating visualizations...")
    
    # Create technology heatmap
    tech_heatmap_path = os.path.join(visuals_dir, 'tech_heatmap.png')
    create_tech_heatmap(df, tech_heatmap_path, "Technology Stack Across Repositories")
    print(f"  Technology heatmap saved to {tech_heatmap_path}")
    
    # Create language distribution chart
    lang_dist_path = os.path.join(visuals_dir, 'language_distribution.png')
    create_language_distribution(df, lang_dist_path, "Programming Language Distribution")
    print(f"  Language distribution chart saved to {lang_dist_path}")
    
    # Create repository timeline
    timeline_path = os.path.join(visuals_dir, 'repo_timeline.png')
    create_repo_timeline(df, timeline_path, "Repository Timeline")
    print(f"  Repository timeline saved to {timeline_path}")
    
    # Create service usage chart
    service_path = os.path.join(visuals_dir, 'service_usage.png')
    create_service_usage_chart(df, service_path, "External Services Usage")
    print(f"  Service usage chart saved to {service_path}")


def main():
    """Main entry point for the repository analysis module."""
    args = parse_args()
    config = load_config(args.config)
    
    print("Starting repository analysis...")
    create_output_dirs(config)
    
    # Analyze repositories
    df = analyze_repositories(config)
    
    # Generate visualizations
    generate_visualizations(df, config)
    
    print("\nRepository analysis complete!")


if __name__ == "__main__":
    main()
