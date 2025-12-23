#!/usr/bin/env python3
# run_agent.py - Run job scraper locally

import sys
import json
import os
from datetime import datetime
from scrape_greenhouse import scrape_all_greenhouse, GREENHOUSE_COMPANIES
from scrape_lever import scrape_all_lever, LEVER_COMPANIES
from scrape_ashby import scrape_all_ashby, ASHBY_COMPANIES
from database import filter_new_jobs
from notifier import send_job_alert

JOBS_FILE = 'all_jobs.json'

def get_role_priority(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm']):
        return 1
    elif any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm']):
        return 2
    elif any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist']):
        return 3
    elif any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing']):
        return 4
    elif any(kw in title_lower for kw in ['research', 'ai safety', 'policy']):
        return 5
    return 6

def get_role_category(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm']):
        return "🎯 Product Manager"
    if any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm']):
        return "📋 Program/Project Manager"
    if any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist']):
        return "📊 Data/Analytics"
    if any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing']):
        return "📈 Ops/GTM/Marketing"
    if any(kw in title_lower for kw in ['research', 'ai safety', 'policy']):
        return "🔬 Research/AI Safety"
    if any(kw in title_lower for kw in ['solutions engineer', 'sales engineer']):
        return "🔧 Solutions/Sales Eng"
    if any(kw in title_lower for kw in ['software engineer', 'backend', 'frontend']):
        return "💻 Software Engineering"
    if any(kw in title_lower for kw in ['engineer', 'infrastructure', 'sre']):
        return "⚙️ Other Engineering"
    if any(kw in title_lower for kw in ['recruiter', 'hr ', 'talent']):
        return "👥 HR/Recruiting"
    return "📁 Other"

def is_us_location(location):
    if not location:
        return False
    location_lower = location.lower().strip()
    non_us = ['spain', 'poland', 'uk', 'canada', 'germany', 'france', 'india', 
              'singapore', 'japan', 'australia', 'london', 'toronto', 'berlin',
              'emea', 'apac', 'latam']
    for non in non_us:
        if non in location_lower:
            return False
    us_indicators = ['united states', 'usa', ', us', 'remote', 'california', 
                     'new york', 'texas', 'san francisco', 'seattle', 'boston',
                     'austin', 'denver', 'chicago', 'los angeles', 'bay area']
    for indicator in us_indicators:
        if indicator in location_lower:
            return True
    return False

def load_existing_jobs():
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_all_jobs(jobs):
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2, default=str)

def run_and_notify(send_email=True):
    print(f"\n{'='*60}")
    print(f"🤖 Job Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    all_jobs = []
    
    print(f"🌱 Greenhouse ({len(GREENHOUSE_COMPANIES)} companies)...")
    all_jobs.extend(scrape_all_greenhouse(verbose=False))
    
    print(f"🎯 Lever ({len(LEVER_COMPANIES)} companies)...")
    all_jobs.extend(scrape_all_lever(verbose=False))
    
    print(f"🔷 Ashby ({len(ASHBY_COMPANIES)} companies)...")
    all_jobs.extend(scrape_all_ashby(verbose=False))
    
    entry_jobs = [j for j in all_jobs if j.get('relevant')]
    us_jobs = [j for j in entry_jobs if is_us_location(j.get('location', ''))]
    
    existing_jobs = load_existing_jobs()
    existing_urls = {j.get('url'): j for j in existing_jobs}
    
    new_jobs = []
    for job in us_jobs:
        if job.get('url') not in existing_urls:
            job['status'] = 'New'
            job['added_date'] = datetime.now().isoformat()
            job['role_category'] = get_role_category(job['title'])
            new_jobs.append(job)
    
    all_saved_jobs = existing_jobs + new_jobs
    save_all_jobs(all_saved_jobs)
    
    print(f"\n📊 Results: {len(all_jobs)} scraped → {len(entry_jobs)} entry-level → {len(us_jobs)} US → {len(new_jobs)} NEW")
    
    if new_jobs and send_email:
        new_jobs.sort(key=lambda j: (j.get('tier', 3), get_role_priority(j['title'])))
        send_job_alert(new_jobs, [])
    
    print(f"✅ Done! Total saved: {len(all_saved_jobs)}")

if __name__ == '__main__':
    run_and_notify(send_email='--no-email' not in sys.argv)
