# Repository Intelligence & Portfolio Curation Tool

A comprehensive tool for analyzing GitHub repositories, generating CTO-level technical reports, and creating public-facing project portfolios.

## 🚀 Features

- **Repository Data Extraction**: Collect metadata, code insights, and technical details from GitHub repositories
- **Technical Analysis**: Analyze code, dependencies, technologies, and architecture patterns
- **Visualization**: Generate technology heatmaps, complexity curves, and other insightful visuals
- **CTO Report Generation**: Create comprehensive technical reports for leadership teams
- **Portfolio Website Generation**: Build public-facing project portfolios to showcase your work
- **Screenshot Collection**: Automatically capture screenshots of live projects

## 📋 Requirements

- Python 3.8+
- GitHub CLI (gh)
- GitHub API access token with appropriate permissions
- Required Python packages (see `requirements.txt`)

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/auge2u/repo-intelligence.git
cd repo-intelligence

# Install required Python packages
pip install -r requirements.txt

# Install GitHub CLI (if not already installed)
# For Ubuntu/Debian
# sudo apt install gh

# For macOS using Homebrew
# brew install gh

# For Windows using Chocolatey
# choco install gh

# Authenticate with GitHub CLI
gh auth login
```

## 🚀 Usage

```bash
# Configure the tool
cp config.example.yaml config.yaml
# Edit config.yaml to specify your organizations and repositories

# Run the complete analysis
./run_intelligence.sh

# Or run individual phases
python src/extract_data.py
python src/analyze_repos.py
python src/collect_screenshots.py
python src/generate_reports.py
```

## 📊 Output

After running the tool, you'll find the following outputs in the `output` directory:

- `output/cto_report/` - CTO-level technical reports (PDF and HTML)
- `output/portfolio/` - Public-facing portfolio website files
- `output/visuals/` - Data visualizations and project screenshots
- `output/data/` - Raw and processed repository data

## 📁 Project Structure

```
repo-intelligence/
├── config.example.yaml     # Example configuration file
├── run_intelligence.sh     # Main execution script
├── requirements.txt        # Python dependencies
├── src/                    # Source code
│   ├── extract_data.py     # Repository data extraction
│   ├── analyze_repos.py    # Repository analysis
│   ├── collect_screenshots.py # Screenshot collection
│   ├── generate_reports.py # Report generation
│   └── utils/              # Utility functions
├── templates/              # HTML templates for reports
└── output/                 # Generated outputs
    ├── cto_report/         # CTO-level reports
    ├── portfolio/          # Portfolio website
    ├── visuals/            # Visualizations
    └── data/               # Raw and processed data
```

## 🔄 Workflow

1. **Configuration**: Define which organizations and repositories to analyze
2. **Data Extraction**: Collect repository metadata, code stats, and documentation
3. **Analysis**: Process the data to identify technologies, patterns, and insights
4. **Visualization**: Generate visual representations of the analysis
5. **Report Generation**: Create comprehensive reports and portfolio websites

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
