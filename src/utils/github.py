#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub API utilities for the Repository Intelligence Tool.
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional, Union
import base64
import requests
from tqdm import tqdm


def run_gh_cmd(command: List[str]) -> Dict[str, Any]:
    """
    Run a GitHub CLI command and return the JSON output.
    
    Args:
        command: List of command parts to execute
        
    Returns:
        JSON decoded output from the command
        
    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    try:
        result = subprocess.run(
            ['gh'] + command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {'output': result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"Command: gh {' '.join(command)}")
        print(f"stderr: {e.stderr}")
        raise


def list_repositories(org: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    List repositories for an organization.
    
    Args:
        org: Organization name
        config: Configuration dictionary
        
    Returns:
        List of repository dictionaries
    """
    max_repos = config['github'].get('max_repos', 100)
    
    print(f"Listing repositories for {org}...")
    repos = run_gh_cmd([
        'repo', 'list', 
        org, 
        '--json', 'name,description,url,createdAt,updatedAt,pushedAt',
        '--limit', str(max_repos)
    ])
    
    # Apply repository filters if configured
    if config['repository_filter'].get('use_include_list', False):
        include_list = config['repository_filter'].get('include_list', [])
        repos = [r for r in repos if r['name'] in include_list]
    
    exclude_list = config['repository_filter'].get('exclude_list', [])
    repos = [r for r in repos if r['name'] not in exclude_list]
    
    return repos


def get_repository_metadata(org: str, repo: str) -> Dict[str, Any]:
    """
    Get metadata for a repository.
    
    Args:
        org: Organization name
        repo: Repository name
        
    Returns:
        Repository metadata dictionary
    """
    print(f"Getting metadata for {org}/{repo}...")
    return run_gh_cmd([
        'repo', 'view', 
        f"{org}/{repo}", 
        '--json', 'name,description,homepageUrl,isPrivate,stargazerCount,forkCount,defaultBranchRef'
    ])


def get_repository_languages(org: str, repo: str) -> Dict[str, int]:
    """
    Get languages used in a repository.
    
    Args:
        org: Organization name
        repo: Repository name
        
    Returns:
        Dictionary mapping language names to byte counts
    """
    try:
        print(f"Getting languages for {org}/{repo}...")
        result = run_gh_cmd(['api', f"repos/{org}/{repo}/languages"])
        return result
    except Exception as e:
        print(f"Error getting languages for {org}/{repo}: {e}")
        return {}


def get_repository_contributors(org: str, repo: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get contributors for a repository.
    
    Args:
        org: Organization name
        repo: Repository name
        config: Configuration dictionary
        
    Returns:
        List of contributor dictionaries
    """
    try:
        print(f"Getting contributors for {org}/{repo}...")
        result = run_gh_cmd(['api', f"repos/{org}/{repo}/stats/contributors"])
        return result[:config['github'].get('max_contributors', 50)]
    except Exception as e:
        print(f"Error getting contributors for {org}/{repo}: {e}")
        return []


def get_file_content(org: str, repo: str, path: str, branch: Optional[str] = None) -> Optional[str]:
    """
    Get content of a file in a repository.
    
    Args:
        org: Organization name
        repo: Repository name
        path: Path to the file
        branch: Branch name (optional)
        
    Returns:
        File content as string, or None if the file doesn't exist
    """
    try:
        url = f"repos/{org}/{repo}/contents/{path}"
        if branch:
            url += f"?ref={branch}"
            
        result = run_gh_cmd(['api', url])
        
        if isinstance(result, dict) and 'content' in result:
            content = base64.b64decode(result['content']).decode('utf-8')
            return content
        return None
    except Exception as e:
        return None


def find_config_files(org: str, repo: str, extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Find configuration files in a repository.
    
    Args:
        org: Organization name
        repo: Repository name
        extensions: List of file extensions to look for (default: ['.toml', '.yaml', '.yml', '.json'])
        
    Returns:
        List of file metadata dictionaries
    """
    if extensions is None:
        extensions = ['.toml', '.yaml', '.yml', '.json']
        
    try:
        print(f"Finding config files for {org}/{repo}...")
        # Get repository contents
        result = run_gh_cmd(['api', f"repos/{org}/{repo}/contents"])
        
        config_files = []
        for item in result:
            if item['type'] == 'file':
                _, ext = os.path.splitext(item['name'])
                if ext in extensions:
                    config_files.append(item)
            elif item['type'] == 'dir' and item['name'] in ['.github', 'config', 'configs']:
                # Look for config files in these directories
                try:
                    dir_contents = run_gh_cmd(['api', item['url']])
                    for dir_item in dir_contents:
                        if dir_item['type'] == 'file':
                            _, ext = os.path.splitext(dir_item['name'])
                            if ext in extensions:
                                config_files.append(dir_item)
                except Exception:
                    pass
                    
        return config_files
    except Exception as e:
        print(f"Error finding config files for {org}/{repo}: {e}")
        return []


def detect_services(org: str, repo: str, config_files: List[Dict[str, Any]], service_keywords: List[str]) -> Dict[str, bool]:
    """
    Detect external services used in a repository.
    
    Args:
        org: Organization name
        repo: Repository name
        config_files: List of configuration file metadata
        service_keywords: List of service keywords to look for
        
    Returns:
        Dictionary mapping service names to boolean indicating if they are used
    """
    services = {service: False for service in service_keywords}
    
    for file_meta in config_files:
        try:
            content = get_file_content(org, repo, file_meta['path'])
            if content:
                content_lower = content.lower()
                for service in service_keywords:
                    if service.lower() in content_lower:
                        services[service] = True
        except Exception:
            pass
            
    # Special check for GitHub Actions
    try:
        result = run_gh_cmd(['api', f"repos/{org}/{repo}/contents/.github/workflows"])
        if isinstance(result, list) and len(result) > 0:
            services['github actions'] = True
    except Exception:
        pass
        
    return services
