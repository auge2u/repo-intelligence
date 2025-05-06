#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration utilities for the Repository Intelligence Tool.
"""

import os
import yaml
import argparse
from typing import Dict, Any


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Repository Intelligence Tool")
    parser.add_argument(
        "--config", "-c", 
        type=str, 
        default="config.yaml",
        help="Path to the configuration file (default: config.yaml)"
    )
    return parser.parse_args()


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing the configuration
        
    Raises:
        FileNotFoundError: If the configuration file does not exist
        yaml.YAMLError: If the configuration file is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML configuration: {e}")


def get_output_paths(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Get output paths from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary containing output paths
    """
    return {
        'base_dir': config['output']['base_dir'],
        'cto_report_dir': config['output']['cto_report_dir'],
        'portfolio_dir': config['output']['portfolio_dir'],
        'visuals_dir': config['output']['visuals_dir'],
        'data_dir': config['output']['data_dir']
    }


def create_output_dirs(config: Dict[str, Any]) -> None:
    """
    Create output directories if they don't exist.
    
    Args:
        config: Configuration dictionary
    """
    paths = get_output_paths(config)
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
