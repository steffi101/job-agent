#!/usr/bin/env python3
# main.py - Job Search Agent Orchestrator

import os
import sys
import re
from datetime import datetime

from auth import get_gmail_service, test_connection
from fetch_emails import get_job_alert_emails
from database import filter_new_jobs, get_job_stats
from config import classify_company, is_relevant_title


def extract_google_jobs(email):
    """Extract jobs from Google Careers emails"""
    jobs = []
    links = email.get('links', [])
    
    google_job_pattern = r'google\.com/about/careers/applications/jobs/results/(\d+)'
    
    seen_ids = set()
    for link in links:
        match = re.search(google_job_pattern, link)
        if match:
            job_id = match.group(1)
            if job_id not in seen_ids:
                seen_ids.add(job_id)
                clean_url = f"https://www.google.com/about/careers/applications/jobs/results/{job_id}"
                jobs.append({
                    'title': 'Google Job Opening',
                    'company': 'Google',
                    'location': 'United States',
                    'url': clean_url,
                    'source': 'google_careers',
                    'tier': 1,
                    'relevant': True,
                })
    return jobs


def extract_linkedin_jobs(email):
    """Extract jobs from LinkedIn emails"""
    jobs = []
    links = email.get('links', [])
    
    linkedin_pattern = r'linkedin\.com/(?:comm/)?jobs/view/(\d+)'
    
    seen_ids = set()
    for link in links:
        match = re.search(linkedin_pattern, link)
        if match:
            job_id = match.group(1)
            if job_id not in seen_ids:
                seen_ids.add(job_id)
                jobs.append({
                    'title': 'LinkedIn Job',
                    'company': 'Unknown',
                    'location': 'Unknown',
                    'url': f'https://www.linkedin.com/jobs/view/{job_id}',
                    'source': 'linkedin',
                    'tier': 3,
                    'relevant': True,
                })
    return jobs


def extract_generic_jobs(email):
    """Extract jobs from any email with job board links"""
    jobs = []
    links = email.get('links', [])
    
    job_patterns = {
        'greenhouse': (r'(boards\.greenhouse\.io/(\w+)/jobs/\d+)', 2),
        'lever': (r'(jobs\.lever\.co/([\w-]+)/[\w-]+)', 2),
        'ashby': (r'(jobs\.ashbyhq\.com/([\w-]+)/[\w-]+)', 2),
    }
    
    seen_urls = set()
    for link in links:
        # Skip images and assets
        if any(ext in link.lower() for ext in ['.png', '.jpg', '.gif', '.css']):
            continue
            
        for platform, (pattern, company_group) in job_patterns.items():
            match = re.search(pattern, link, re.IGNORECASE)
            if match:
                url = match.group(1)
                if not url.startswith('http'):
                    url = 'https://' + url
                    
                if url not in seen_urls:
                    seen_urls.add(url)
                    company = match.group(company_group).replace('-', ' ').title()
                    jobs.append({
                        'title': f'{platform.title()} Job',
                        'company': company,
                        'location': 'Unknown',
                        'url': url,
                        'source': platform,
                        'tier': classify_company(company),
                        'relevant': True,
                    })
                break
    
    return jobs


def process_email(email):
    """Process a single email and extract jobs"""
    jobs = []
    sender = email.get('sender', '').lower()
    subject = email.get('subject', '').lower()
    
    print(f"   Processing: {subject[:50]}...")
    print(f"   From: {sender[:50]}")
    print(f"   Links found: {len(email.get('links', []))}")
    
    # Route to appropriate extractor
    if 'google' in sender or 'careers-noreply@google' in sender:
        jobs = extract_google_jobs(email)
        print(f"   → Google parser found {len(jobs)} jobs")
    
    elif 'linkedin' in sender:
        jobs = extract_linkedin_jobs(email)
        print(f"   → LinkedIn parser found {len(jobs)} jobs")
    
    elif 'fpsb' in sender.lower() or 'india' in sender.lower():
        print(f"   → Skipping (India-based)")
        return []
    
    else:
        jobs = extract_generic_jobs(email)
        print(f"   → Generic parser found {len(jobs)} jobs")
    
    return jobs


def prioritize_jobs(jobs):
    """Sort jobs by tier and relevance"""
    return sorted(jobs, key=lambda j: (j.get('tier', 3), not j.get('relevant', True)))


def display_jobs(jobs, title="Jobs Found"):
    """Display jobs in a formatted way"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")
    
    if not jobs:
        print("No new jobs found.")
        return
    
    tier_names = {1: "🔥 TIER 1 - Dream Companies", 2: "⭐ TIER 2 - Strong Companies", 3: "📋 TIER 3 - Other"}
    
    for tier in [1, 2, 3]:
        tier_jobs = [j for j in jobs if j.get('tier') == tier]
        if tier_jobs:
            print(f"\n{tier_names[tier]} ({len(tier_jobs)} jobs)")
            print("-" * 50)
            
            for job in tier_jobs:
                relevance = "✅" if job.get('relevant') else "⚠️"
                title = job.get('title', 'Unknown')[:50]
                company = job.get('company', 'Unknown')[:30]
                location = job.get('location', '')[:20]
                
                print(f"{relevance} {title}")
                print(f"   {company} | {location}")
                if job.get('url'):
                    print(f"   🔗 {job['url']}")
                print()


def run_job_search(days_back=1, verbose=True):
    """Main function to run the job search agent."""
    if verbose:
        print(f"\n{'='*70}")
        print(f" Job Search Agent - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*70}\n")
    
    print("📧 Fetching job alert emails...")
    emails = get_job_alert_emails(days_back=days_back)
    print(f"   Found {len(emails)} emails to process\n")
    
    # Extract jobs from all emails
    all_jobs = []
    for email in emails:
        jobs = process_email(email)
        all_jobs.extend(jobs)
        print()
    
    print(f"📊 Extracted {len(all_jobs)} total job listings")
    
    # Filter to new jobs only
    new_jobs = filter_new_jobs(all_jobs)
    print(f"   {len(new_jobs)} are new (not seen before)")
    
    # Prioritize and display
    prioritized = prioritize_jobs(new_jobs)
    display_jobs(prioritized, "New Job Opportunities")
    
    # Show stats
    stats = get_job_stats()
    print(f"\n📊 Database Stats:")
    print(f"   Total tracked: {stats['total_jobs']}")
    print(f"   By tier: T1={stats['by_tier'].get(1, 0)}, T2={stats['by_tier'].get(2, 0)}, T3={stats['by_tier'].get(3, 0)}")
    
    return prioritized


def main():
    """Entry point"""
    days = 1
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except:
            pass
    
    print("Testing Gmail connection...")
    if not test_connection():
        print("\n⚠️  Gmail connection failed.")
        sys.exit(1)
    
    jobs = run_job_search(days_back=days)
    return len(jobs)


if __name__ == '__main__':
    main()
