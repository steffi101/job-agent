#!/usr/bin/env python3
# run_agent_cloud.py - Cloud version for GitHub Actions

import os
import json
from datetime import datetime
from scrape_greenhouse import scrape_all_greenhouse, GREENHOUSE_COMPANIES
from scrape_lever import scrape_all_lever, LEVER_COMPANIES
from scrape_ashby import scrape_all_ashby, ASHBY_COMPANIES
from notifier import send_job_alert

import notifier
notifier.SENDER_PASSWORD = os.environ.get('GMAIL_PASSWORD', '')

JOBS_FILE = 'all_jobs.json'

def get_role_priority(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm', 'associate product']):
        return 1
    elif any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm', 'technical program']):
        return 2
    elif any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist', 'business analyst']):
        return 3
    elif any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing', 'growth']):
        return 4
    elif any(kw in title_lower for kw in ['research', 'ai safety', 'policy', 'trust']):
        return 5
    return 6

def get_role_category(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm', 'associate product']):
        return "🎯 Product Manager"
    if any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm', 'technical program']):
        return "📋 Program/Project Manager"
    if any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist', 'business analyst']):
        return "📊 Data/Analytics"
    if any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing', 'growth']):
        return "📈 Ops/GTM/Marketing"
    if any(kw in title_lower for kw in ['research', 'ai safety', 'policy', 'trust']):
        return "🔬 Research/AI Safety"
    if any(kw in title_lower for kw in ['solutions engineer', 'sales engineer']):
        return "🔧 Solutions/Sales Eng"
    if any(kw in title_lower for kw in ['software engineer', 'backend', 'frontend', 'developer']):
        return "💻 Software Engineering"
    if any(kw in title_lower for kw in ['engineer', 'infrastructure', 'sre', 'devops']):
        return "⚙️ Other Engineering"
    if any(kw in title_lower for kw in ['recruiter', 'hr ', 'talent', 'coordinator']):
        return "👥 HR/Recruiting"
    return "📁 Other"

def is_us_location(location):
    if not location:
        return False
    location_lower = location.lower().strip()
    
    non_us = [
        'spain', 'poland', 'uk', 'united kingdom', 'canada', 'germany', 
        'france', 'india', 'singapore', 'japan', 'australia', 'brazil',
        'mexico', 'ireland', 'netherlands', 'sweden', 'israel', 'china',
        'london', 'toronto', 'vancouver', 'berlin', 'paris', 'dublin',
        'sydney', 'melbourne', 'bangalore', 'mumbai', 'tel aviv', 'tokyo',
        ', uk', ', ca,', 'ontario', 'emea', 'apac', 'latam',
    ]
    for non in non_us:
        if non in location_lower:
            return False
    
    us_indicators = [
        'united states', 'usa', 'u.s.', ', us', '- us', 'remote - us',
        'remote us', '(us)', 'remote, us', 'california', 'new york', 
        'texas', 'washington', 'colorado', 'massachusetts', 'illinois',
        'san francisco', 'nyc', 'seattle', 'austin', 'boston', 
        'los angeles', 'chicago', 'denver', 'atlanta', 'miami',
        'palo alto', 'mountain view', 'bay area', 'remote',
    ]
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

def run():
    print(f"\n{'='*60}")
    print(f"🤖 Job Agent (Cloud) - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    all_jobs = []
    
    # Greenhouse
    print(f"🌱 Scraping Greenhouse ({len(GREENHOUSE_COMPANIES)} companies)...")
    greenhouse_jobs = scrape_all_greenhouse(verbose=False)
    all_jobs.extend(greenhouse_jobs)
    print(f"   Found {len(greenhouse_jobs)} jobs")
    
    # Lever
    print(f"🎯 Scraping Lever ({len(LEVER_COMPANIES)} companies)...")
    lever_jobs = scrape_all_lever(verbose=False)
    all_jobs.extend(lever_jobs)
    print(f"   Found {len(lever_jobs)} jobs")
    
    # Ashby (Plaid, OpenAI, Ramp, Notion, etc.)
    print(f"🔷 Scraping Ashby ({len(ASHBY_COMPANIES)} companies)...")
    ashby_jobs = scrape_all_ashby(verbose=False)
    all_jobs.extend(ashby_jobs)
    print(f"   Found {len(ashby_jobs)} jobs")
    
    # Filter
    entry_jobs = [j for j in all_jobs if j.get('relevant')]
    us_jobs = [j for j in entry_jobs if is_us_location(j.get('location', ''))]
    
    # Load existing jobs
    existing_jobs = load_existing_jobs()
    existing_urls = {j.get('url'): j for j in existing_jobs}
    
    # Find new jobs
    new_jobs = []
    for job in us_jobs:
        if job.get('url') not in existing_urls:
            job['status'] = 'New'
            job['added_date'] = datetime.now().isoformat()
            job['role_category'] = get_role_category(job['title'])
            new_jobs.append(job)
    
    # Merge jobs
    all_saved_jobs = existing_jobs.copy()
    all_saved_jobs.extend(new_jobs)
    
    # Save for Streamlit
    save_all_jobs(all_saved_jobs)
    
    print(f"\n📊 Results:")
    print(f"   Total scraped: {len(all_jobs)}")
    print(f"   Entry-level (≤2yr): {len(entry_jobs)}")
    print(f"   US-based: {len(us_jobs)}")
    print(f"   NEW jobs: {len(new_jobs)}")
    print(f"   Total saved: {len(all_saved_jobs)}")
    
    if new_jobs:
        for job in new_jobs:
            job['role_priority'] = get_role_priority(job['title'])
        new_jobs.sort(key=lambda j: (j.get('tier', 3), j.get('role_priority', 6)))
        
        print(f"\n🆕 New Jobs:")
        for job in new_jobs[:5]:
            print(f"   • {job['title'][:40]} @ {job['company']}")
        
        print(f"\n📧 Sending email...")
        send_job_alert(new_jobs, [])
    else:
        print(f"\n😴 No new jobs.")
    
    print(f"\n✅ Done!")

if __name__ == '__main__':
    run()
