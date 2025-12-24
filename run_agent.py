#!/usr/bin/env python3
"""
Job Search Agent - Main Runner
- Tracks when jobs were first seen (date_added)
- Marks jobs as NEW if added in last 48 hours
- Removes jobs that are no longer posted
"""

import json
import os
from datetime import datetime, timedelta

from scrape_greenhouse import scrape_all_greenhouse
from scrape_lever import scrape_all_lever

try:
    from scrape_ashby import scrape_all_ashby
    HAS_ASHBY = True
except ImportError:
    HAS_ASHBY = False

JOBS_FILE = "all_jobs.json"

def load_existing_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

def create_job_key(job):
    return f"{job.get('company', '')}|{job.get('title', '')}|{job.get('job_id', '')}"

def merge_jobs(existing_jobs, new_jobs):
    now = datetime.now()
    cutoff = now - timedelta(hours=48)
    
    existing_lookup = {}
    for job in existing_jobs:
        key = create_job_key(job)
        existing_lookup[key] = job
    
    new_lookup = {}
    for job in new_jobs:
        key = create_job_key(job)
        new_lookup[key] = job
    
    merged = []
    new_count = 0
    kept_count = 0
    removed_count = 0
    
    for key, job in new_lookup.items():
        if key in existing_lookup:
            old_job = existing_lookup[key]
            job['date_added'] = old_job.get('date_added', now.isoformat())
            job['status'] = old_job.get('status', 'new')
            kept_count += 1
        else:
            job['date_added'] = now.isoformat()
            job['status'] = 'new'
            new_count += 1
        
        try:
            added_date = datetime.fromisoformat(job['date_added'])
            job['is_new'] = added_date > cutoff
        except:
            job['is_new'] = True
        
        merged.append(job)
    
    for key in existing_lookup:
        if key not in new_lookup:
            removed_count += 1
    
    print(f"   📊 Jobs: {len(merged)} active ({new_count} new, {kept_count} existing, {removed_count} removed)")
    
    return merged, new_count

def run_scraper():
    print(f"\n{'='*60}")
    print(f"🔍 JOB SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    existing_jobs = load_existing_jobs()
    print(f"📂 Loaded {len(existing_jobs)} existing jobs\n")
    
    all_new_jobs = []
    
    print("🌱 Scraping Greenhouse...")
    try:
        greenhouse_jobs = scrape_all_greenhouse(verbose=True)
        all_new_jobs.extend(greenhouse_jobs)
        print(f"   Total: {len(greenhouse_jobs)} jobs\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    print("🎯 Scraping Lever...")
    try:
        lever_jobs = scrape_all_lever(verbose=True)
        all_new_jobs.extend(lever_jobs)
        print(f"   Total: {len(lever_jobs)} jobs\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    if HAS_ASHBY:
        print("🏢 Scraping Ashby...")
        try:
            ashby_jobs = scrape_all_ashby(verbose=True)
            all_new_jobs.extend(ashby_jobs)
            print(f"   Total: {len(ashby_jobs)} jobs\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    relevant_jobs = [j for j in all_new_jobs if j.get('relevant', False)]
    print(f"📋 Relevant (entry-level) jobs: {len(relevant_jobs)}")
    
    print("\n🔄 Merging with existing jobs...")
    merged_jobs, new_count = merge_jobs(existing_jobs, relevant_jobs)
    
    merged_jobs.sort(key=lambda j: (
        j.get('tier', 3),
        not j.get('is_new', False),
        j.get('company', '')
    ))
    
    save_jobs(merged_jobs)
    print(f"\n✅ Saved {len(merged_jobs)} jobs to {JOBS_FILE}")
    
    new_jobs = [j for j in merged_jobs if j.get('is_new', False)]
    if new_jobs:
        print(f"\n🆕 NEW JOBS (last 48 hours): {len(new_jobs)}")
        for job in new_jobs[:10]:
            print(f"   • {job['title'][:45]} @ {job['company']}")
    
    return merged_jobs, new_count

if __name__ == "__main__":
    jobs, new_count = run_scraper()
    print(f"\n🎉 Done! {new_count} new jobs found.")
