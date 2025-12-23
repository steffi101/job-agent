# scrape_lever.py - Scrape jobs directly from Lever job boards

import requests
import re
import time
from config import classify_company

LEVER_COMPANIES = {
    'wealthfront': 'Wealthfront', 'betterment': 'Betterment', 'pipe': 'Pipe',
    'netlify': 'Netlify', 'supabase': 'Supabase', 'planetscale': 'PlanetScale',
    'railway': 'Railway', 'render': 'Render', 'replit': 'Replit',
    'benchling': 'Benchling', 'astranis': 'Astranis', 'anduril': 'Anduril',
    'relativity': 'Relativity Space', 'zipline': 'Zipline', 'nuro': 'Nuro',
    'aurora': 'Aurora', 'cruise': 'Cruise', 'calm': 'Calm',
    'duolingo': 'Duolingo', 'masterclass': 'MasterClass', 'substack': 'Substack',
    'medium': 'Medium', 'patreon': 'Patreon',
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

def fetch_lever_jobs(company_slug, company_name=None):
    if company_name is None:
        company_name = company_slug.title()
    url = f"https://api.lever.co/v0/postings/{company_slug}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return []
        jobs = []
        for job in response.json():
            title = job.get('text', '')
            categories = job.get('categories', {})
            location = categories.get('location', 'Unknown')
            job_url = job.get('hostedUrl', '')
            job_id = job.get('id', '')
            
            if is_intern(title):
                continue
            
            # Build description text
            description = job.get('descriptionPlain', '') or ''
            lists = job.get('lists', [])
            for lst in lists:
                description += ' ' + lst.get('text', '') + ' '
                content = lst.get('content', '')
                if isinstance(content, list):
                    description += ' '.join(content)
                elif isinstance(content, str):
                    description += content
            
            if is_senior_title(title):
                is_entry = False
                years = None
            else:
                is_entry, years = check_years_experience(description)
                
                if is_entry and is_manager_title(title) and years is None:
                    is_entry = False
            
            jobs.append({
                'title': title, 
                'company': company_name, 
                'location': location,
                'url': job_url, 
                'job_id': str(job_id), 
                'source': 'lever',
                'tier': classify_company(company_name), 
                'relevant': is_entry,
                'years_required': years,
            })
        return jobs
    except Exception as e:
        print(f"   Error fetching {company_slug}: {e}")
        return []

def scrape_all_lever(companies=None, verbose=True):
    if companies is None:
        companies = LEVER_COMPANIES
    all_jobs = []
    for slug, name in companies.items():
        if verbose:
            print(f"   Fetching {name}...", end=' ', flush=True)
        jobs = fetch_lever_jobs(slug, name)
        if verbose:
            entry_level = [j for j in jobs if j.get('relevant')]
            print(f"found {len(jobs)} jobs ({len(entry_level)} entry-level ≤2yrs)")
        all_jobs.extend(jobs)
        time.sleep(0.1)
    return all_jobs

if __name__ == '__main__':
    print("Testing Lever scraper...")
    jobs = scrape_all_lever({'duolingo': 'Duolingo'})
    entry = [j for j in jobs if j.get('relevant')]
    print(f"\nTotal: {len(jobs)} jobs, Entry-level: {len(entry)}")
