#!/bin/bash

# Repository Intelligence & Portfolio Curation
# Main execution script

set -e

CONFIG_FILE="config.yaml"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="run_intelligence_${TIMESTAMP}.log"

# Function to display a progress banner
show_banner() {
    local text="$1"
    local width=80
    local padding=$(( (width - ${#text}) / 2 ))
    local line=$(printf '%*s' "$width" | tr ' ' '=')
    
    echo ""
    echo "$line"
    printf "%*s%s%*s\n" $padding "" "$text" $padding ""
    echo "$line"
    echo ""
}

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    echo "[$timestamp] [$level] $message"
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Initialize log file
echo "# Repository Intelligence & Portfolio Curation Log" > "$LOG_FILE"
echo "# Started at: $(date)" >> "$LOG_FILE"
echo "# Configuration: $CONFIG_FILE" >> "$LOG_FILE"
echo "-------------------------------------------" >> "$LOG_FILE"

show_banner "Repository Intelligence & Portfolio Curation"
log_message "INFO" "Starting repository analysis process..."

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    log_message "ERROR" "Config file not found: $CONFIG_FILE"
    echo "Please copy config.example.yaml to config.yaml and edit as needed."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    log_message "ERROR" "Python 3 not found. Please install Python 3.8 or newer."
    exit 1
fi

# Check GitHub CLI installation
if ! command -v gh &> /dev/null; then
    log_message "ERROR" "GitHub CLI (gh) not found. Please install it first."
    echo "Visit: https://cli.github.com/"
    exit 1
fi

# Check GitHub authentication
if ! gh auth status &> /dev/null; then
    log_message "WARNING" "GitHub CLI not authenticated"
    echo "Please authenticate with GitHub CLI first:"
    gh auth login
fi

# Create output directories
show_banner "Initializing Output Directories"
log_message "INFO" "Creating output directories..."
python3 -c "import yaml; config = yaml.safe_load(open('$CONFIG_FILE')); import os; [os.makedirs(d, exist_ok=True) for d in [config['output']['base_dir'], config['output']['cto_report_dir'], config['output']['portfolio_dir'], config['output']['visuals_dir'], config['output']['data_dir']]]"

# Phase 1: Extract repository data
show_banner "Phase 1: Data Extraction"
log_message "INFO" "Starting repository data extraction..."
python3 src/extract_data.py --config "$CONFIG_FILE" 2>&1 | tee -a "$LOG_FILE"
log_message "INFO" "Repository data extraction complete"

# Phase 2: Analyze repositories
show_banner "Phase 2: Repository Analysis"
log_message "INFO" "Starting repository analysis..."
python3 src/analyze_repos.py --config "$CONFIG_FILE" 2>&1 | tee -a "$LOG_FILE"
log_message "INFO" "Repository analysis complete"

# Phase 3: Collect screenshots (if enabled)
is_screenshots_enabled=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['screenshots']['enabled'])")
if [ "$is_screenshots_enabled" = "True" ]; then
    show_banner "Phase 3: Screenshot Collection"
    log_message "INFO" "Starting screenshot collection..."
    python3 src/collect_screenshots.py --config "$CONFIG_FILE" 2>&1 | tee -a "$LOG_FILE"
    log_message "INFO" "Screenshot collection complete"
else
    log_message "INFO" "Screenshot collection is disabled in config"
fi

# Phase 4: Generate reports
show_banner "Phase 4: Report Generation"
log_message "INFO" "Generating reports..."
python3 src/generate_reports.py --config "$CONFIG_FILE" 2>&1 | tee -a "$LOG_FILE"
log_message "INFO" "Report generation complete"

# Display summary
show_banner "Process Complete"
echo "Repository Intelligence & Portfolio Curation complete!"
echo "Log file: $LOG_FILE"

# Show output locations
echo ""
echo "Output Locations:"
echo "- CTO Report: $(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['output']['cto_report_dir'])")/cto_report.html"
echo "- Portfolio Website: $(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['output']['portfolio_dir'])")/index.html"
echo "- Visualizations: $(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['output']['visuals_dir'])")"
echo ""

# Display runtime information
RUNTIME=$SECONDS
log_message "INFO" "Total runtime: $(($RUNTIME / 60)) minutes and $(($RUNTIME % 60)) seconds"
echo "Total runtime: $(($RUNTIME / 60)) minutes and $(($RUNTIME % 60)) seconds"
