#!/bin/bash

# Repository Intelligence & Portfolio Curation
# Main execution script

set -e

CONFIG_FILE="config.yaml"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Config file not found: $CONFIG_FILE"
    echo "Please copy config.example.yaml to config.yaml and edit as needed."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.8 or newer."
    exit 1
fi

# Check GitHub CLI installation
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) not found. Please install it first."
    echo "Visit: https://cli.github.com/"
    exit 1
fi

# Check GitHub authentication
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub CLI first:"
    gh auth login
fi

# Create output directories
echo "Creating output directories..."
python3 -c "import yaml; config = yaml.safe_load(open('$CONFIG_FILE')); import os; [os.makedirs(d, exist_ok=True) for d in [config['output']['base_dir'], config['output']['cto_report_dir'], config['output']['portfolio_dir'], config['output']['visuals_dir'], config['output']['data_dir']]]"

# Phase 1: Extract repository data
echo "Phase 1: Extracting repository data..."
python3 src/extract_data.py --config "$CONFIG_FILE"

# Phase 2: Analyze repositories
echo "Phase 2: Analyzing repositories..."
python3 src/analyze_repos.py --config "$CONFIG_FILE"

# Phase 3: Collect screenshots (if enabled)
is_screenshots_enabled=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['screenshots']['enabled'])")
if [ "$is_screenshots_enabled" = "True" ]; then
    echo "Phase 3: Collecting screenshots..."
    python3 src/collect_screenshots.py --config "$CONFIG_FILE"
else
    echo "Phase 3: Screenshot collection is disabled in config."
fi

# Phase 4: Generate reports
echo "Phase 4: Generating reports..."
python3 src/generate_reports.py --config "$CONFIG_FILE"

echo "Repository Intelligence & Portfolio Curation complete!"
echo "Reports are available in the output directory."
