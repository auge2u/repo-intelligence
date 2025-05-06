#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Screenshot collection module for the Repository Intelligence Tool.

This module takes screenshots of live projects for the portfolio.
"""

import os
import json
import time
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.utils.config import parse_args, load_config, create_output_dirs


def setup_webdriver(config: Dict[str, Any]) -> webdriver.Chrome:
    """
    Set up Chrome WebDriver for screenshot collection.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Chrome WebDriver instance
    """
    print("Setting up WebDriver...")
    
    # Configure Chrome options
    chrome_options = Options()
    
    # Set headless mode based on configuration
    if config['screenshots'].get('headless', True):
        chrome_options.add_argument("--headless")
    
    # Set window size
    width = config['screenshots'].get('width', 1920)
    height = config['screenshots'].get('height', 1080)
    chrome_options.add_argument(f"--window-size={width},{height}")
    
    # Additional options for stability
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    
    # Install and setup ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    # Create WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set page load timeout
    timeout = config['screenshots'].get('page_load_timeout', 30)
    driver.set_page_load_timeout(timeout)
    
    return driver


def take_screenshot(driver: webdriver.Chrome, url: str, output_path: str, config: Dict[str, Any]) -> bool:
    """
    Take a screenshot of a web page.
    
    Args:
        driver: Chrome WebDriver instance
        url: URL to capture
        output_path: Path to save the screenshot
        config: Configuration dictionary
        
    Returns:
        True if the screenshot was successful, False otherwise
    """
    try:
        print(f"Taking screenshot of {url}")
        
        # Navigate to URL
        driver.get(url)
        
        # Wait for page to load
        time.sleep(config['screenshots'].get('page_load_timeout', 10) / 2)
        
        # Take screenshot
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        driver.save_screenshot(output_path)
        
        print(f"Screenshot saved to {output_path}")
        return True
    except TimeoutException:
        print(f"Timeout while loading {url}")
        return False
    except WebDriverException as e:
        print(f"WebDriver error for {url}: {e}")
        return False
    except Exception as e:
        print(f"Error taking screenshot of {url}: {e}")
        return False


def collect_screenshots(config: Dict[str, Any]) -> None:
    """
    Collect screenshots of live projects.
    
    Args:
        config: Configuration dictionary
    """
    # Check if screenshots are enabled
    if not config['screenshots'].get('enabled', True):
        print("Screenshot collection is disabled in configuration.")
        return
    
    # Create output directory
    screenshots_dir = os.path.join(config['output']['visuals_dir'], 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Load processed repository data
    repos_path = os.path.join(config['output']['data_dir'], 'processed', 'repositories.json')
    try:
        with open(repos_path, 'r') as f:
            repositories = json.load(f)
    except Exception as e:
        print(f"Error loading repository data: {e}")
        return
    
    # Filter repositories with homepages
    repos_with_homepage = [repo for repo in repositories if repo.get('homepage')]
    
    if not repos_with_homepage:
        print("No repositories with homepage URLs found.")
        return
    
    print(f"Found {len(repos_with_homepage)} repositories with homepages.")
    
    # Setup WebDriver
    driver = setup_webdriver(config)
    
    try:
        # Take screenshots for each repository with a homepage
        for repo in repos_with_homepage:
            homepage = repo.get('homepage', '')
            if not homepage or not homepage.startswith(('http://', 'https://')):
                continue
            
            # Parse URL for filename
            parsed_url = urlparse(homepage)
            filename = f"{repo['name']}_{parsed_url.netloc.replace(':', '_')}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            # Take screenshot
            success = take_screenshot(driver, homepage, filepath, config)
            
            if success:
                # Add screenshot path to repository data
                repo['screenshot'] = os.path.join('visuals', 'screenshots', filename)
        
        # Save updated repository data
        with open(repos_path, 'w') as f:
            json.dump(repositories, f, indent=2)
    finally:
        # Close WebDriver
        driver.quit()


def main():
    """Main entry point for the screenshot collection module."""
    args = parse_args()
    config = load_config(args.config)
    
    print("Starting screenshot collection...")
    create_output_dirs(config)
    
    collect_screenshots(config)
    
    print("\nScreenshot collection complete!")


if __name__ == "__main__":
    main()
