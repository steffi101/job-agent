#!/usr/bin/env python3
"""
People Finder Agent - Streamlit UI
Separate from the job dashboard
"""

import streamlit as st
import json
import os
from datetime import datetime

# Your profile
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
        their_work = "your work"
    
    specialty_part = f"Your work on {specialty} is inspiring—" if specialty else ""
    
    message = f"Hi {name} — I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']}. I {MY_PROFILE['highlight']}. {specialty_part}Your experience {their_work} at {company} caught my attention—would love to connect and learn from your journey."
    
    return message

def add_person_to_queue(name, role, company, linkedin_url="", specialty=""):
    """Add person and generate message"""
    
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
    
    message = generate_message(person)
    
    people.append(person)
    save_people(people)
    
    queue_item = {
        "id": len(queue) + 1,
        "person_id": person['id'],
        "person_name": name,
        "company": company,
        "linkedin_url": linkedin_url,
        "message": message,
        "status": "pending",
        "created_date": datetime.now().isoformat(),
    }
    queue.append(queue_item)
    save_queue(queue)
    
    return message

def main():
    st.set_page_config(
        page_title="👥 People Finder Agent",
        page_icon="👥",
        layout="wide"
    )
    
    st.title("👥 People Finder Agent")
    st.caption("Find people, generate personalized messages, and track your outreach")
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🔍 Find People", "➕ Add & Generate Message", "📋 Message Queue", "📊 Stats"]
    )
    
    if page == "🔍 Find People":
        show_find_people()
    elif page == "➕ Add & Generate Message":
        show_add_person()
    elif page == "📋 Message Queue":
        show_queue()
    elif page == "📊 Stats":
        show_stats()

def show_find_people():
    """LinkedIn search links for a company"""
    st.header("🔍 Find People at a Company")
    
    company = st.text_input("Enter company name:", placeholder="e.g., Anthropic, Stripe, Meta")
    
    if company:
        company_encoded = company.replace(' ', '%20')
        
        st.subheader(f"LinkedIn Search Links for {company}")
        
        searches = {
            "🎯 Product Team": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20product%20manager",
            "📊 Data Team": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20data%20engineer%20OR%20data%20scientist%20OR%20data%20analyst",
            "💻 Engineering": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20software%20engineer",
            "📋 Program/TPM": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20program%20manager%20OR%20TPM",
            "🤖 AI/ML Team": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20machine%20learning%20OR%20AI%20engineer",
            "👔 Leadership": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20director%20OR%20head%20of%20OR%20VP",
            "🎯 Recruiting": f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20recruiter%20OR%20talent",
        }
        
        cols = st.columns(2)
        for i, (team, url) in enumerate(searches.items()):
            with cols[i % 2]:
                st.link_button(team, url, use_container_width=True)
        
        st.info("👉 Click a button to search LinkedIn. When you find someone interesting, come back and add them!")

def show_add_person():
    """Add a person and generate message"""
    st.header("➕ Add Person & Generate Message")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Person Details")
        
        name = st.text_input("First Name *", placeholder="e.g., Sagar")
        role = st.text_input("Their Role/Title *", placeholder="e.g., Senior Data Engineer")
        company = st.text_input("Company *", placeholder="e.g., Meta")
        linkedin = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/...")
        specialty = st.text_input(
            "Their Specialty (makes message more personal)",
            placeholder="e.g., building large-scale data platforms"
        )
        
        if st.button("✨ Generate Message & Add to Queue", type="primary", use_container_width=True):
            if name and role and company:
                message = add_person_to_queue(name, role, company, linkedin, specialty)
                st.session_state['generated_message'] = message
                st.session_state['generated_for'] = f"{name} @ {company}"
                st.success(f"✅ Added {name} to queue!")
            else:
                st.error("Please fill in Name, Role, and Company")
    
    with col2:
        st.subheader("Generated Message")
        
        if 'generated_message' in st.session_state:
            st.caption(f"For: {st.session_state.get('generated_for', '')}")
            
            message = st.session_state['generated_message']
            
            st.text_area(
                "Copy this message:",
                value=message,
                height=200,
                key="msg_display"
            )
            
            char_count = len(message)
            if char_count <= 300:
                st.success(f"✅ {char_count}/300 characters - Perfect for LinkedIn!")
            else:
                st.warning(f"⚠️ {char_count}/300 characters - Consider shortening or use InMail")
        else:
            st.info("👈 Fill in the person's details and click Generate")

def show_queue():
    """Show and manage message queue"""
    st.header("📋 Message Queue")
    
    queue = load_queue()
    
    # Filter tabs
    tab1, tab2, tab3 = st.tabs(["📨 Pending", "✅ Sent", "⏭️ Skipped"])
    
    with tab1:
        pending = [q for q in queue if q['status'] == 'pending']
        if not pending:
            st.info("No pending messages! Add people to generate messages.")
        else:
            st.caption(f"{len(pending)} messages to send")
            
            for item in pending:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{item['person_name']}** @ {item['company']}")
                        if item.get('linkedin_url'):
                            st.caption(f"🔗 {item['linkedin_url']}")
                    
                    with col2:
                        if st.button("✅ Sent", key=f"sent_{item['id']}", use_container_width=True):
                            for q in queue:
                                if q['id'] == item['id']:
                                    q['status'] = 'sent'
                                    q['sent_date'] = datetime.now().isoformat()
                            save_queue(queue)
                            st.rerun()
                    
                    with col3:
                        if st.button("⏭️ Skip", key=f"skip_{item['id']}", use_container_width=True):
                            for q in queue:
                                if q['id'] == item['id']:
                                    q['status'] = 'skipped'
                            save_queue(queue)
                            st.rerun()
                    
                    st.text_area(
                        "Message:",
                        value=item['message'],
                        height=120,
                        key=f"msg_{item['id']}",
                        label_visibility="collapsed"
                    )
                    st.divider()
    
    with tab2:
        sent = [q for q in queue if q['status'] == 'sent']
        if not sent:
            st.info("No sent messages yet.")
        else:
            st.caption(f"{len(sent)} messages sent")
            for item in sent:
                st.markdown(f"✅ **{item['person_name']}** @ {item['company']}")
                st.caption(f"Sent: {item.get('sent_date', 'Unknown')[:10]}")
                st.divider()
    
    with tab3:
        skipped = [q for q in queue if q['status'] == 'skipped']
        if not skipped:
            st.info("No skipped messages.")
        else:
            st.caption(f"{len(skipped)} messages skipped")
            for item in skipped:
                st.markdown(f"⏭️ **{item['person_name']}** @ {item['company']}")
                st.divider()

def show_stats():
    """Show outreach stats"""
    st.header("📊 Outreach Stats")
    
    queue = load_queue()
    people = load_people()
    
    pending = len([q for q in queue if q['status'] == 'pending'])
    sent = len([q for q in queue if q['status'] == 'sent'])
    skipped = len([q for q in queue if q['status'] == 'skipped'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total People", len(people))
    col2.metric("Pending", pending)
    col3.metric("Sent", sent)
    col4.metric("Skipped", skipped)
    
    st.divider()
    
    # Companies reached out to
    if people:
        st.subheader("Companies")
        companies = {}
        for p in people:
            co = p.get('company', 'Unknown')
            companies[co] = companies.get(co, 0) + 1
        
        for company, count in sorted(companies.items(), key=lambda x: -x[1]):
            st.markdown(f"• **{company}**: {count} people")

if __name__ == "__main__":
    main()
