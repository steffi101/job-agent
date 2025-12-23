#!/usr/bin/env python3
"""
Outreach Agent UI - Connected to Job Dashboard
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

JOBS_FILE = "all_jobs.json"
QUEUE_FILE = "outreach_queue.json"


def load_jobs():
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
    jobs = load_jobs()
    companies = {}
    for job in jobs:
        company = job.get('company', '')
        if company:
            if company not in companies:
                companies[company] = {'name': company, 'tier': job.get('tier', 3), 'roles': []}
            companies[company]['roles'].append(job.get('title', ''))
    return companies


def extract_role_keyword(job_title):
    title_lower = job_title.lower()
    if 'product' in title_lower:
        return 'product%20manager'
    elif 'program' in title_lower or 'tpm' in title_lower:
        return 'program%20manager'
    elif 'data analyst' in title_lower:
        return 'data%20analyst'
    elif 'data scientist' in title_lower:
        return 'data%20scientist'
    elif 'data engineer' in title_lower:
        return 'data%20engineer'
    elif 'software' in title_lower:
        return 'software%20engineer'
    return ''


def get_linkedin_search_url(company, search_type, job_title=None):
    company_encoded = company.replace(' ', '%20')
    
    if search_type == "team" and job_title:
        role_kw = extract_role_keyword(job_title)
        return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20{role_kw}"
    elif search_type == "hiring":
        return f"https://www.linkedin.com/search/results/content/?keywords={company_encoded}%20hiring"
    elif search_type == "recruiter":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20recruiter"
    elif search_type == "leadership":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}%20director%20OR%20VP"
    return f"https://www.linkedin.com/search/results/people/?keywords={company_encoded}"


def generate_message(person, message_type):
    name = person['name']
    company = person['company']
    role = person.get('role', '').lower()
    specialty = person.get('specialty', '')
    
    if message_type == "team":
        # Team member message
        if any(kw in role for kw in ['data', 'analytics', 'scientist']):
            their_work = "building data platforms"
        elif any(kw in role for kw in ['product', 'pm']):
            their_work = "shaping product strategy"
        elif any(kw in role for kw in ['engineer', 'software']):
            their_work = "building scalable systems"
        elif any(kw in role for kw in ['program', 'tpm']):
            their_work = "driving complex initiatives"
        elif any(kw in role for kw in ['director', 'head', 'lead', 'manager']):
            their_work = "leading teams"
        else:
            their_work = "your work"
        
        specialty_part = f"Your work on {specialty} is inspiring—" if specialty else ""
        return f"Hi {name} — I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']}. I {MY_PROFILE['highlight']}. {specialty_part}Your experience {their_work} at {company} caught my attention—would love to connect and learn from your journey."
    
    elif message_type == "hiring":
        # Hiring poster message
        job = person.get('job_applying_for', 'the open role')
        return f"Hi {name} — I saw your post about hiring at {company} and I'm very interested! I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']}. I {MY_PROFILE['highlight']}. Would love to connect and learn more about the {job} opportunity."
    
    elif message_type == "coffee":
        # General networking
        return f"Hi {name} — I'm {MY_PROFILE['name']}, a {MY_PROFILE['school']} exploring opportunities in tech. I admire your journey at {company} and would love to connect!"
    
    elif message_type == "followup":
        # Follow-up after acceptance
        return f"""Hi {name}, thanks so much for connecting!

I'm {MY_PROFILE['name']}, currently finishing my {MY_PROFILE['school']}. I've been researching {company} and am really impressed by the team's work.

Would you have 15-20 minutes for a quick virtual coffee chat? I'd love to hear about your experience and any advice for someone breaking into the field.

Totally understand if you're busy—appreciate any time you can spare!

Best,
{MY_PROFILE['name']}"""
    
    return ""


def add_to_queue(person, message_type):
    queue = load_queue()
    message = generate_message(person, message_type)
    
    queue_item = {
        "id": len(queue) + 1,
        "person_name": person['name'],
        "person_role": person.get('role', ''),
        "company": person['company'],
        "linkedin_url": person.get('linkedin_url', ''),
        "job_applying_for": person.get('job_applying_for', ''),
        "message_type": message_type,
        "message": message,
        "status": "pending",
        "created_date": datetime.now().isoformat(),
    }
    
    queue.append(queue_item)
    save_queue(queue)
    return message


def main():
    st.set_page_config(page_title="👥 Outreach Agent", page_icon="👥", layout="wide")
    
    st.title("👥 Outreach Agent")
    st.caption("Connected to your Job Dashboard • 3 Message Types")
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard Jobs", "🔍 Find People", "➕ Add Person", "📨 Message Queue", "📊 Stats"]
    )
    
    if page == "🏠 Dashboard Jobs":
        show_dashboard_jobs()
    elif page == "🔍 Find People":
        show_find_people()
    elif page == "➕ Add Person":
        show_add_person()
    elif page == "📨 Message Queue":
        show_queue()
    elif page == "📊 Stats":
        show_stats()


def show_dashboard_jobs():
    st.header("🏠 Companies from Your Job Dashboard")
    
    companies = get_companies_from_jobs()
    
    if not companies:
        st.warning("No jobs found! Run the job scraper first.")
        return
    
    st.success(f"Found {len(companies)} companies with open roles")
    
    # Filter by tier
    tier_filter = st.multiselect(
        "Filter by tier",
        options=[1, 2, 3],
        default=[1, 2],
        format_func=lambda x: {1: "🔥 Tier 1", 2: "⭐ Tier 2", 3: "📋 Tier 3"}[x]
    )
    
    for tier in tier_filter:
        tier_companies = [c for c in companies.values() if c['tier'] == tier]
        if tier_companies:
            tier_emoji = {1: "🔥", 2: "⭐", 3: "📋"}[tier]
            st.subheader(f"{tier_emoji} Tier {tier} ({len(tier_companies)} companies)")
            
            for c in sorted(tier_companies, key=lambda x: x['name']):
                roles = list(set(c['roles']))
                
                with st.expander(f"**{c['name']}** - {len(roles)} open roles"):
                    st.write("**Open Roles:**")
                    for role in roles[:5]:
                        st.write(f"• {role}")
                    if len(roles) > 5:
                        st.write(f"• ... and {len(roles) - 5} more")
                    
                    st.divider()
                    st.write("**🔍 Find People:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button(
                            "👥 Team Members",
                            get_linkedin_search_url(c['name'], "team", roles[0] if roles else ""),
                            use_container_width=True
                        )
                        st.link_button(
                            "📢 Hiring Posts",
                            get_linkedin_search_url(c['name'], "hiring"),
                            use_container_width=True
                        )
                    with col2:
                        st.link_button(
                            "🎯 Recruiters",
                            get_linkedin_search_url(c['name'], "recruiter"),
                            use_container_width=True
                        )
                        st.link_button(
                            "👔 Leadership",
                            get_linkedin_search_url(c['name'], "leadership"),
                            use_container_width=True
                        )


def show_find_people():
    st.header("🔍 Find People")
    
    companies = get_companies_from_jobs()
    company_list = sorted(companies.keys())
    
    if not company_list:
        st.warning("No companies found. Run the job scraper first.")
        return
    
    company = st.selectbox("Select company", options=company_list)
    
    if company:
        roles = list(set(companies[company]['roles']))
        
        st.subheader(f"Open roles at {company}:")
        for role in roles[:5]:
            st.write(f"• {role}")
        
        st.divider()
        
        st.subheader("🔍 LinkedIn Searches")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Team Members:**")
            for role in roles[:3]:
                url = get_linkedin_search_url(company, "team", role)
                st.link_button(f"🔍 {role[:30]}...", url, use_container_width=True)
        
        with col2:
            st.markdown("**Other Searches:**")
            st.link_button("📢 Hiring Posts", get_linkedin_search_url(company, "hiring"), use_container_width=True)
            st.link_button("🎯 Recruiters", get_linkedin_search_url(company, "recruiter"), use_container_width=True)
            st.link_button("👔 Leadership", get_linkedin_search_url(company, "leadership"), use_container_width=True)


def show_add_person():
    st.header("➕ Add Person & Generate Message")
    
    companies = get_companies_from_jobs()
    company_list = sorted(companies.keys())
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Person Details")
        
        message_type = st.radio(
            "Message Type",
            options=["team", "hiring", "coffee"],
            format_func=lambda x: {
                "team": "👥 Team Member (someone on the team)",
                "hiring": "📢 Hiring Poster (posted 'We're hiring!')",
                "coffee": "☕ Coffee Chat (general networking)"
            }[x],
            horizontal=False
        )
        
        st.divider()
        
        name = st.text_input("First Name *", placeholder="Sagar")
        role = st.text_input("Their Role", placeholder="Senior Data Engineer")
        
        if company_list:
            company = st.selectbox("Company *", options=[""] + company_list)
        else:
            company = st.text_input("Company *", placeholder="Meta")
        
        linkedin = st.text_input("LinkedIn URL", placeholder="https://linkedin.com/in/...")
        
        if message_type == "team":
            specialty = st.text_input(
                "Their Specialty (makes it personal)",
                placeholder="building large-scale data platforms"
            )
            
            # Get roles for this company
            if company and company in companies:
                roles = list(set(companies[company]['roles']))
                job_applying = st.selectbox("Job you're applying for", options=[""] + roles)
            else:
                job_applying = st.text_input("Job you're applying for", placeholder="Product Manager")
        else:
            specialty = ""
            job_applying = ""
        
        if st.button("✨ Generate Message", type="primary", use_container_width=True):
            if name and company:
                person = {
                    "name": name,
                    "role": role,
                    "company": company,
                    "linkedin_url": linkedin,
                    "specialty": specialty,
                    "job_applying_for": job_applying,
                }
                
                message = add_to_queue(person, message_type)
                st.session_state['generated_message'] = message
                st.session_state['generated_for'] = f"{name} @ {company}"
                st.success(f"✅ Added {name} to queue!")
            else:
                st.error("Please enter Name and Company")
    
    with col2:
        st.subheader("Generated Message")
        
        if 'generated_message' in st.session_state:
            st.caption(f"For: {st.session_state.get('generated_for', '')}")
            
            message = st.session_state['generated_message']
            st.text_area("Copy this:", value=message, height=250)
            
            chars = len(message)
            if chars <= 300:
                st.success(f"✅ {chars}/300 chars - Perfect for LinkedIn!")
            else:
                st.warning(f"⚠️ {chars}/300 chars - Use InMail or shorten")
        else:
            st.info("👈 Fill details and click Generate")
        
        st.divider()
        
        # Quick templates
        st.subheader("📝 Message Type Examples")
        
        with st.expander("👥 Team Member Example"):
            st.code("""Hi Sagar — I'm Steffi, a Duke MEng. I led a production data-quality and anomaly-detection platform that automated validation across pipelines and delivered ~$260K in annual savings. Your work on building large-scale data platforms is inspiring—Your experience building data platforms at Meta caught my attention—would love to connect and learn from your journey.""", language=None)
        
        with st.expander("📢 Hiring Poster Example"):
            st.code("""Hi Sarah — I saw your post about hiring at Stripe and I'm very interested! I'm Steffi, a Duke MEng. I led a production data-quality and anomaly-detection platform that automated validation across pipelines and delivered ~$260K in annual savings. Would love to connect and learn more about the Product Manager opportunity.""", language=None)
        
        with st.expander("☕ Coffee Chat Example"):
            st.code("""Hi Mike — I'm Steffi, a Duke MEng exploring opportunities in fintech. I admire your journey at Plaid and would love to connect!""", language=None)


def show_queue():
    st.header("📨 Message Queue")
    
    queue = load_queue()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📨 Pending", "✅ Sent", "🤝 Accepted", "⏭️ Skipped"])
    
    with tab1:
        pending = [q for q in queue if q['status'] == 'pending']
        if not pending:
            st.info("No pending messages. Add people to get started!")
        else:
            st.caption(f"{len(pending)} messages to send")
            
            for item in pending:
                type_emoji = {"team": "👥", "hiring": "📢", "coffee": "☕", "followup": "🔄"}.get(item['message_type'], "📝")
                
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{type_emoji} {item['person_name']}** @ {item['company']}")
                        if item.get('linkedin_url'):
                            st.caption(f"🔗 [LinkedIn]({item['linkedin_url']})")
                    
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
                    
                    st.text_area("Message:", value=item['message'], height=120, key=f"msg_{item['id']}", label_visibility="collapsed")
                    st.divider()
    
    with tab2:
        sent = [q for q in queue if q['status'] == 'sent']
        if not sent:
            st.info("No sent messages yet.")
        else:
            st.caption(f"{len(sent)} messages sent - mark as Accepted when they respond!")
            
            for item in sent:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"✅ **{item['person_name']}** @ {item['company']}")
                    st.caption(f"Sent: {item.get('sent_date', '')[:10]}")
                
                with col2:
                    if st.button("🤝 Accepted", key=f"accept_{item['id']}", use_container_width=True):
                        for q in queue:
                            if q['id'] == item['id']:
                                q['status'] = 'accepted'
                                q['accepted_date'] = datetime.now().isoformat()
                        save_queue(queue)
                        
                        # Generate follow-up
                        person = {"name": item['person_name'], "company": item['company']}
                        followup = generate_message(person, "followup")
                        st.session_state['followup_message'] = followup
                        st.session_state['followup_for'] = item['person_name']
                        st.rerun()
                
                st.divider()
            
            # Show follow-up if just generated
            if 'followup_message' in st.session_state:
                st.success(f"🎉 {st.session_state['followup_for']} accepted!")
                st.subheader("📝 Send this follow-up message:")
                st.text_area("Follow-up:", value=st.session_state['followup_message'], height=200)
                
                if st.button("Add follow-up to queue"):
                    person = {"name": st.session_state['followup_for'], "company": ""}
                    add_to_queue(person, "followup")
                    del st.session_state['followup_message']
                    del st.session_state['followup_for']
                    st.rerun()
    
    with tab3:
        accepted = [q for q in queue if q['status'] == 'accepted']
        if not accepted:
            st.info("No accepted connections yet. Keep sending!")
        else:
            st.caption(f"🎉 {len(accepted)} people accepted your request!")
            for item in accepted:
                st.markdown(f"🤝 **{item['person_name']}** @ {item['company']}")
                st.caption(f"Accepted: {item.get('accepted_date', '')[:10]}")
                st.divider()
    
    with tab4:
        skipped = [q for q in queue if q['status'] == 'skipped']
        if not skipped:
            st.info("No skipped messages.")
        else:
            for item in skipped:
                st.markdown(f"⏭️ {item['person_name']} @ {item['company']}")


def show_stats():
    st.header("📊 Outreach Stats")
    
    queue = load_queue()
    companies = get_companies_from_jobs()
    
    pending = len([q for q in queue if q['status'] == 'pending'])
    sent = len([q for q in queue if q['status'] == 'sent'])
    accepted = len([q for q in queue if q['status'] == 'accepted'])
    skipped = len([q for q in queue if q['status'] == 'skipped'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Companies", len(companies))
    col2.metric("Pending", pending)
    col3.metric("Sent", sent)
    col4.metric("Accepted", accepted)
    col5.metric("Response Rate", f"{(accepted/sent*100):.0f}%" if sent > 0 else "N/A")
    
    st.divider()
    
    # By message type
    st.subheader("By Message Type")
    
    type_counts = {}
    for q in queue:
        t = q.get('message_type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    for t, count in type_counts.items():
        emoji = {"team": "👥", "hiring": "📢", "coffee": "☕", "followup": "🔄"}.get(t, "📝")
        st.write(f"{emoji} {t.title()}: {count}")


if __name__ == "__main__":
    main()
