#!/usr/bin/env python3
# run_agent.py - Run job scraper and send email alerts

import sys
import json
import os
from datetime import datetime
from scrape_greenhouse import scrape_all_greenhouse, GREENHOUSE_COMPANIES
from scrape_lever import scrape_all_lever, LEVER_COMPANIES
from database import filter_new_jobs, get_job_stats, load_database
from notifier import send_job_alert

OLD_JOBS_FILE = 'old_jobs.json'

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

def load_old_jobs():
    """Load previously seen jobs"""
    if os.path.exists(OLD_JOBS_FILE):
        try:
            with open(OLD_JOBS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_old_jobs(jobs):
    """Save jobs for next run"""
    # Keep only essential fields to save space
    minimal_jobs = []
    for job in jobs:
        minimal_jobs.append({
            'title': job.get('title'),
            'company': job.get('company'),
            'location': job.get('location'),
            'url': job.get('url'),
            'tier': job.get('tier'),
        })
    with open(OLD_JOBS_FILE, 'w') as f:
        json.dump(minimal_jobs, f)

def run_and_notify(send_email=True, verbose=True):
    """Run scraper and send email"""
    
    print(f"\n{'='*60}")
    print(f"🤖 Job Agent Running - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
    
    # Get new vs old
    new_jobs = filter_new_jobs(us_jobs.copy())
    
    # Load previously saved old jobs
    old_jobs = load_old_jobs()
    
    print(f"\n📊 Results:")
    print(f"   Total scraped: {len(all_jobs)}")
    print(f"   Entry-level (≤2yr): {len(entry_jobs)}")
    print(f"   US-based: {len(us_jobs)}")
    print(f"   NEW jobs: {len(new_jobs)}")
    print(f"   Previously seen: {len(old_jobs)}")
    
    # Sort jobs
    for job in new_jobs:
        job['role_priority'] = get_role_priority(job['title'])
    new_jobs.sort(key=lambda j: (j.get('tier', 3), j.get('role_priority', 6)))
    
    for job in old_jobs:
        job['role_priority'] = get_role_priority(job['title'])
    old_jobs.sort(key=lambda j: (j.get('tier', 3), j.get('role_priority', 6)))
    
    if new_jobs:
        print(f"\n🆕 Top New Jobs:")
        for job in new_jobs[:5]:
            print(f"   • {job['title'][:40]} @ {job['company']}")
        if len(new_jobs) > 5:
            print(f"   ... and {len(new_jobs) - 5} more")
    
    # Send email
    if send_email and (new_jobs or old_jobs):
        print(f"\n📧 Sending email alert...")
        send_job_alert(new_jobs, old_jobs)
    elif not new_jobs:
        print(f"\n😴 No new jobs since last run.")
    
    # Save current US jobs as "old" for next run
    save_old_jobs(us_jobs)
    
    print(f"\n✅ Done!")
    return new_jobs

if __name__ == '__main__':
    send_email = '--no-email' not in sys.argv
    run_and_notify(send_email=send_email)
