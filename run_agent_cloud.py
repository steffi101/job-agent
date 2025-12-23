#!/usr/bin/env python3
# run_agent_cloud.py - Cloud version for GitHub Actions

import os
import sys
from datetime import datetime
from scrape_greenhouse import scrape_all_greenhouse, GREENHOUSE_COMPANIES
from scrape_lever import scrape_all_lever, LEVER_COMPANIES
from notifier import send_job_alert

# Override password from environment
import notifier
notifier.SENDER_PASSWORD = os.environ.get('GMAIL_PASSWORD', '')

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
        'palo alto', 'mountain view', 'bay area',
    ]
    for indicator in us_indicators:
        if indicator in location_lower:
            return True
    return False

def run():
    print(f"\n{'='*60}")
    print(f"🤖 Job Agent (Cloud) - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    all_jobs = []
    
    print(f"🌱 Scraping Greenhouse ({len(GREENHOUSE_COMPANIES)} companies)...")
    greenhouse_jobs = scrape_all_greenhouse(verbose=False)
    all_jobs.extend(greenhouse_jobs)
    print(f"   Found {len(greenhouse_jobs)} jobs")
    
    print(f"🎯 Scraping Lever ({len(LEVER_COMPANIES)} companies)...")
    lever_jobs = scrape_all_lever(verbose=False)
    all_jobs.extend(lever_jobs)
    print(f"   Found {len(lever_jobs)} jobs")
    
    # Filter
    entry_jobs = [j for j in all_jobs if j.get('relevant')]
    us_jobs = [j for j in entry_jobs if is_us_location(j.get('location', ''))]
    
    print(f"\n📊 Results:")
    print(f"   Total scraped: {len(all_jobs)}")
    print(f"   Entry-level (≤2yr): {len(entry_jobs)}")
    print(f"   US-based: {len(us_jobs)}")
    
    if us_jobs:
        # Sort jobs
        for job in us_jobs:
            job['role_priority'] = get_role_priority(job['title'])
        us_jobs.sort(key=lambda j: (j.get('tier', 3), j.get('role_priority', 6)))
        
        print(f"\n📧 Sending email with {len(us_jobs)} jobs...")
        send_job_alert(us_jobs, [])
    else:
        print(f"\n😴 No jobs found.")
    
    print(f"\n✅ Done!")

if __name__ == '__main__':
    run()
