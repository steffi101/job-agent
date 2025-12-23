# scrape_ashby.py - Scrape jobs from Ashby job boards

import requests
import re
import time
from config import classify_company

# Companies using Ashby
ASHBY_COMPANIES = {
    'plaid': 'Plaid',
    'openai': 'OpenAI', 
    'ramp': 'Ramp',
    'notion': 'Notion',
    'linear': 'Linear',
    'mercury': 'Mercury',
    'replo': 'Replo',
    'resend': 'Resend',
}

def check_years_experience(text):
    if not text:
        return True, None
    text_lower = text.lower()
    patterns = [
        r'(\d+)\+?\s*(?:to|\-|–)?\s*\d*\s*years?\s*(?:of)?\s*(?:experience|exp)',
        r'(\d+)\+?\s*years?\s*(?:of)?\s*(?:experience|exp|work)',
        r'(\d+)\+\s*years',
        r'minimum\s*(?:of)?\s*(\d+)\s*years?',
        r'at\s*least\s*(\d+)\s*years?',
        r'(\d+)\-\d+\s*years',
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
        'iii', 'iv', ' v ', 'level 3', 'level 4', 'level 5',
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

def fetch_ashby_jobs(company_slug, company_name=None):
    if company_name is None:
        company_name = company_slug.title()
    
    url = f"https://api.ashbyhq.com/posting-api/job-board/{company_slug}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        jobs_data = data.get('jobs', [])
        
        jobs = []
        for job in jobs_data:
            title = job.get('title', '')
            location = job.get('location', 'Unknown')
            job_id = job.get('id', '')
            job_url = job.get('jobUrl', f"https://jobs.ashbyhq.com/{company_slug}/{job_id}")
            description = job.get('descriptionPlain', '') or ''
            
            if is_intern(title):
                continue
            
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
                'source': 'ashby',
                'tier': classify_company(company_name),
                'relevant': is_entry,
                'years_required': years,
            })
        
        return jobs
    except Exception as e:
        return []

def scrape_all_ashby(companies=None, verbose=True):
    if companies is None:
        companies = ASHBY_COMPANIES
    all_jobs = []
    for slug, name in companies.items():
        if verbose:
            print(f"   {name}...", end=' ', flush=True)
        jobs = fetch_ashby_jobs(slug, name)
        if jobs:
            entry_level = [j for j in jobs if j.get('relevant')]
            if verbose:
                print(f"{len(jobs)} jobs ({len(entry_level)} entry-level)")
        else:
            if verbose:
                print(f"skipped")
        all_jobs.extend(jobs)
        time.sleep(0.1)
    return all_jobs

if __name__ == '__main__':
    print("Testing Ashby scraper...")
    jobs = scrape_all_ashby({'plaid': 'Plaid', 'openai': 'OpenAI'})
    entry = [j for j in jobs if j.get('relevant')]
    print(f"\nTotal: {len(jobs)} jobs, Entry-level: {len(entry)}")
