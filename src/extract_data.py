#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data extraction module for the Repository Intelligence Tool.

This module extracts data from GitHub repositories and saves it for analysis.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from tqdm import tqdm

from src.utils.config import parse_args, load_config, create_output_dirs
from src.utils.github import (
    list_repositories, 
    get_repository_metadata, 
    get_repository_languages,
    get_repository_contributors,
    get_file_content,
    find_config_files,
    detect_services
)


def extract_repo_data(org: str, repo_name: str, config: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    """
    Extract data for a single repository.
    
    Args:
        org: Organization name
        repo_name: Repository name
        config: Configuration dictionary
        output_dir: Directory to save repository data
        
    Returns:
        Dictionary containing repository data
    """
    repo_data = {
        'name': repo_name,
        'organization': org,
    }
    
    # Get repository metadata
    try:
        metadata = get_repository_metadata(org, repo_name)
        repo_data['metadata'] = metadata
    except Exception as e:
        print(f"Error getting metadata for {org}/{repo_name}: {e}")
        repo_data['metadata'] = {}
    
    # Get repository languages
    try:
        languages = get_repository_languages(org, repo_name)
        repo_data['languages'] = languages
    except Exception as e:
        print(f"Error getting languages for {org}/{repo_name}: {e}")
        repo_data['languages'] = {}
    
    # Get repository contributors
    try:
        contributors = get_repository_contributors(org, repo_name, config)
        repo_data['contributors'] = contributors
    except Exception as e:
        print(f"Error getting contributors for {org}/{repo_name}: {e}")
        repo_data['contributors'] = []
    
    # Get README file
    try:
        readme_content = get_file_content(org, repo_name, 'README.md')
        if not readme_content:
            readme_content = get_file_content(org, repo_name, 'readme.md')
        if not readme_content:
            readme_content = get_file_content(org, repo_name, 'Readme.md')
        repo_data['readme'] = readme_content or ""
    except Exception as e:
        print(f"Error getting README for {org}/{repo_name}: {e}")
        repo_data['readme'] = ""
    
    # Get techbragging.md file if it exists
    try:
        techbragging_content = get_file_content(org, repo_name, 'techbragging.md')
        if not techbragging_content:
            techbragging_content = get_file_content(org, repo_name, 'TECHBRAGGING.md')
        repo_data['techbragging'] = techbragging_content or ""
    except Exception as e:
        print(f"Error getting techbragging.md for {org}/{repo_name}: {e}")
        repo_data['techbragging'] = ""
    
    # Find configuration files
    try:
        config_files = find_config_files(org, repo_name)
        repo_data['config_files'] = config_files
        
        # Detect services
        service_keywords = config['analysis']['services']['keywords']
        services = detect_services(org, repo_name, config_files, service_keywords)
        repo_data['services'] = services
    except Exception as e:
        print(f"Error finding config files for {org}/{repo_name}: {e}")
        repo_data['config_files'] = []
        repo_data['services'] = {}
    
    # Save repository data to output directory
    repo_output_dir = os.path.join(output_dir, org, repo_name)
    os.makedirs(repo_output_dir, exist_ok=True)
    
    with open(os.path.join(repo_output_dir, 'repo_data.json'), 'w') as f:
        json.dump(repo_data, f, indent=2)
    
    return repo_data


def extract_data_for_organizations(config: Dict[str, Any]) -> None:
    """
    Extract data for all organizations in the configuration.
    
    Args:
        config: Configuration dictionary
    """
    # Create output directories
    create_output_dirs(config)
    output_dir = os.path.join(config['output']['data_dir'], 'raw')
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract data for each organization
    for org in config['organizations']:
        print(f"\nProcessing organization: {org}")
        org_output_dir = os.path.join(output_dir, org)
        os.makedirs(org_output_dir, exist_ok=True)
        
        # List repositories
        try:
            repos = list_repositories(org, config)
            
            # Save repository list
            with open(os.path.join(org_output_dir, 'repos.json'), 'w') as f:
                json.dump(repos, f, indent=2)
            
            # Extract data for each repository
            for repo in tqdm(repos, desc=f"Extracting data for {org} repositories"):
                repo_name = repo['name']
                try:
                    extract_repo_data(org, repo_name, config, output_dir)
                    # Add a small delay to avoid rate limiting
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error extracting data for {org}/{repo_name}: {e}")
        except Exception as e:
            print(f"Error listing repositories for {org}: {e}")


def main():
    """Main entry point for the data extraction module."""
    args = parse_args()
    config = load_config(args.config)
    
    print("Starting repository data extraction...")
    extract_data_for_organizations(config)
    print("\nRepository data extraction complete!")


if __name__ == "__main__":
    main()
