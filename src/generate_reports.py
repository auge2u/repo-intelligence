#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Report generation module for the Repository Intelligence Tool.

This module generates CTO-level reports and public portfolios based on analyzed data.
"""

import os
import json
import shutil
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
import jinja2

from src.utils.config import parse_args, load_config, create_output_dirs


def create_template_dirs(config: Dict[str, Any]) -> None:
    """
    Create template directories for reports.
    
    Args:
        config: Configuration dictionary
    """
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    # Create CTO report template
    cto_template_path = os.path.join(template_dir, 'cto_report.html')
    if not os.path.exists(cto_template_path):
        with open(cto_template_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ report.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a73e8; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #1a73e8; margin-top: 30px; }
        h3 { color: #444; }
        .executive-summary { background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .repo-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px; }
        .repo-header { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .tech-badge { display: inline-block; background-color: #e7f4ff; color: #1a73e8; padding: 3px 8px; border-radius: 3px; margin-right: 5px; margin-bottom: 5px; font-size: 0.8em; }
        .service-badge { display: inline-block; background-color: #e9ffe7; color: #0d652d; padding: 3px 8px; border-radius: 3px; margin-right: 5px; margin-bottom: 5px; font-size: 0.8em; }
        .language-chart { height: 150px; margin: 20px 0; }
        .cross-project { margin-top: 40px; }
        .timestamp { color: #999; font-size: 0.8em; text-align: right; margin-top: 50px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ report.title }}</h1>
        
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <p>Analysis of {{ report.executive_summary.repo_count }} repositories across {{ report.executive_summary.orgs_analyzed|join(', ') }} organizations.</p>
            
            <h3>Key Technologies</h3>
            <div>
                {% for tech, count in report.executive_summary.key_technologies %}
                <span class="tech-badge">{{ tech }} ({{ count }})</span>
                {% endfor %}
            </div>
        </div>
        
        <h2>Repository Deep Dives</h2>
        {% for repo in report.repositories %}
        <div class="repo-card">
            <div class="repo-header">
                <h3>{{ repo.name }}</h3>
                <span>{{ repo.organization }}</span>
            </div>
            
            <p><strong>Description:</strong> {{ repo.description }}</p>
            <p><strong>Created:</strong> {{ repo.created_at[:10] if repo.created_at else 'Unknown' }} | <strong>Updated:</strong> {{ repo.updated_at[:10] if repo.updated_at else 'Unknown' }}</p>
            
            {% if repo.homepage %}
            <p><strong>Homepage:</strong> <a href="{{ repo.homepage }}">{{ repo.homepage }}</a></p>
            {% endif %}
            
            <div>
                <h4>Technology Stack</h4>
                {% for tech in repo.tech_stack %}
                <span class="tech-badge">{{ tech }}</span>
                {% endfor %}
            </div>
            
            <div>
                <h4>External Services</h4>
                {% for service, used in repo.services.items() %}
                {% if used %}
                <span class="service-badge">{{ service }}</span>
                {% endif %}
                {% endfor %}
            </div>
            
            {% if repo.readme_summary %}
            <div>
                <h4>Summary</h4>
                <p>{{ repo.readme_summary }}</p>
            </div>
            {% endif %}
            
            {% if repo.techbragging_summary %}
            <div>
                <h4>Technical Highlights</h4>
                <p>{{ repo.techbragging_summary }}</p>
            </div>
            {% endif %}
            
            {% if repo.maturity %}
            <div>
                <h4>Project Maturity</h4>
                <p>{{ repo.maturity }}</p>
            </div>
            {% endif %}
        </div>
        {% endfor %}
        
        <div class="cross-project">
            <h2>Cross-Project Themes</h2>
            <p>This section highlights common patterns, technologies, and approaches observed across multiple repositories.</p>
            
            <h3>Technology Distribution</h3>
            <img src="../visuals/tech_heatmap.png" alt="Technology Heatmap" style="max-width: 100%;">
            
            <h3>Programming Languages</h3>
            <img src="../visuals/language_distribution.png" alt="Language Distribution" style="max-width: 100%;">
            
            <h3>External Services</h3>
            <img src="../visuals/service_usage.png" alt="Service Usage" style="max-width: 100%;">
            
            <h3>Development Timeline</h3>
            <img src="../visuals/repo_timeline.png" alt="Repository Timeline" style="max-width: 100%;">
        </div>
        
        <div class="timestamp">
            Generated on {{ report.generated_at[:10] }}
        </div>
    </div>
</body>
</html>
            ''')
    
    # Create portfolio index template
    portfolio_template_path = os.path.join(template_dir, 'portfolio_index.html')
    if not os.path.exists(portfolio_template_path):
        with open(portfolio_template_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ portfolio.title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 class="text-3xl font-bold text-gray-900">{{ portfolio.title }}</h1>
        </div>
    </header>
    
    <main>
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div class="px-4 py-6 sm:px-0">
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {% for project in portfolio.projects %}
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        {% if project.screenshot %}
                        <img src="{{ project.screenshot }}" alt="{{ project.name }}" class="w-full h-48 object-cover">
                        {% else %}
                        <div class="w-full h-48 bg-gray-200 flex items-center justify-center">
                            <span class="text-gray-500">No screenshot available</span>
                        </div>
                        {% endif %}
                        
                        <div class="px-4 py-5 sm:p-6">
                            <h3 class="text-lg leading-6 font-medium text-gray-900">{{ project.name }}</h3>
                            <div class="mt-2 text-sm text-gray-500">
                                <p>{{ project.description }}</p>
                            </div>
                            
                            <div class="mt-4">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
                                    {% if project.maturity == 'Production-Ready' %}
                                    bg-green-100 text-green-800
                                    {% elif project.maturity == 'Beta' %}
                                    bg-yellow-100 text-yellow-800
                                    {% elif project.maturity == 'Alpha' %}
                                    bg-blue-100 text-blue-800
                                    {% else %}
                                    bg-gray-100 text-gray-800
                                    {% endif %}
                                    mr-2">
                                    {{ project.maturity }}
                                </span>
                                
                                {% if project.homepage %}
                                <a href="{{ project.homepage }}" target="_blank" class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-indigo-100 text-indigo-800">
                                    View Live
                                </a>
                                {% endif %}
                            </div>
                            
                            <div class="mt-4">
                                {% for tech in project.tech_stack[:5] %}
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 mr-1 mb-1">
                                    {{ tech }}
                                </span>
                                {% endfor %}
                                {% if project.tech_stack|length > 5 %}
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800">
                                    +{{ project.tech_stack|length - 5 }} more
                                </span>
                                {% endif %}
                            </div>
                            
                            <div class="mt-4">
                                <a href="{{ project.name|lower|replace(' ', '_') }}.html" class="text-indigo-600 hover:text-indigo-900">
                                    View Details
                                </a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </main>
    
    <footer class="bg-white">
        <div class="max-w-7xl mx-auto py-6 px-4 overflow-hidden sm:px-6 lg:px-8">
            <p class="text-center text-gray-500">Generated on {{ portfolio.generated_at[:10] }}</p>
        </div>
    </footer>
</body>
</html>
            ''')
    
    # Create portfolio project template
    project_template_path = os.path.join(template_dir, 'portfolio_project.html')
    if not os.path.exists(project_template_path):
        with open(project_template_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ project.name }} - Portfolio</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <header class="bg-white shadow">
        <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 class="text-3xl font-bold text-gray-900">{{ project.name }}</h1>
        </div>
    </header>
    
    <main>
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div class="px-4 py-6 sm:px-0">
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    {% if project.screenshot %}
                    <img src="{{ project.screenshot }}" alt="{{ project.name }}" class="w-full h-64 object-cover">
                    {% endif %}
                    
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Project Details</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">{{ project.description }}</p>
                    </div>
                    
                    <div class="border-t border-gray-200">
                        <dl>
                            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Maturity</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium 
                                        {% if project.maturity == 'Production-Ready' %}
                                        bg-green-100 text-green-800
                                        {% elif project.maturity == 'Beta' %}
                                        bg-yellow-100 text-yellow-800
                                        {% elif project.maturity == 'Alpha' %}
                                        bg-blue-100 text-blue-800
                                        {% else %}
                                        bg-gray-100 text-gray-800
                                        {% endif %}">
                                        {{ project.maturity }}
                                    </span>
                                </dd>
                            </div>
                            
                            {% if project.homepage %}
                            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Homepage</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    <a href="{{ project.homepage }}" target="_blank" class="text-indigo-600 hover:text-indigo-900">{{ project.homepage }}</a>
                                </dd>
                            </div>
                            {% endif %}
                            
                            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Technology Stack</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                                    <div class="flex flex-wrap">
                                        {% for tech in project.tech_stack %}
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-gray-100 text-gray-800 mr-2 mb-2">
                                            {{ tech }}
                                        </span>
                                        {% endfor %}
                                    </div>
                                </dd>
                            </div>
                            
                            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                                <dt class="text-sm font-medium text-gray-500">Summary</dt>
                                <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ project.summary }}</dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <footer class="bg-white mt-12">
        <div class="max-w-7xl mx-auto py-6 px-4 overflow-hidden sm:px-6 lg:px-8">
            <p class="text-center text-sm text-gray-500">
                <a href="index.html" class="text-indigo-600 hover:text-indigo-900">← Back to Portfolio</a>
            </p>
        </div>
    </footer>
</body>
</html>
            ''')


def load_repository_data(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Load repository data from processed JSON file.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of repository dictionaries
    """
    repos_path = os.path.join(config['output']['data_dir'], 'processed', 'repositories.json')
    try:
        with open(repos_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading repository data: {e}")
        return []


def get_top_technologies(repositories: List[Dict[str, Any]], top_n: int = 10) -> List[Any]:
    """
    Get the most commonly used technologies across repositories.
    
    Args:
        repositories: List of repository dictionaries
        top_n: Number of top technologies to return
        
    Returns:
        List of (technology, count) tuples
    """
    tech_counts = {}
    for repo in repositories:
        for tech in repo.get('tech_stack', []):
            if tech in tech_counts:
                tech_counts[tech] += 1
            else:
                tech_counts[tech] = 1
    
    return sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]


def extract_readme_summary(repo: Dict[str, Any], data_dir: str) -> str:
    """
    Extract a summary from the repository README.
    
    Args:
        repo: Repository dictionary
        data_dir: Data directory
        
    Returns:
        README summary
    """
    # Check if summary already exists in the repository data
    if 'summary' in repo:
        return repo['summary']
    
    # Load README from raw data
    readme_path = os.path.join(
        data_dir, 'raw', 
        repo['org'], repo['name'], 
        'repo_data.json'
    )
    try:
        with open(readme_path, 'r') as f:
            repo_data = json.load(f)
            readme = repo_data.get('readme', '')
            
            # Extract first paragraph
            if readme:
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
                    summary = first_paragraph.replace('#', '').replace('*', '').replace('`', '').strip()
                    
                    # Truncate if too long
                    if len(summary) > 200:
                        return summary[:197] + "..."
                    
                    return summary
    except Exception:
        pass
    
    return ""


def extract_techbragging_summary(repo: Dict[str, Any], data_dir: str) -> str:
    """
    Extract a summary from the repository techbragging.md file.
    
    Args:
        repo: Repository dictionary
        data_dir: Data directory
        
    Returns:
        Technical highlights summary
    """
    # Load techbragging from raw data
    techbragging_path = os.path.join(
        data_dir, 'raw', 
        repo['org'], repo['name'], 
        'repo_data.json'
    )
    try:
        with open(techbragging_path, 'r') as f:
            repo_data = json.load(f)
            techbragging = repo_data.get('techbragging', '')
            
            # Extract first paragraph
            if techbragging:
                paragraphs = techbragging.split('\n\n')
                if paragraphs:
                    # Skip heading if it exists
                    first_paragraph = paragraphs[0]
                    if first_paragraph.startswith('#'):
                        if len(paragraphs) > 1:
                            first_paragraph = paragraphs[1]
                        else:
                            first_paragraph = ""
                    
                    # Clean up markdown
                    summary = first_paragraph.replace('#', '').replace('*', '').replace('`', '').strip()
                    
                    # Truncate if too long
                    if len(summary) > 200:
                        return summary[:197] + "..."
                    
                    return summary
    except Exception:
        pass
    
    return ""


def generate_cto_report(repositories: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """
    Generate the CTO-level technical report.
    
    Args:
        repositories: List of repository dictionaries
        config: Configuration dictionary
    """
    # Create report directory
    report_dir = config['output']['cto_report_dir']
    os.makedirs(report_dir, exist_ok=True)
    
    # Prepare report data
    report = {
        "title": "CTO-Level Technical and Strategic Insight Report",
        "generated_at": datetime.now().isoformat(),
        "executive_summary": {
            "repo_count": len(repositories),
            "orgs_analyzed": config['organizations'],
            "key_technologies": get_top_technologies(repositories)
        },
        "repositories": []
    }
    
    # Add detailed repository information
    for repo in repositories:
        # Extract README and techbragging summaries
        readme_summary = extract_readme_summary(repo, config['output']['data_dir'])
        techbragging_summary = extract_techbragging_summary(repo, config['output']['data_dir'])
        
        report["repositories"].append({
            "name": repo['name'],
            "organization": repo['org'],
            "description": repo.get('description', ''),
            "created_at": repo.get('createdAt', ''),
            "updated_at": repo.get('updatedAt', ''),
            "homepage": repo.get('homepage', ''),
            "tech_stack": repo.get('tech_stack', []),
            "languages": repo.get('languages', {}),
            "services": repo.get('services', {}),
            "readme_summary": readme_summary,
            "techbragging_summary": techbragging_summary,
            "maturity": repo.get('maturity', 'Unknown')
        })
    
    # Save report to JSON
    with open(os.path.join(report_dir, 'cto_report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create HTML report
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
    )
    template = env.get_template('cto_report.html')
    html_content = template.render(report=report)
    
    with open(os.path.join(report_dir, 'cto_report.html'), 'w') as f:
        f.write(html_content)
    
    # Copy visualizations
    for vis_file in ['tech_heatmap.png', 'language_distribution.png', 'service_usage.png', 'repo_timeline.png']:
        src_path = os.path.join(config['output']['visuals_dir'], vis_file)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(report_dir, vis_file))
    
    # Try to convert to PDF if wkhtmltopdf is installed
    try:
        subprocess.run(
            ['wkhtmltopdf', os.path.join(report_dir, 'cto_report.html'), os.path.join(report_dir, 'cto_report.pdf')],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"CTO report generated: {os.path.join(report_dir, 'cto_report.pdf')}")
    except Exception:
        print(f"HTML CTO report generated: {os.path.join(report_dir, 'cto_report.html')}")
        print("PDF conversion failed. Please install wkhtmltopdf to generate PDFs.")


def generate_portfolio(repositories: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """
    Generate the public-facing portfolio website.
    
    Args:
        repositories: List of repository dictionaries
        config: Configuration dictionary
    """
    # Create portfolio directory
    portfolio_dir = config['output']['portfolio_dir']
    os.makedirs(portfolio_dir, exist_ok=True)
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = os.path.join(portfolio_dir, 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Copy screenshots
    src_screenshots_dir = os.path.join(config['output']['visuals_dir'], 'screenshots')
    if os.path.exists(src_screenshots_dir):
        for file in os.listdir(src_screenshots_dir):
            if file.endswith('.png'):
                shutil.copy2(
                    os.path.join(src_screenshots_dir, file),
                    os.path.join(screenshots_dir, file)
                )
    
    # Prepare portfolio data
    portfolio = {
        "title": "Habitusnet Project & Product Portfolio",
        "generated_at": datetime.now().isoformat(),
        "projects": []
    }
    
    # Add curated project information
    for repo in repositories:
        # Only include projects with sufficient documentation or maturity
        if len(repo.get('summary', '')) > 10 or repo.get('homepage'):
            portfolio["projects"].append({
                "name": repo['name'],
                "description": repo.get('description', ''),
                "tech_stack": repo.get('tech_stack', []),
                "homepage": repo.get('homepage', ''),
                "summary": repo.get('summary', ''),
                "maturity": repo.get('maturity', 'Unknown'),
                "screenshot": repo.get('screenshot', '').replace('visuals/', '')
            })
    
    # Save portfolio to JSON
    with open(os.path.join(portfolio_dir, 'portfolio.json'), 'w') as f:
        json.dump(portfolio, f, indent=2)
    
    # Create HTML portfolio
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
    )
    
    # Generate index page
    template = env.get_template('portfolio_index.html')
    html_content = template.render(portfolio=portfolio)
    
    with open(os.path.join(portfolio_dir, 'index.html'), 'w') as f:
        f.write(html_content)
    
    # Generate individual project pages
    project_template = env.get_template('portfolio_project.html')
    for project in portfolio["projects"]:
        html_content = project_template.render(project=project)
        
        project_filename = project["name"].lower().replace(" ", "_")
        with open(os.path.join(portfolio_dir, f"{project_filename}.html"), 'w') as f:
            f.write(html_content)


def main():
    """Main entry point for the report generation module."""
    args = parse_args()
    config = load_config(args.config)
    
    print("Starting report generation...")
    create_output_dirs(config)
    create_template_dirs(config)
    
    # Load repository data
    repositories = load_repository_data(config)
    
    if not repositories:
        print("No repository data found. Please run the analysis module first.")
        return
    
    # Generate CTO report
    print("Generating CTO-level technical report...")
    generate_cto_report(repositories, config)
    
    # Generate portfolio
    print("Generating project portfolio...")
    generate_portfolio(repositories, config)
    
    print("\nReport generation complete!")


if __name__ == "__main__":
    main()
