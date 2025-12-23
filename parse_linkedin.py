# parse_linkedin.py - Parse LinkedIn job alert emails

import re
from bs4 import BeautifulSoup
from config import classify_company, is_relevant_title


def parse_linkedin_alert(email_data):
    """
    Parse a LinkedIn job alert email and extract job listings.
    
    Returns list of job dicts with title, company, location, url.
    """
    jobs = []
    body = email_data.get('body', '')
    links = email_data.get('links', [])
    
    # LinkedIn job URLs pattern
    linkedin_job_pattern = r'https://www\.linkedin\.com/(?:comm/)?jobs/view/(\d+)'
    
    # Extract job IDs from links
    job_ids = set()
    for link in links:
        match = re.search(linkedin_job_pattern, link)
        if match:
            job_ids.add(match.group(1))
    
    # Try to parse job details from email body
    # LinkedIn emails typically have format:
    # Job Title
    # Company Name · Location
    
    # Pattern for job listings in email
    job_block_pattern = r'([A-Z][^·\n]+)\n([^·\n]+)\s*·\s*([^\n]+)'
    matches = re.findall(job_block_pattern, body)
    
    for match in matches:
        title, company, location = match
        title = title.strip()
        company = company.strip()
        location = location.strip()
        
        # Skip if title doesn't look like a job title
        if len(title) < 5 or len(title) > 100:
            continue
        if not any(c.isalpha() for c in title):
            continue
            
        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'source': 'linkedin',
            'tier': classify_company(company),
            'relevant': is_relevant_title(title),
        })
    
    # Add job URLs
    for i, job_id in enumerate(job_ids):
        url = f'https://www.linkedin.com/jobs/view/{job_id}'
        if i < len(jobs):
            jobs[i]['url'] = url
        else:
            jobs.append({
                'title': 'Unknown',
                'company': 'Unknown',
                'location': 'Unknown',
                'url': url,
                'source': 'linkedin',
                'tier': 3,
                'relevant': True,  # Assume relevant if we can't parse
            })
    
    return jobs


def parse_linkedin_html(html_body):
    """
    Parse LinkedIn email HTML for better extraction.
    """
    try:
        soup = BeautifulSoup(html_body, 'html.parser')
        jobs = []
        
        # LinkedIn uses various class patterns
        job_cards = soup.find_all(['tr', 'div'], class_=re.compile(r'job|card|listing'))
        
        for card in job_cards:
            title_elem = card.find(['a', 'span', 'h3'], class_=re.compile(r'title|name'))
            company_elem = card.find(['span', 'div'], class_=re.compile(r'company|employer'))
            location_elem = card.find(['span', 'div'], class_=re.compile(r'location'))
            link_elem = card.find('a', href=re.compile(r'linkedin\.com/jobs'))
            
            if title_elem:
                job = {
                    'title': title_elem.get_text(strip=True),
                    'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                    'location': location_elem.get_text(strip=True) if location_elem else 'Unknown',
                    'url': link_elem['href'] if link_elem else None,
                    'source': 'linkedin',
                }
                job['tier'] = classify_company(job['company'])
                job['relevant'] = is_relevant_title(job['title'])
                jobs.append(job)
        
        return jobs
    except Exception as e:
        print(f"HTML parsing error: {e}")
        return []


def extract_linkedin_jobs_from_links(links):
    """
    Extract job info directly from LinkedIn URLs when email parsing fails.
    Returns list of partial job dicts that need to be enriched.
    """
    jobs = []
    linkedin_pattern = r'linkedin\.com/(?:comm/)?jobs/view/(\d+)'
    
    for link in links:
        match = re.search(linkedin_pattern, link)
        if match:
            job_id = match.group(1)
            jobs.append({
                'title': 'Needs Fetching',
                'company': 'Needs Fetching', 
                'location': 'Needs Fetching',
                'url': f'https://www.linkedin.com/jobs/view/{job_id}',
                'job_id': job_id,
                'source': 'linkedin',
                'tier': 3,
                'relevant': True,
                'needs_enrichment': True,
            })
    
    return jobs
