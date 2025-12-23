#!/usr/bin/env python3
# scrape_jobs.py - Main job scraper

import sys
from datetime import datetime
from scrape_greenhouse import scrape_all_greenhouse, GREENHOUSE_COMPANIES
from scrape_lever import scrape_all_lever, LEVER_COMPANIES
from database import filter_new_jobs, get_job_stats

def get_role_priority(title):
    """Rank roles by fit - lower number = better fit for Steff"""
    title_lower = title.lower()
    
    pm_keywords = ['product manager', 'product management', 'apm', 'associate product manager', 
                   'technical program manager', 'program manager', 'tpm', 'product operations']
    if any(kw in title_lower for kw in pm_keywords):
        return 1
    
    data_keywords = ['data analyst', 'analytics', 'business analyst', 'data scientist', 
                     'business intelligence', 'bi analyst', 'insights', 'quantitative']
    if any(kw in title_lower for kw in data_keywords):
        return 2
    
    ops_keywords = ['operations', 'strategy', 'gtm', 'go-to-market', 'marketing', 
                    'growth', 'sales ops', 'revenue ops', 'bizops', 'biz ops',
                    'customer success', 'account', 'partnerships', 'solutions']
    if any(kw in title_lower for kw in ops_keywords):
        return 3
    
    research_keywords = ['research', 'ai safety', 'policy', 'trust', 'safety', 
                         'responsible ai', 'ethics', 'governance']
    if any(kw in title_lower for kw in research_keywords):
        return 4
    
    light_tech = ['solutions engineer', 'technical account', 'sales engineer',
                  'implementation', 'integration', 'support engineer', 'qa', 
                  'technical writer', 'developer relations', 'devrel']
    if any(kw in title_lower for kw in light_tech):
        return 5
    
    eng_keywords = ['software engineer', 'backend', 'frontend', 'full stack', 'fullstack',
                    'machine learning engineer', 'ml engineer', 'infrastructure', 
                    'platform engineer', 'sre', 'devops', 'systems engineer',
                    'security engineer', 'data engineer', 'mobile engineer']
    if any(kw in title_lower for kw in eng_keywords):
        return 6
    
    return 7

def scrape_all_jobs(verbose=True):
    all_jobs = []
    if verbose:
        print(f"\n{'='*70}")
        print(f" Job Board Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f" Filtering: ≤2 years experience, US only, no interns")
        print(f"{'='*70}\n")
        print(f"🌱 Scraping Greenhouse ({len(GREENHOUSE_COMPANIES)} companies)...")
    greenhouse_jobs = scrape_all_greenhouse(verbose=verbose)
    all_jobs.extend(greenhouse_jobs)
    if verbose:
        print(f"   Total from Greenhouse: {len(greenhouse_jobs)} jobs\n")
        print(f"🎯 Scraping Lever ({len(LEVER_COMPANIES)} companies)...")
    lever_jobs = scrape_all_lever(verbose=verbose)
    all_jobs.extend(lever_jobs)
    if verbose:
        print(f"   Total from Lever: {len(lever_jobs)} jobs\n")
    return all_jobs

def is_us_location(location):
    if not location:
        return False
    location_lower = location.lower().strip()
    
    non_us = [
        'spain', 'poland', 'uk', 'united kingdom', 'canada', 'germany', 
        'france', 'india', 'singapore', 'japan', 'australia', 'brazil',
        'mexico', 'ireland', 'netherlands', 'sweden', 'israel', 'china',
        'hong kong', 'taiwan', 'korea', 'dubai', 'uae', 'italy', 'portugal',
        'switzerland', 'austria', 'belgium', 'denmark', 'norway', 'finland',
        'london', 'toronto', 'vancouver', 'montreal', 'berlin', 'paris', 
        'amsterdam', 'dublin', 'sydney', 'melbourne', 'singapore', 
        'bangalore', 'mumbai', 'tel aviv', 'tokyo', 'seoul',
        'mexico city', 'sao paulo', 'warsaw', 'prague',
        ', uk', ', ca,', ', de', ', fr', ', jp', ', au', ', sg', ', in',
        ', mx', 'ontario', 'british columbia', 'emea', 'apac', 'latam',
    ]
    
    for non in non_us:
        if non in location_lower:
            return False
    
    us_indicators = [
        'united states', 'usa', 'u.s.', ', us', '- us', 'remote - us',
        'remote us', '(us)', 'remote, us', 'remote (us)', 'us remote',
        'california', 'new york', 'texas', 'washington', 'colorado', 
        'massachusetts', 'illinois', 'georgia', 'florida', 'arizona',
        'oregon', 'virginia', 'north carolina', 'pennsylvania', 'ohio',
        'san francisco', 'nyc', 'seattle', 'austin', 'boston', 
        'los angeles', 'chicago', 'denver', 'atlanta', 'miami',
        'palo alto', 'mountain view', 'menlo park', 'sunnyvale',
        'san jose', 'san diego', 'portland', 'phoenix', 'dallas',
        'bay area', 'sf', 'salt lake', 'bellevue', 'brooklyn',
    ]
    
    for indicator in us_indicators:
        if indicator in location_lower:
            return True
    
    return False

def filter_us_jobs(jobs):
    return [job for job in jobs if is_us_location(job.get('location', ''))]

def display_jobs(jobs, new_job_urls=None):
    if new_job_urls is None:
        new_job_urls = set()
    
    print(f"\n{'='*70}")
    print(f" Entry-Level Jobs (≤2 yrs exp, USA Only)")
    print(f" 🆕 = New since last run")
    print(f"{'='*70}")
    
    if not jobs:
        print("\nNo jobs found matching criteria.")
        return
    
    tier_names = {1: "🔥 TIER 1 - Dream Companies", 2: "⭐ TIER 2 - Strong", 3: "📋 TIER 3 - Other"}
    role_names = {
        1: "🎯 PM / Program Manager",
        2: "📊 Data / Analytics", 
        3: "📈 Ops / GTM / Marketing",
        4: "🔬 Research / AI Safety",
        5: "🔧 Light Technical",
        6: "💻 Engineering (Code-Heavy)",
        7: "📋 Other"
    }
    
    for tier in [1, 2, 3]:
        tier_jobs = [j for j in jobs if j.get('tier') == tier]
        if not tier_jobs:
            continue
            
        print(f"\n{'='*70}")
        print(f"{tier_names[tier]} ({len(tier_jobs)} jobs)")
        print(f"{'='*70}")
        
        for priority in [1, 2, 3, 4, 5, 6, 7]:
            priority_jobs = [j for j in tier_jobs if get_role_priority(j['title']) == priority]
            if not priority_jobs:
                continue
            
            print(f"\n  {role_names[priority]} ({len(priority_jobs)} jobs)")
            print(f"  {'-'*55}")
            
            companies = {}
            for job in priority_jobs:
                company = job.get('company', 'Unknown')
                if company not in companies:
                    companies[company] = []
                companies[company].append(job)
            
            for company, cjobs in sorted(companies.items()):
                print(f"\n    📍 {company}")
                for job in cjobs[:3]:
                    is_new = job.get('url', '') in new_job_urls
                    new_marker = "🆕" if is_new else "  "
                    years = job.get('years_required')
                    years_str = f"({years}yr)" if years else "(0-2yr)"
                    print(f"      {new_marker} • {job['title'][:45]} {years_str}")
                    print(f"            📍 {job['location'][:35]}")
                    print(f"            🔗 {job['url'][:60]}")
                if len(cjobs) > 3:
                    print(f"            ... and {len(cjobs) - 3} more")

def main():
    all_jobs = scrape_all_jobs(verbose=True)
    print(f"📊 Total jobs scraped: {len(all_jobs)}")
    
    entry_jobs = [j for j in all_jobs if j.get('relevant')]
    print(f"   Entry-level (≤2 yrs): {len(entry_jobs)}")
    
    us_jobs = filter_us_jobs(entry_jobs)
    print(f"   US-based: {len(us_jobs)}")
    
    new_jobs = filter_new_jobs(us_jobs.copy())
    new_job_urls = {j.get('url', '') for j in new_jobs}
    print(f"   New (not seen before): {len(new_jobs)}")
    
    for job in us_jobs:
        job['role_priority'] = get_role_priority(job['title'])
    
    us_jobs.sort(key=lambda j: (j.get('tier', 3), j.get('role_priority', 7), j.get('company', '')))
    
    display_jobs(us_jobs, new_job_urls)
    
    print(f"\n{'='*70}")
    print("📌 QUICK SUMMARY - Best Matches for You (PM/Data/Ops at Tier 1)")
    print(f"{'='*70}")
    
    best_jobs = [j for j in us_jobs if j.get('role_priority', 7) <= 3 and j.get('tier', 3) == 1]
    if best_jobs:
        print(f"\n🌟 Found {len(best_jobs)} PM/Data/Ops roles at Tier 1 companies:\n")
        for job in best_jobs[:15]:
            is_new = job.get('url', '') in new_job_urls
            new_marker = "🆕" if is_new else "  "
            years = job.get('years_required')
            years_str = f"({years}yr)" if years else "(0-2yr)"
            print(f"  {new_marker} • {job['title'][:40]} @ {job['company']} {years_str}")
            print(f"       🔗 {job['url'][:60]}")
    else:
        print("\n   No PM/Data/Ops roles at Tier 1 companies right now.")
    
    stats = get_job_stats()
    print(f"\n📊 Database: {stats['total_jobs']} total tracked")
    print(f"✅ Done!")

if __name__ == '__main__':
    main()
