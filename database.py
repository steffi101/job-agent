# database.py - Track seen jobs and avoid duplicates

import json
import os
from datetime import datetime
from hashlib import md5

DATABASE_FILE = 'seen_jobs.json'


def load_database():
    """Load seen jobs from disk"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {'jobs': {}, 'last_updated': None}


def save_database(db):
    """Save database to disk"""
    db['last_updated'] = datetime.now().isoformat()
    with open(DATABASE_FILE, 'w') as f:
        json.dump(db, f, indent=2, default=str)


def get_job_hash(job):
    """Generate unique hash for a job"""
    # Use combination of title, company, and URL
    key_parts = [
        job.get('title', '').lower().strip(),
        job.get('company', '').lower().strip(),
        job.get('url', '').split('?')[0],  # Remove query params
    ]
    key = '|'.join(key_parts)
    return md5(key.encode()).hexdigest()


def is_new_job(job, db=None):
    """Check if job hasn't been seen before"""
    if db is None:
        db = load_database()
    
    job_hash = get_job_hash(job)
    return job_hash not in db['jobs']


def mark_job_seen(job, db=None):
    """Mark a job as seen"""
    if db is None:
        db = load_database()
    
    job_hash = get_job_hash(job)
    db['jobs'][job_hash] = {
        'title': job.get('title'),
        'company': job.get('company'),
        'url': job.get('url'),
        'first_seen': datetime.now().isoformat(),
        'tier': job.get('tier'),
        'status': 'new',  # new, applied, skipped
    }
    save_database(db)
    return job_hash


def filter_new_jobs(jobs):
    """Filter list of jobs to only new ones"""
    db = load_database()
    new_jobs = []
    
    for job in jobs:
        if is_new_job(job, db):
            new_jobs.append(job)
            mark_job_seen(job, db)
    
    return new_jobs


def update_job_status(job_hash, status):
    """Update status of a job (applied, skipped, etc)"""
    db = load_database()
    if job_hash in db['jobs']:
        db['jobs'][job_hash]['status'] = status
        db['jobs'][job_hash]['updated'] = datetime.now().isoformat()
        save_database(db)


def get_job_stats():
    """Get statistics about tracked jobs"""
    db = load_database()
    
    total = len(db['jobs'])
    by_status = {}
    by_tier = {1: 0, 2: 0, 3: 0}
    
    for job_hash, job in db['jobs'].items():
        status = job.get('status', 'new')
        by_status[status] = by_status.get(status, 0) + 1
        
        tier = job.get('tier', 3)
        by_tier[tier] = by_tier.get(tier, 0) + 1
    
    return {
        'total_jobs': total,
        'by_status': by_status,
        'by_tier': by_tier,
        'last_updated': db['last_updated'],
    }


def clear_old_jobs(days=30):
    """Remove jobs older than N days"""
    db = load_database()
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    to_remove = []
    for job_hash, job in db['jobs'].items():
        first_seen = job.get('first_seen')
        if first_seen:
            try:
                job_time = datetime.fromisoformat(first_seen).timestamp()
                if job_time < cutoff:
                    to_remove.append(job_hash)
            except:
                pass
    
    for job_hash in to_remove:
        del db['jobs'][job_hash]
    
    save_database(db)
    return len(to_remove)
