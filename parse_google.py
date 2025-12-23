import re
from config import classify_company

def parse_google_careers_alert(email_data):
    jobs = []
    links = email_data.get('links', [])
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
                    'title': 'Google Job',
                    'company': 'Google',
                    'location': 'United States',
                    'url': clean_url,
                    'job_id': job_id,
                    'source': 'google_careers',
                    'tier': 1,
                    'relevant': True,
                    'needs_enrichment': True,
                })
    return jobs
