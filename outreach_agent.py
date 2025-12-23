#!/usr/bin/env python3
"""
Outreach Agent - Connected to Job Dashboard
3 Types: Team Members, Hiring Posters, Coffee Chat
"""

import json
import os
from datetime import datetime

# Your profile
MY_PROFILE = {
    "name": "Steffi",
    "school": "Duke MEng",
    "highlight": "led a production data-quality and anomaly-detection platform that automated validation across pipelines and delivered ~$260K in annual savings",
}

JOBS_FILE = "all_jobs.json"
QUEUE_FILE = "outreach_queue.json"

# ====================
# MESSAGE TEMPLATES
# ====================

def generate_team_member_message(person):
    """Type 1: For people on the team you're applying to"""
    name = person['name']
    role = person.get('role', '').lower()
    company = person['company']
    specialty = person.get('specialty', '')
    job_title = person.get('job_applying_for', '')
    
    # Customize based on their role
    if any(kw in role for kw in ['data', 'analytics', 'scientist']):
        their_work = "building data platforms"
    elif any(kw in role for kw in ['product', 'pm']):
        their_work = "shaping product strategy"
    elif any(kw in role for kw in ['engineer', 'software']):
        their_work = "building scalable systems"
    elif any(kw in role for kw in ['program', 'tpm', 'project']):
        their_work = "driving complex initiatives"
    elif any(kw in role for kw in ['director', 'head', 'lead', 'vp', 'manager']):
        their_work = "leading teams"
    elif any(kw in role for kw in ['ai', 'ml', 'machine learning', 'research']):
        their_work = "advancing AI/ML"
    else:
        their_work = "your work"
    
    specialty_part = f"Your work on {specialty} is inspiring—" if specialty else ""
    
    message = f"Hi {name} — I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']}. I {MY_PROFILE['highlight']}. {specialty_part}Your experience {their_work} at {company} caught my attention—would love to connect and learn from your journey."
    
    return message


def generate_hiring_poster_message(person):
    """Type 2: For people who posted 'We're hiring!' on LinkedIn"""
    name = person['name']
    company = person['company']
    job_title = person.get('job_applying_for', 'the open role')
    
    message = f"Hi {name} — I saw your post about hiring at {company} and I'm very interested! I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']}. I {MY_PROFILE['highlight']}. Would love to connect and learn more about the {job_title} opportunity."
    
    return message


def generate_coffee_chat_message(person):
    """Type 3: General networking - initial connection request"""
    name = person['name']
    role = person.get('role', '')
    company = person['company']
    
    message = f"Hi {name} — I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']} exploring opportunities in {get_industry(company)}. I admire your journey at {company} and would love to connect!"
    
    return message


def generate_followup_message(person):
    """Type 3b: Follow-up after they accept - ask for coffee chat"""
    name = person['name']
    company = person['company']
    
    message = f"""Hi {name}, thanks so much for connecting!

I'm {MY_PROFILE['name']}, currently finishing my {MY_PROFILE['school']}. I've been researching {company} and am really impressed by the team's work.

Would you have 15-20 minutes for a quick virtual coffee chat? I'd love to hear about your experience and any advice you might have for someone breaking into the field.

Totally understand if you're busy—I appreciate any time you can spare!

Best,
{MY_PROFILE['name']}"""
    
    return message


def get_industry(company):
    """Determine industry based on company"""
    fintech = ['stripe', 'plaid', 'brex', 'ramp', 'coinbase', 'robinhood', 'affirm', 'chime', 'mercury']
    ai = ['anthropic', 'openai', 'deepmind', 'cohere', 'scale', 'hugging face']
    faang = ['google', 'meta', 'amazon', 'apple', 'microsoft', 'netflix']
    
    company_lower = company.lower()
    if any(c in company_lower for c in fintech):
        return "fintech"
    elif any(c in company_lower for c in ai):
        return "AI"
    elif any(c in company_lower for c in faang):
        return "tech"
    else:
        return "tech"


# ====================
# DATA MANAGEMENT
# ====================

def load_jobs():
    """Load jobs from dashboard"""
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []


def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return []


def save_queue(queue):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)


def get_companies_from_jobs():
    """Get unique companies from job dashboard"""
    jobs = load_jobs()
    companies = {}
    for job in jobs:
        company = job.get('company', '')
        if company:
            if company not in companies:
                companies[company] = {
                    'name': company,
                    'tier': job.get('tier', 3),
                    'roles': []
                }
            companies[company]['roles'].append(job.get('title', ''))
    return companies


def get_linkedin_search_url(company, search_type, job_title=None):
    """Generate LinkedIn search URLs"""
    company_encoded = company.replace(' ', '%20')
    
    if search_type == "team":
        # Search for people on the specific team
        if job_title:
            role_keyword = extract_role_keyword(job_title)
            return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20{role_keyword}"
        return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}"
    
    elif search_type == "hiring":
        # Search for hiring posts
        return f"https://www.linkedin.com/search/results/content/?keywords={company_encoded}%20hiring&origin=GLOBAL_SEARCH_HEADER"
    
    elif search_type == "recruiter":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20recruiter%20OR%20talent"
    
    elif search_type == "leadership":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20director%20OR%20head%20of%20OR%20VP"
    
    return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}"


def extract_role_keyword(job_title):
    """Extract searchable keyword from job title"""
    title_lower = job_title.lower()
    
    if 'product manager' in title_lower or 'product' in title_lower:
        return 'product%20manager'
    elif 'program manager' in title_lower or 'tpm' in title_lower:
        return 'program%20manager'
    elif 'data analyst' in title_lower or 'analytics' in title_lower:
        return 'data%20analyst'
    elif 'data scientist' in title_lower:
        return 'data%20scientist'
    elif 'data engineer' in title_lower:
        return 'data%20engineer'
    elif 'software engineer' in title_lower:
        return 'software%20engineer'
    elif 'research' in title_lower:
        return 'research'
    elif 'operations' in title_lower:
        return 'operations'
    else:
        return ''


def add_to_queue(person, message_type):
    """Add person to outreach queue with generated message"""
    queue = load_queue()
    
    # Generate appropriate message
    if message_type == "team":
        message = generate_team_member_message(person)
    elif message_type == "hiring":
        message = generate_hiring_poster_message(person)
    elif message_type == "coffee":
        message = generate_coffee_chat_message(person)
    elif message_type == "followup":
        message = generate_followup_message(person)
    else:
        message = generate_team_member_message(person)
    
    queue_item = {
        "id": len(queue) + 1,
        "person_name": person['name'],
        "person_role": person.get('role', ''),
        "company": person['company'],
        "linkedin_url": person.get('linkedin_url', ''),
        "job_applying_for": person.get('job_applying_for', ''),
        "message_type": message_type,
        "message": message,
        "status": "pending",  # pending, sent, accepted, followup_sent, skipped
        "created_date": datetime.now().isoformat(),
    }
    
    queue.append(queue_item)
    save_queue(queue)
    
    return queue_item, message


# ====================
# CLI INTERFACE
# ====================

def print_header():
    print("\n" + "="*60)
    print("👥 OUTREACH AGENT - Connected to Job Dashboard")
    print("="*60)


def print_menu():
    print("\n1. 📋 View companies from job dashboard")
    print("2. 🔍 Search for people at a company")
    print("3. ➕ Add person (Team Member)")
    print("4. 📢 Add person (Hiring Poster)")
    print("5. ☕ Add person (Coffee Chat)")
    print("6. 📨 View message queue")
    print("7. ✅ Mark as sent")
    print("8. 🤝 Mark as accepted (generate follow-up)")
    print("9. 📊 Stats")
    print("0. 🚪 Exit")
    print("-"*60)


def main():
    print_header()
    
    while True:
        print_menu()
        choice = input("Choice: ").strip()
        
        if choice == "1":
            # View companies from dashboard
            companies = get_companies_from_jobs()
            if not companies:
                print("\n⚠️ No jobs found! Run the job scraper first.")
                continue
            
            print(f"\n📋 Companies from your job dashboard ({len(companies)}):\n")
            
            # Sort by tier
            for tier in [1, 2, 3]:
                tier_companies = [c for c in companies.values() if c['tier'] == tier]
                if tier_companies:
                    tier_emoji = "🔥" if tier == 1 else "⭐" if tier == 2 else "📋"
                    print(f"{tier_emoji} Tier {tier}:")
                    for c in sorted(tier_companies, key=lambda x: x['name']):
                        roles = list(set(c['roles']))[:3]
                        print(f"   • {c['name']} - {', '.join(roles)[:50]}...")
                    print()
        
        elif choice == "2":
            # Search for people
            companies = get_companies_from_jobs()
            company_list = sorted(companies.keys())
            
            print("\n🔍 Select a company:")
            for i, c in enumerate(company_list[:20], 1):
                print(f"   {i}. {c}")
            
            selection = input("\nEnter number or company name: ").strip()
            
            if selection.isdigit() and int(selection) <= len(company_list):
                company = company_list[int(selection) - 1]
            else:
                company = selection
            
            if company:
                print(f"\n🔍 LinkedIn searches for {company}:\n")
                
                # Get roles at this company
                roles = companies.get(company, {}).get('roles', [])
                
                print(f"📋 Open roles: {', '.join(set(roles))[:60]}...\n")
                
                print("1️⃣  Team Members:")
                for role in list(set(roles))[:3]:
                    url = get_linkedin_search_url(company, "team", role)
                    print(f"   {role}: {url}\n")
                
                print("2️⃣  Hiring Posts:")
                print(f"   {get_linkedin_search_url(company, 'hiring')}\n")
                
                print("3️⃣  Recruiters:")
                print(f"   {get_linkedin_search_url(company, 'recruiter')}\n")
                
                print("4️⃣  Leadership:")
                print(f"   {get_linkedin_search_url(company, 'leadership')}\n")
        
        elif choice in ["3", "4", "5"]:
            # Add person
            message_types = {"3": "team", "4": "hiring", "5": "coffee"}
            message_type = message_types[choice]
            
            type_names = {"team": "Team Member", "hiring": "Hiring Poster", "coffee": "Coffee Chat"}
            print(f"\n➕ Add {type_names[message_type]}:\n")
            
            name = input("First name: ").strip()
            role = input("Their role: ").strip()
            company = input("Company: ").strip()
            linkedin = input("LinkedIn URL (optional): ").strip()
            
            if message_type == "team":
                specialty = input("Their specialty (optional): ").strip()
                job = input("Job you're applying for (optional): ").strip()
            else:
                specialty = ""
                job = ""
            
            if name and company:
                person = {
                    "name": name,
                    "role": role,
                    "company": company,
                    "linkedin_url": linkedin,
                    "specialty": specialty,
                    "job_applying_for": job,
                }
                
                queue_item, message = add_to_queue(person, message_type)
                
                print(f"\n✅ Added {name} to queue!")
                print(f"\n📝 Generated message ({len(message)} chars):\n")
                print("-"*50)
                print(message)
                print("-"*50)
                
                if len(message) <= 300:
                    print("✅ Perfect for LinkedIn connection request!")
                else:
                    print("⚠️ Too long for connection request - use InMail")
        
        elif choice == "6":
            # View queue
            queue = load_queue()
            pending = [q for q in queue if q['status'] == 'pending']
            
            if not pending:
                print("\n📭 No pending messages!")
                continue
            
            print(f"\n📨 Pending Messages ({len(pending)}):\n")
            
            for item in pending:
                type_emoji = {"team": "👥", "hiring": "📢", "coffee": "☕", "followup": "🔄"}.get(item['message_type'], "📝")
                print(f"ID {item['id']} | {type_emoji} {item['person_name']} @ {item['company']}")
                print(f"Type: {item['message_type'].upper()}")
                if item.get('linkedin_url'):
                    print(f"LinkedIn: {item['linkedin_url']}")
                print(f"Message:\n{item['message'][:200]}...")
                print("-"*50)
        
        elif choice == "7":
            # Mark as sent
            queue = load_queue()
            pending = [q for q in queue if q['status'] == 'pending']
            
            if not pending:
                print("\n📭 No pending messages!")
                continue
            
            print("\nPending:")
            for item in pending:
                print(f"   {item['id']}: {item['person_name']} @ {item['company']}")
            
            queue_id = input("\nID to mark as sent: ").strip()
            if queue_id.isdigit():
                for q in queue:
                    if q['id'] == int(queue_id):
                        q['status'] = 'sent'
                        q['sent_date'] = datetime.now().isoformat()
                save_queue(queue)
                print("✅ Marked as sent!")
        
        elif choice == "8":
            # Mark as accepted + generate follow-up
            queue = load_queue()
            sent = [q for q in queue if q['status'] == 'sent']
            
            if not sent:
                print("\n📭 No sent messages to mark as accepted!")
                continue
            
            print("\nSent messages:")
            for item in sent:
                print(f"   {item['id']}: {item['person_name']} @ {item['company']}")
            
            queue_id = input("\nID to mark as accepted: ").strip()
            if queue_id.isdigit():
                for q in queue:
                    if q['id'] == int(queue_id):
                        q['status'] = 'accepted'
                        q['accepted_date'] = datetime.now().isoformat()
                        
                        # Generate follow-up message
                        person = {
                            "name": q['person_name'],
                            "company": q['company'],
                        }
                        followup = generate_followup_message(person)
                        
                        print(f"\n🎉 {q['person_name']} accepted!")
                        print(f"\n📝 Follow-up message:\n")
                        print("-"*50)
                        print(followup)
                        print("-"*50)
                        
                        # Add follow-up to queue
                        add_followup = input("\nAdd follow-up to queue? (y/n): ").strip().lower()
                        if add_followup == 'y':
                            add_to_queue(person, "followup")
                            print("✅ Follow-up added to queue!")
                
                save_queue(queue)
        
        elif choice == "9":
            # Stats
            queue = load_queue()
            companies = get_companies_from_jobs()
            
            pending = len([q for q in queue if q['status'] == 'pending'])
            sent = len([q for q in queue if q['status'] == 'sent'])
            accepted = len([q for q in queue if q['status'] == 'accepted'])
            
            print(f"\n📊 Stats:\n")
            print(f"   Companies in dashboard: {len(companies)}")
            print(f"   Pending messages: {pending}")
            print(f"   Sent: {sent}")
            print(f"   Accepted: {accepted}")
            print(f"   Response rate: {(accepted/sent*100):.0f}%" if sent > 0 else "   Response rate: N/A")
        
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice")


if __name__ == "__main__":
    main()
