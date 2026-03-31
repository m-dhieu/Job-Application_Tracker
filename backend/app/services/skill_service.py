import re
import requests
from typing import List, Set, Dict, Any
import logging
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

# Common programming languages, frameworks, and tools
TECH_SKILLS = {
    # Programming Languages
    'python', 'javascript', 'java', 'typescript', 'go', 'rust', 'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin',
    'scala', 'clojure', 'haskell', 'erlang', 'elixir', 'dart', 'r', 'matlab', 'sql',

    # Frontend Technologies
    'react', 'vue', 'angular', 'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less',
    'html', 'css', 'webpack', 'vite', 'parcel', 'rollup',

    # Backend Technologies
    'node.js', 'express', 'fastapi', 'django', 'flask', 'spring', 'laravel', 'rails',
    'gin', 'echo', 'fiber', 'nest.js', 'koa', 'hapi',

    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
    'sqlite', 'mariadb', 'oracle', 'sql server', 'neo4j', 'influxdb',

    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
    'gitlab', 'github', 'circleci', 'travis', 'helm', 'istio', 'prometheus', 'grafana',

    # Data & ML
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'spark',
    'hadoop', 'kafka', 'airflow', 'dbt', 'snowflake', 'databricks',

    # Testing
    'jest', 'pytest', 'junit', 'cypress', 'selenium', 'mocha', 'chai', 'testing-library',

    # Others
    'git', 'linux', 'bash', 'vim', 'vscode', 'intellij', 'figma', 'sketch', 'photoshop'
}

def extract_skills_from_text(text: str) -> List[str]:
    """Extract technical skills from job description text"""
    if not text:
        return []

    # Convert to lowercase for matching
    text_lower = text.lower()

    # Remove HTML tags if any
    text_clean = re.sub(r'<[^>]+>', ' ', text_lower)

    # Find skills mentioned in the text
    found_skills = set()

    for skill in TECH_SKILLS:
        # Create regex pattern for the skill
        # Look for whole word matches with word boundaries
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'

        if re.search(pattern, text_clean):
            found_skills.add(skill)

    # Also look for common variations and abbreviations
    skill_variations = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'k8s': 'kubernetes',
        'tf': 'terraform',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'ci/cd': 'continuous integration',
        'devops': 'devops',
        'microservices': 'microservices',
        'api': 'api development',
        'rest': 'rest api',
        'graphql': 'graphql',
        'nosql': 'nosql',
        'full-stack': 'full-stack development',
        'frontend': 'frontend development',
        'backend': 'backend development',
        'mobile': 'mobile development',
        'ios': 'ios development',
        'android': 'android development'
    }

    for abbrev, full_skill in skill_variations.items():
        pattern = r'\b' + re.escape(abbrev.lower()) + r'\b'
        if re.search(pattern, text_clean):
            found_skills.add(full_skill)

    return sorted(list(found_skills))

def scrape_job_description(job_url: str) -> str:
    """Scrape full job description from job URL"""
    if not job_url:
        return ""

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find job description in common selectors
        description_selectors = [
            '.job-description',
            '.description',
            '.job-content',
            '.content',
            '[data-testid="job-description"]',
            '.job-detail',
            '.posting-content'
        ]

        description_text = ""
        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                description_text = element.get_text()
                break

        # If no specific selector found, try to get text from body
        if not description_text:
            body = soup.find('body')
            if body:
                description_text = body.get_text()

        return description_text[:2000]  # Limit to first 2000 characters

    except Exception as e:
        logger.warning(f"Failed to scrape job description from {job_url}: {e}")
        return ""

def extract_skills_from_job(job: Dict[str, Any]) -> List[str]:
    """Extract skills from a job posting"""
    skills = set()

    # Extract from title
    if job.get('title'):
        title_skills = extract_skills_from_text(job['title'])
        skills.update(title_skills)

    # Extract from description
    if job.get('description'):
        desc_skills = extract_skills_from_text(job['description'])
        skills.update(desc_skills)

    # Extract from categories if available
    if job.get('categories'):
        for category in job['categories']:
            cat_skills = extract_skills_from_text(category)
            skills.update(cat_skills)

    # If we have an application link, try to scrape more details
    if job.get('applicationLink') and len(skills) < 5:
        try:
            # Add a small delay to be respectful
            time.sleep(0.5)
            scraped_description = scrape_job_description(job['applicationLink'])
            if scraped_description:
                scraped_skills = extract_skills_from_text(scraped_description)
                skills.update(scraped_skills)
        except Exception as e:
            logger.warning(f"Failed to scrape additional skills: {e}")

    return sorted(list(skills))

def analyze_skills_demand(jobs: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze skill demand across multiple jobs"""
    skill_count = {}

    for job in jobs:
        job_skills = extract_skills_from_job(job)
        for skill in job_skills:
            skill_count[skill] = skill_count.get(skill, 0) + 1

    # Sort by frequency
    return dict(sorted(skill_count.items(), key=lambda x: x[1], reverse=True))

def get_skill_recommendations(job_skills: List[str], market_skills: Dict[str, int]) -> List[str]:
    """Get skill recommendations based on job requirements and market demand"""
    recommendations = []

    # Skills that appear in job but user might want to learn more about
    job_skill_set = set(skill.lower() for skill in job_skills)

    # Related skills mapping
    skill_relationships = {
        'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy'],
        'javascript': ['react', 'vue', 'angular', 'node.js', 'typescript'],
        'react': ['redux', 'next.js', 'typescript', 'testing-library'],
        'aws': ['docker', 'kubernetes', 'terraform', 'lambda'],
        'docker': ['kubernetes', 'jenkins', 'terraform'],
        'sql': ['postgresql', 'mysql', 'database design'],
        'machine learning': ['python', 'tensorflow', 'pytorch', 'pandas']
    }

    # Find related skills
    for skill in job_skills:
        if skill.lower() in skill_relationships:
            related = skill_relationships[skill.lower()]
            for related_skill in related:
                if related_skill not in job_skill_set and related_skill in market_skills:
                    recommendations.append(related_skill)

    # Add high-demand skills not in job requirements
    for skill, count in list(market_skills.items())[:10]:
        if skill not in job_skill_set and count > 1:
            recommendations.append(skill)

    return list(set(recommendations))[:5]  # Return top 5 unique recommendations
