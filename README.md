# Repository Intelligence & Portfolio Curation Tool

A comprehensive tool for analyzing GitHub repositories, generating CTO-level technical reports, and creating public-facing project portfolios.

![Repository Intelligence](https://user-images.githubusercontent.com/750093/234691234-a8f9c123-1234-5678-9abc-def0123456.png)

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/auge2u/repo-intelligence.git
cd repo-intelligence

# Install dependencies
pip install -r requirements.txt

# Setup GitHub CLI (if not already installed)
# macOS: brew install gh
# Linux: apt install gh
# Windows: winget install GitHub.cli

# Authenticate with GitHub
gh auth login

# Create config file
cp config.example.yaml config.yaml
# Edit config.yaml as needed

# Make script executable
chmod +x run_intelligence.sh

# Run the analysis
./run_intelligence.sh
```

## 🎯 Features

- **Repository Data Extraction**: Collect metadata, code insights, and technical details from GitHub repositories
- **Technical Analysis**: Analyze code, dependencies, technologies, and architecture patterns
- **Visualization**: Generate technology heatmaps, complexity curves, and other insightful visuals
- **CTO Report Generation**: Create comprehensive technical reports for leadership teams
- **Portfolio Website Generation**: Build public-facing project portfolios to showcase your work
- **Screenshot Collection**: Automatically capture screenshots of live projects

## 🧩 Use Cases

1. **Technical Leadership Reports**: Generate comprehensive technical landscape reports for CTOs and engineering leadership
2. **Portfolio Development**: Create a professional portfolio of past projects with technical details and live screenshots
3. **Technology Audit**: Analyze technology choices and patterns across your organization's repositories
4. **Engineering Capability Mapping**: Identify technical skills and capabilities demonstrated in your codebase
5. **Investor Due Diligence**: Showcase technical depth and breadth for investors or potential partners

## 📊 Generated Reports

### CTO-Level Technical Report

A comprehensive technical analysis including:
- Executive summary of key technologies and capabilities
- Deep-dive analysis of each repository
- Cross-project patterns and technology usage
- Skills and capability mapping
- Technical maturity assessment

### Public Portfolio Website

A web-based portfolio showcasing:
- Project overview and description
- Technology stack visualization
- Live screenshots
- Maturity indicators
- Links to live projects

## 🧠 Analysis Methodology

The tool analyzes repositories across multiple dimensions:

1. **Technical Skill Profiling**
   - Language and framework diversity
   - Tooling and stack maturity
   - DevOps and CI/CD practices

2. **Architecture and System Design**
   - Modular design patterns
   - Scalability approaches
   - Infrastructure-as-code usage

3. **Problem-Solving and Innovation**
   - Creative abstractions
   - Domain-specific optimizations
   - Advanced technology adoption

4. **Business & Customer Value**
   - Problem-solution alignment
   - User journey support
   - Monetization potential

5. **Team and Leadership Signals**
   - Code review dynamics
   - Collaboration patterns
   - Project structure

## 🛠️ Configuration Options

The `config.yaml` file allows you to customize:

- GitHub organizations to analyze
- Repository inclusion/exclusion filters
- Output directory structure
- Technical keywords to identify
- Service detection patterns
- Screenshot capture settings

## 📝 Running Individual Phases

Instead of running the complete analysis, you can run individual phases:

```bash
# Extract data only
python src/extract_data.py --config config.yaml

# Analyze repositories
python src/analyze_repos.py --config config.yaml

# Collect screenshots
python src/collect_screenshots.py --config config.yaml

# Generate reports
python src/generate_reports.py --config config.yaml
```

## 🔄 Automation with GitHub Actions

This repository includes a GitHub Action workflow that:
1. Runs weekly (or on-demand)
2. Performs the complete analysis
3. Generates all reports and visualizations
4. Uploads artifacts for download
5. Optionally deploys the portfolio to GitHub Pages

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
