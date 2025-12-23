# parse_indeed.py - Parse Indeed job alert emails

import re
from bs4 import BeautifulSoup
from config import classify_company, is_relevant_title


def parse_indeed_alert(email_data):
    """
    Parse an Indeed job alert email and extract job listings.
    
    Returns list of job dicts with title, company, location, url.
    """
    jobs = []
    body = email_data.get('body', '')
    links = email_data.get('links', [])
    
    # Indeed job URL patterns
    indeed_patterns = [
        r'https://www\.indeed\.com/viewjob\?jk=([a-f0-9]+)',
        r'https://www\.indeed\.com/rc/clk\?jk=([a-f0-9]+)',
        r'indeed\.com.*?jk=([a-f0-9]+)',
    ]
    
    # Extract job keys from links
    job_keys = set()
    for link in links:
        for pattern in indeed_patterns:
            match = re.search(pattern, link, re.IGNORECASE)
            if match:
                job_keys.add(match.group(1))
                break
    
    # Parse job listings from body
    # Indeed format varies but typically:
    # Job Title
    # Company Name
    # Location
    # Brief description...
    
    lines = body.split('\n')
    i = 0
    while i < len(lines) - 2:
        line = lines[i].strip()
        
        # Heuristic: job title usually starts with capital, has 2-10 words
        words = line.split()
        if 2 <= len(words) <= 10 and line[0].isupper() and not line.endswith(':'):
            # Could be a job title
            potential_title = line
            potential_company = lines[i+1].strip() if i+1 < len(lines) else ''
            potential_location = lines[i+2].strip() if i+2 < len(lines) else ''
            
            # Basic validation
            if (potential_company and 
                len(potential_company) < 100 and
                not potential_company.startswith('http')):
                
                jobs.append({
                    'title': potential_title,
                    'company': potential_company,
                    'location': potential_location,
                    'source': 'indeed',
                    'tier': classify_company(potential_company),
                    'relevant': is_relevant_title(potential_title),
                })
                i += 3
                continue
        i += 1
    
    # Add URLs to jobs
    job_key_list = list(job_keys)
    for i, job_key in enumerate(job_key_list):
        url = f'https://www.indeed.com/viewjob?jk={job_key}'
        if i < len(jobs):
            jobs[i]['url'] = url
        else:
            jobs.append({
                'title': 'Unknown',
                'company': 'Unknown',
                'location': 'Unknown',
                'url': url,
                'source': 'indeed',
                'tier': 3,
                'relevant': True,
                'needs_enrichment': True,
            })
    
    return jobs


def extract_indeed_jobs_from_links(links):
    """
    Extract job info directly from Indeed URLs.
    """
    jobs = []
    indeed_pattern = r'indeed\.com.*?jk=([a-f0-9]+)'
    
    seen_keys = set()
    for link in links:
        match = re.search(indeed_pattern, link, re.IGNORECASE)
        if match:
            job_key = match.group(1)
            if job_key not in seen_keys:
                seen_keys.add(job_key)
                jobs.append({
                    'title': 'Needs Fetching',
                    'company': 'Needs Fetching',
                    'location': 'Needs Fetching', 
                    'url': f'https://www.indeed.com/viewjob?jk={job_key}',
                    'job_key': job_key,
                    'source': 'indeed',
                    'tier': 3,
                    'relevant': True,
                    'needs_enrichment': True,
                })
    
    return jobs


def parse_indeed_html(html_body):
    """
    Parse Indeed HTML email for structured extraction.
    """
    try:
        soup = BeautifulSoup(html_body, 'html.parser')
        jobs = []
        
        # Indeed email structure varies
        job_cards = soup.find_all(['tr', 'div', 'td'], class_=re.compile(r'job|result'))
        
        for card in job_cards:
            title_elem = card.find(['a', 'span'], text=re.compile(r'.{10,}'))
            
            if title_elem:
                # Try to find company/location nearby
                text_content = card.get_text(separator='\n', strip=True)
                lines = [l for l in text_content.split('\n') if l.strip()]
                
                if len(lines) >= 1:
                    job = {
                        'title': lines[0] if lines else 'Unknown',
                        'company': lines[1] if len(lines) > 1 else 'Unknown',
                        'location': lines[2] if len(lines) > 2 else 'Unknown',
                        'source': 'indeed',
                    }
                    
                    # Get URL
                    link = card.find('a', href=True)
                    if link:
                        job['url'] = link['href']
                    
                    job['tier'] = classify_company(job['company'])
                    job['relevant'] = is_relevant_title(job['title'])
                    jobs.append(job)
        
        return jobs
    except Exception as e:
        print(f"HTML parsing error: {e}")
        return []
