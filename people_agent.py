#!/usr/bin/env python3
"""
People Finder Agent
- Finds team members at target companies
- Generates personalized outreach messages
- Queues messages for review and sending
"""

import json
import os
from datetime import datetime

# Your profile - customize this
MY_PROFILE = {
    "name": "Steffi",
    "school": "Duke MEng",
    "highlight": "led a production data-quality and anomaly-detection platform that automated validation across pipelines and delivered ~$260K in annual savings",
}

QUEUE_FILE = "message_queue.json"
PEOPLE_FILE = "people_database.json"

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_queue(queue):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def load_people():
    if os.path.exists(PEOPLE_FILE):
        with open(PEOPLE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_people(people):
    with open(PEOPLE_FILE, 'w') as f:
        json.dump(people, f, indent=2)

def generate_message(person):
    """Generate personalized message based on person's profile"""
    
    name = person.get('name', 'there')
    role = person.get('role', '').lower()
    company = person.get('company', 'your company')
    specialty = person.get('specialty', '')
    
    # Determine what to compliment based on their role
    if any(kw in role for kw in ['data', 'analytics', 'scientist']):
        their_work = "building data platforms"
    elif any(kw in role for kw in ['product', 'pm']):
        their_work = "shaping product strategy"
    elif any(kw in role for kw in ['engineer', 'software', 'swe']):
        their_work = "building scalable systems"
    elif any(kw in role for kw in ['program', 'tpm', 'project']):
        their_work = "driving complex initiatives"
    elif any(kw in role for kw in ['director', 'head', 'lead', 'vp', 'manager']):
        their_work = "leading teams"
    elif any(kw in role for kw in ['recruit', 'talent']):
        their_work = "connecting talent with opportunities"
    elif any(kw in role for kw in ['ai', 'ml', 'machine learning']):
        their_work = "advancing AI/ML"
    else:
        their_work = f"your work"
    
    # Build the message
    specialty_part = f"Your work on {specialty} is inspiring—" if specialty else ""
    
    message = f"Hi {name} — I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']}. I {MY_PROFILE['highlight']}. {specialty_part}Your experience {their_work} at {company} caught my attention—would love to connect and learn from your journey."
    
    return message

def add_person(name, role, company, linkedin_url="", specialty=""):
    """Add a person to the database and generate their message"""
    
    people = load_people()
    queue = load_queue()
    
    person = {
        "id": len(people) + 1,
        "name": name,
        "role": role,
        "company": company,
        "linkedin_url": linkedin_url,
        "specialty": specialty,
        "added_date": datetime.now().isoformat(),
    }
    
    # Generate personalized message
    message = generate_message(person)
    
    # Add to people database
    people.append(person)
    save_people(people)
    
    # Add to message queue
    queue_item = {
        "id": len(queue) + 1,
        "person_id": person['id'],
        "person_name": name,
        "company": company,
        "linkedin_url": linkedin_url,
        "message": message,
        "status": "pending",  # pending, sent, skipped
        "created_date": datetime.now().isoformat(),
    }
    queue.append(queue_item)
    save_queue(queue)
    
    return person, message

def get_linkedin_search_urls(company):
    """Get LinkedIn search URLs for different teams at a company"""
    company_encoded = company.replace(' ', '%20')
    
    return {
        "Product Team": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20product%20manager",
        "Data Team": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20data%20engineer%20OR%20data%20scientist",
        "Engineering": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20software%20engineer",
        "Program/TPM": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20program%20manager%20OR%20TPM",
        "Leadership": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20director%20OR%20head%20of",
        "Recruiting": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20recruiter",
    }

def view_queue():
    """View all pending messages"""
    queue = load_queue()
    pending = [q for q in queue if q['status'] == 'pending']
    return pending

def mark_sent(queue_id):
    """Mark a message as sent"""
    queue = load_queue()
    for item in queue:
        if item['id'] == queue_id:
            item['status'] = 'sent'
            item['sent_date'] = datetime.now().isoformat()
    save_queue(queue)

def mark_skipped(queue_id):
    """Mark a message as skipped"""
    queue = load_queue()
    for item in queue:
        if item['id'] == queue_id:
            item['status'] = 'skipped'
    save_queue(queue)

# ===================
# CLI Interface
# ===================

def print_menu():
    print("\n" + "="*50)
    print("👥 PEOPLE FINDER AGENT")
    print("="*50)
    print("1. 🔍 Search for people at a company")
    print("2. ➕ Add a person & generate message")
    print("3. 📋 View message queue")
    print("4. ✅ Mark message as sent")
    print("5. ⏭️  Skip a message")
    print("6. 📊 View stats")
    print("7. 🚪 Exit")
    print("="*50)

def main():
    while True:
        print_menu()
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            # Search for people
            company = input("Enter company name: ").strip()
            if company:
                print(f"\n🔍 LinkedIn search links for {company}:\n")
                urls = get_linkedin_search_urls(company)
                for team, url in urls.items():
                    print(f"  {team}:")
                    print(f"  {url}\n")
                print("👉 Open these links in your browser to find people!")
        
        elif choice == "2":
            # Add a person
            print("\n➕ Add a new person:\n")
            name = input("First name: ").strip()
            role = input("Their role/title: ").strip()
            company = input("Company: ").strip()
            linkedin = input("LinkedIn URL (optional): ").strip()
            specialty = input("Their specialty (optional, e.g., 'building large-scale data platforms'): ").strip()
            
            if name and role and company:
                person, message = add_person(name, role, company, linkedin, specialty)
                print(f"\n✅ Added {name} from {company}!")
                print(f"\n📝 Generated message:\n")
                print("-"*40)
                print(message)
                print("-"*40)
                print(f"\n📊 Character count: {len(message)}/300")
                if len(message) <= 300:
                    print("✅ Perfect for LinkedIn connection request!")
                else:
                    print("⚠️ Too long for connection request - use InMail or shorten")
        
        elif choice == "3":
            # View queue
            pending = view_queue()
            if not pending:
                print("\n📭 No pending messages in queue!")
            else:
                print(f"\n📋 Message Queue ({len(pending)} pending):\n")
                for item in pending:
                    print(f"ID: {item['id']} | {item['person_name']} @ {item['company']}")
                    print(f"LinkedIn: {item.get('linkedin_url', 'N/A')}")
                    print(f"Message:\n{item['message']}")
                    print("-"*40)
        
        elif choice == "4":
            # Mark as sent
            pending = view_queue()
            if not pending:
                print("\n📭 No pending messages!")
            else:
                print("\nPending messages:")
                for item in pending:
                    print(f"  {item['id']}: {item['person_name']} @ {item['company']}")
                queue_id = input("\nEnter ID to mark as sent: ").strip()
                if queue_id.isdigit():
                    mark_sent(int(queue_id))
                    print("✅ Marked as sent!")
        
        elif choice == "5":
            # Skip
            pending = view_queue()
            if not pending:
                print("\n📭 No pending messages!")
            else:
                print("\nPending messages:")
                for item in pending:
                    print(f"  {item['id']}: {item['person_name']} @ {item['company']}")
                queue_id = input("\nEnter ID to skip: ").strip()
                if queue_id.isdigit():
                    mark_skipped(int(queue_id))
                    print("⏭️ Skipped!")
        
        elif choice == "6":
            # Stats
            queue = load_queue()
            people = load_people()
            pending = len([q for q in queue if q['status'] == 'pending'])
            sent = len([q for q in queue if q['status'] == 'sent'])
            skipped = len([q for q in queue if q['status'] == 'skipped'])
            
            print(f"\n📊 Stats:")
            print(f"  Total people: {len(people)}")
            print(f"  Pending messages: {pending}")
            print(f"  Sent: {sent}")
            print(f"  Skipped: {skipped}")
        
        elif choice == "7":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
