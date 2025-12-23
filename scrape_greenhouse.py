# scrape_greenhouse.py - Scrape jobs directly from Greenhouse job boards

import requests
import re
import time
from config import classify_company

GREENHOUSE_COMPANIES = {
    # FAANG + Big Tech
    'meta': 'Meta',
    'netflix': 'Netflix',
    'apple': 'Apple',
    'microsoft': 'Microsoft',
    'google': 'Google',
    'amazon': 'Amazon',
    'nvidia': 'NVIDIA',
    'salesforce': 'Salesforce',
    'adobe': 'Adobe',
    'oracle': 'Oracle',
    'uber': 'Uber',
    'lyft': 'Lyft',
    'tiktok': 'TikTok',
    'bytedance': 'ByteDance',
    'linkedin': 'LinkedIn',
    'reddit': 'Reddit',
    'snap': 'Snap',
    'pinterest': 'Pinterest',
    'spotify': 'Spotify',
    
    # AI / AI Safety
    'anthropic': 'Anthropic', 
    'openai': 'OpenAI', 
    'deepmind': 'DeepMind',
    'cohere': 'Cohere', 
    'scaleai': 'Scale AI', 
    'huggingface': 'Hugging Face',
    'stability': 'Stability AI', 
    'adept': 'Adept', 
    'inflectionai': 'Inflection AI',
    'character': 'Character.AI', 
    'perplexityai': 'Perplexity', 
    'runwayml': 'Runway',
    
    # Fintech
    'stripe': 'Stripe', 
    'plaid': 'Plaid', 
    'brex': 'Brex', 
    'ramp': 'Ramp',
    'coinbase': 'Coinbase', 
    'robinhood': 'Robinhood', 
    'chime': 'Chime',
    'affirm': 'Affirm', 
    'sofi': 'SoFi', 
    'mercury': 'Mercury', 
    'rippling': 'Rippling',
    'moderntreasury': 'Modern Treasury', 
    'marqeta': 'Marqeta',
    'anchorage': 'Anchorage Digital', 
    'circle': 'Circle', 
    'fireblocks': 'Fireblocks',
    'chainalysis': 'Chainalysis', 
    'alchemy': 'Alchemy',
    'block': 'Block (Square)',
    
    # Consumer Tech
    'airbnb': 'Airbnb', 
    'doordash': 'DoorDash', 
    'instacart': 'Instacart',
    'discord': 'Discord',
    'notion': 'Notion', 
    'figma': 'Figma', 
    'canva': 'Canva',
    'airtable': 'Airtable', 
    'asana': 'Asana', 
    'dropbox': 'Dropbox',
    'slack': 'Slack',
    'zoom': 'Zoom',
    
    # Enterprise / B2B
    'databricks': 'Databricks', 
    'snowflakecomputing': 'Snowflake', 
    'datadog': 'Datadog',
    'mongodb': 'MongoDB', 
    'elastic': 'Elastic', 
    'hashicorp': 'HashiCorp',
    'cloudflare': 'Cloudflare', 
    'twilio': 'Twilio', 
    'okta': 'Okta',
    'crowdstrike': 'CrowdStrike', 
    'confluent': 'Confluent', 
    'daboratories': 'dbt Labs',
    'fivetran': 'Fivetran', 
    'palantir': 'Palantir',
    
    # Other Tech
    'shopify': 'Shopify', 
    'squarespace': 'Squarespace',
    'webflow': 'Webflow', 
    'vercel': 'Vercel', 
    'netlify': 'Netlify',
    'gitlab': 'GitLab', 
    'postman': 'Postman', 
    'linear': 'Linear',
    'retool': 'Retool', 
    'amplitude': 'Amplitude', 
    'mixpanel': 'Mixpanel',
}

def check_years_experience(text):
    """Check job description for years of experience required."""
    if not text:
        return True, None
    
    text_lower = text.lower()
    
    patterns = [
        r'(\d+)\+?\s*(?:to|\-|–)?\s*\d*\s*years?\s*(?:of)?\s*(?:experience|exp)',
        r'(\d+)\+?\s*years?\s*(?:of)?\s*(?:experience|exp|work)',
        r'(\d+)\+?\s*yrs?\s*(?:of)?\s*(?:experience|exp)',
        r'(\d+)\+\s*years',
        r'(\d+)\s*\+\s*years',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'minimum\s*(?:of)?\s*(\d+)\s*years?',
        r'at\s*least\s*(\d+)\s*years?',
        r'(\d+)\+?\s*years?\s*(?:in|of|working)',
        r'(\d+)\+?\s*years?\s*(?:product|engineering|software|data|program)',
        r'(\d+)\+?\s*years?\s*(?:professional|relevant|related)',
        r'(\d+)\-\d+\s*years',
        r'(\d+)\s*to\s*\d+\s*years',
    ]
    
    max_years = 0
    found_years = False
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                years = int(match)
                if years > 20:
                    continue
                found_years = True
                if years > max_years:
                    max_years = years
            except:
                pass
    
    if not found_years:
        return True, None
    
    return max_years <= 2, max_years

def is_senior_title(title):
    title_lower = title.lower()
    senior_indicators = [
        'senior', 'sr.', 'sr ', 'staff', 'principal', 'lead', 'head of',
        'director', 'vp', 'vice president', 'chief', 'cto', 'cfo', 'ceo',
        'architect', 'distinguished', 'fellow', 'executive', 'partner',
        'iii', 'iv', ' v ', 'level 3', 'level 4', 'level 5', 'level 6',
        'l3', 'l4', 'l5', 'l6', 'l7', 
    ]
    for indicator in senior_indicators:
        if indicator in title_lower:
            return True
    return False

def is_intern(title):
    return 'intern' in title.lower()

def is_manager_title(title):
    title_lower = title.lower()
    if 'manager' in title_lower:
        if any(x in title_lower for x in ['associate', 'junior', 'assistant', 'apm', 'i ', ' i,', ' 1']):
            return False
        return True
    return False

def fetch_greenhouse_jobs(company_slug, company_name=None):
    if company_name is None:
        company_name = company_slug.title()
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true"
    try:
        response = requests.get(url, timeout=30)  # Increased timeout
        if response.status_code != 200:
            return []
        data = response.json()
        jobs = []
        for job in data.get('jobs', []):
            title = job.get('title', '')
            location = job.get('location', {}).get('name', 'Unknown')
            job_id = job.get('id')
            job_url = job.get('absolute_url') or f"https://boards.greenhouse.io/{company_slug}/jobs/{job_id}"
            
            if is_intern(title):
                continue
            
            if is_senior_title(title):
                is_entry = False
                years = None
            else:
                content = job.get('content', '')
                is_entry, years = check_years_experience(content)
                
                if is_entry and is_manager_title(title) and years is None:
                    is_entry = False
            
            jobs.append({
                'title': title, 
                'company': company_name, 
                'location': location,
                'url': job_url, 
                'job_id': str(job_id), 
                'source': 'greenhouse',
                'tier': classify_company(company_name), 
                'relevant': is_entry,
                'years_required': years,
            })
        return jobs
    except Exception as e:
        # Don't print full error, just note it failed
        return []

def scrape_all_greenhouse(companies=None, verbose=True):
    if companies is None:
        companies = GREENHOUSE_COMPANIES
    all_jobs = []
    failed = []
    for slug, name in companies.items():
        if verbose:
            print(f"   {name}...", end=' ', flush=True)
        jobs = fetch_greenhouse_jobs(slug, name)
        if jobs:
            entry_level = [j for j in jobs if j.get('relevant')]
            if verbose:
                print(f"{len(jobs)} jobs ({len(entry_level)} entry-level)")
        else:
            if verbose:
                print(f"skipped")
            failed.append(name)
        all_jobs.extend(jobs)
        time.sleep(0.05)  # Faster
    if failed and verbose:
        print(f"   ⚠️  Could not reach: {', '.join(failed[:5])}{'...' if len(failed) > 5 else ''}")
    return all_jobs

if __name__ == '__main__':
    print("Testing Greenhouse scraper...")
    jobs = scrape_all_greenhouse({'anthropic': 'Anthropic', 'stripe': 'Stripe'})
    entry = [j for j in jobs if j.get('relevant')]
    print(f"\nTotal: {len(jobs)} jobs, Entry-level: {len(entry)}")
