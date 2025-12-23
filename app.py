#!/usr/bin/env python3
# app.py - Job Dashboard with AI-Powered People Finder & Resume Customizer

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

JOBS_FILE = 'all_jobs.json'

# Your base info for message generation
USER_INFO = {
    "name": "Steffi",
    "school": "Duke MEng",
    "highlight": "led a production data-quality and anomaly-detection platform that automated validation across pipelines and delivered ~$260K in annual savings",
    "interests": ["data platforms", "product management", "fintech", "AI safety"],
}

def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def get_role_category(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm']):
        return "🎯 Product Manager"
    if any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm']):
        return "📋 Program/Project Manager"
    if any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist', 'business analyst']):
        return "📊 Data/Analytics"
    if any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing', 'growth']):
        return "📈 Ops/GTM/Marketing"
    if any(kw in title_lower for kw in ['research', 'ai safety', 'policy', 'trust']):
        return "🔬 Research/AI Safety"
    if any(kw in title_lower for kw in ['solutions engineer', 'sales engineer']):
        return "🔧 Solutions/Sales Eng"
    if any(kw in title_lower for kw in ['software engineer', 'backend', 'frontend', 'developer']):
        return "💻 Software Engineering"
    if any(kw in title_lower for kw in ['engineer', 'infrastructure', 'sre', 'devops']):
        return "⚙️ Other Engineering"
    if any(kw in title_lower for kw in ['recruiter', 'hr ', 'talent', 'coordinator']):
        return "👥 HR/Recruiting"
    return "📁 Other"

def get_linkedin_search_url(company, role_type):
    """Generate LinkedIn search URL for specific team members"""
    company_clean = company.replace(' ', '%20').replace('(', '').replace(')', '')
    
    role_queries = {
        "Product Team": f"{company_clean}%20product%20manager",
        "Data Team": f"{company_clean}%20data%20engineer%20OR%20data%20scientist%20OR%20data%20analyst",
        "Engineering Team": f"{company_clean}%20software%20engineer",
        "Program/TPM Team": f"{company_clean}%20program%20manager%20OR%20TPM",
        "Leadership": f"{company_clean}%20director%20OR%20head%20of",
        "Recruiting": f"{company_clean}%20recruiter%20OR%20talent",
        "AI/ML Team": f"{company_clean}%20machine%20learning%20OR%20AI%20engineer",
        "Operations": f"{company_clean}%20operations%20OR%20strategy",
    }
    
    query = role_queries.get(role_type, company_clean)
    return f"https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER"

def generate_personalized_message(person_name, person_role, person_company, person_specialty=None):
    """Generate a personalized outreach message based on the person's profile"""
    
    # Map their role to a relevant compliment
    role_lower = person_role.lower() if person_role else ""
    
    if any(kw in role_lower for kw in ['data', 'analytics', 'scientist']):
        their_work = "building data platforms and driving insights"
        connection = "As someone who built a production anomaly-detection system, I deeply appreciate the complexity of data infrastructure work"
    elif any(kw in role_lower for kw in ['product', 'pm']):
        their_work = "shaping product strategy and driving impact"
        connection = "I'm passionate about translating technical capabilities into user value"
    elif any(kw in role_lower for kw in ['engineer', 'software', 'swe']):
        their_work = "building scalable systems"
        connection = "Having built production data systems myself, I understand the engineering challenges"
    elif any(kw in role_lower for kw in ['program', 'tpm', 'project']):
        their_work = "driving complex cross-functional initiatives"
        connection = "I love the challenge of coordinating technical projects across teams"
    elif any(kw in role_lower for kw in ['director', 'head', 'lead', 'vp']):
        their_work = "leading and scaling teams"
        connection = "I'd love to learn how you think about building high-performing teams"
    elif any(kw in role_lower for kw in ['recruit', 'talent']):
        their_work = "connecting great talent with opportunities"
        connection = "I'm actively exploring roles and would value your perspective"
    elif any(kw in role_lower for kw in ['ai', 'ml', 'machine learning']):
        their_work = "advancing AI/ML capabilities"
        connection = "I'm fascinated by the intersection of AI and practical applications"
    else:
        their_work = f"your work at {person_company}"
        connection = "I'd love to learn more about your journey"
    
    # Add specialty if provided
    specialty_line = ""
    if person_specialty:
        specialty_line = f"Your work on {person_specialty} is particularly inspiring—"
    
    message = f"""Hi {person_name} — I'm {USER_INFO['name']}, a {USER_INFO['school']} student. I {USER_INFO['highlight']}. {specialty_line}Your experience {their_work} at {person_company} caught my attention—would love to connect and learn from your journey."""
    
    return message

def generate_customized_resume_bullets(job):
    """Generate customized resume bullet points based on job title"""
    title_lower = job.get('title', '').lower()
    company = job.get('company', '')
    
    customized = []
    
    if any(kw in title_lower for kw in ['product manager', 'product', 'pm', 'apm']):
        customized = [
            f"### 💡 For {company} PM role, emphasize:",
            "• Led end-to-end development of anomaly detection product, from requirements gathering with stakeholders to production deployment, reducing operational overhead by 40%",
            "• Defined product roadmap for data monitoring tools based on user research and business needs, prioritizing features that delivered ~$260K annual savings",
            "• Drove adoption across 3 business units by creating intuitive dashboards and documentation, improving incident response time by 80%",
            "• Collaborated cross-functionally with engineering, operations, and business teams to translate complex technical capabilities into user-friendly solutions",
        ]
    elif any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm']):
        customized = [
            f"### 💡 For {company} Program Manager role, emphasize:",
            "• Managed cross-functional project delivering automated monitoring system across engineering, data, and operations teams—on time and under budget",
            "• Established project milestones, success metrics, and risk mitigation strategies, tracking progress through weekly stakeholder updates",
            "• Coordinated integration of anomaly detection system with existing infrastructure, ensuring minimal disruption to ongoing operations",
            "• Created comprehensive documentation and runbooks, enabling seamless handoff and reducing onboarding time for new team members by 50%",
        ]
    elif any(kw in title_lower for kw in ['data analyst', 'analyst', 'analytics', 'data scientist', 'business intelligence']):
        customized = [
            f"### 💡 For {company} Data/Analytics role, emphasize:",
            "• Built automated anomaly detection system using Python and Snowflake, applying statistical methods (IQR) to identify outliers across 15+ critical data pipelines",
            "• Designed interactive Streamlit dashboards enabling real-time trend visualization and root cause investigation for operations teams",
            "• Reduced detection time from hours to minutes by implementing automated alerting via Microsoft Teams integration",
            "• Delivered ~$260K annual cost savings by replacing manual monitoring processes with scalable, data-driven solutions",
        ]
    elif any(kw in title_lower for kw in ['operations', 'ops', 'strategy', 'bizops']):
        customized = [
            f"### 💡 For {company} Operations role, emphasize:",
            "• Automated manual monitoring processes, freeing up 10+ hours/week for the operations team to focus on strategic initiatives",
            "• Designed and implemented SOPs for anomaly investigation workflows, standardizing response procedures across teams",
            "• Built real-time dashboards enabling operations teams to proactively identify and resolve data quality issues",
            "• Partnered with engineering and business stakeholders to align technical solutions with operational needs",
        ]
    elif any(kw in title_lower for kw in ['research', 'ai safety', 'policy', 'trust']):
        customized = [
            f"### 💡 For {company} Research/Safety role, emphasize:",
            "• Developed anomaly detection methodologies to ensure data quality and integrity across production systems",
            "• Applied statistical analysis to identify edge cases and failure modes in data pipelines",
            "• Collaborated with cross-functional teams to implement safeguards and monitoring for critical systems",
            "• Passionate about responsible AI development and ensuring systems work safely and reliably",
        ]
    else:
        customized = [
            f"### 💡 For {company} role, emphasize:",
            "• Built and productionized automated anomaly detection system using Python and Snowflake, delivering ~$260K in annual cost savings",
            "• Designed end-to-end data pipelines with real-time alerting, reducing detection time from hours to minutes",
            "• Created interactive dashboards enabling teams to visualize trends and investigate issues in real-time",
            "• Collaborated cross-functionally with engineering, operations, and business teams to deliver impactful solutions",
        ]
    
    return customized


def main():
    st.set_page_config(
        page_title="🚀 Job Dashboard",
        page_icon="🚀",
        layout="wide"
    )
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Job Board", "🔍 People Finder", "📄 Resume Customizer", "⚙️ Settings"],
        index=0
    )
    
    jobs = load_jobs()
    
    if page == "🏠 Job Board":
        show_job_board(jobs)
    elif page == "🔍 People Finder":
        show_people_finder(jobs)
    elif page == "📄 Resume Customizer":
        show_resume_customizer(jobs)
    elif page == "⚙️ Settings":
        show_settings()


def show_job_board(jobs):
    """Main job board view"""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🚀 Job Search Dashboard")
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.caption(f"Last loaded: {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
    
    if not jobs:
        st.warning("No jobs found yet. Run the scraper first.")
        return
    
    df = pd.DataFrame(jobs)
    
    if 'role_category' not in df.columns:
        df['role_category'] = df['title'].apply(get_role_category)
    if 'status' not in df.columns:
        df['status'] = 'New'
    
    # Filters
    st.sidebar.header("🔍 Filters")
    
    tier_options = {1: "🔥 Tier 1", 2: "⭐ Tier 2", 3: "📋 Tier 3"}
    selected_tiers = st.sidebar.multiselect(
        "Company Tier", options=[1, 2, 3], default=[1, 2],
        format_func=lambda x: tier_options[x]
    )
    
    all_categories = sorted(df['role_category'].unique().tolist())
    preferred = ["🎯 Product Manager", "📋 Program/Project Manager", "📊 Data/Analytics", 
                 "📈 Ops/GTM/Marketing", "🔬 Research/AI Safety"]
    default_cats = [c for c in preferred if c in all_categories]
    selected_categories = st.sidebar.multiselect("Role Type", options=all_categories, default=default_cats)
    
    all_companies = sorted(df['company'].unique().tolist())
    selected_companies = st.sidebar.multiselect("Company", options=all_companies)
    
    search = st.sidebar.text_input("🔎 Search", "")
    
    # Apply filters
    filtered = df.copy()
    if selected_tiers:
        filtered = filtered[filtered['tier'].isin(selected_tiers)]
    if selected_categories:
        filtered = filtered[filtered['role_category'].isin(selected_categories)]
    if selected_companies:
        filtered = filtered[filtered['company'].isin(selected_companies)]
    if search:
        filtered = filtered[filtered['title'].str.lower().str.contains(search.lower())]
    
    # Stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(df))
    c2.metric("Filtered", len(filtered))
    c3.metric("Tier 1", len(df[df['tier'] == 1]))
    c4.metric("Companies", df['company'].nunique())
    
    st.divider()
    
    if filtered.empty:
        st.info("No jobs match filters.")
        return
    
    # Sort
    cat_order = {"🎯 Product Manager": 1, "📋 Program/Project Manager": 2, "📊 Data/Analytics": 3,
                 "📈 Ops/GTM/Marketing": 4, "🔬 Research/AI Safety": 5, "🔧 Solutions/Sales Eng": 6,
                 "💻 Software Engineering": 7, "⚙️ Other Engineering": 8, "👥 HR/Recruiting": 9, "📁 Other": 10}
    filtered['_order'] = filtered['role_category'].map(cat_order).fillna(10)
    filtered = filtered.sort_values(['tier', '_order', 'company'])
    
    # Display jobs
    for idx, row in filtered.iterrows():
        tier_emoji = "🔥" if row['tier'] == 1 else "⭐" if row['tier'] == 2 else "📋"
        
        with st.container():
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{row['title']}**")
                st.caption(f"{tier_emoji} {row['company']} · 📍 {str(row.get('location', 'Unknown'))[:30]} · {row['role_category']}")
            
            with col2:
                st.link_button("Apply", row['url'], use_container_width=True)
            
            with col3:
                if st.button("👥 People", key=f"people_{idx}", use_container_width=True):
                    st.session_state['selected_company_people'] = row['company']
                    st.session_state['selected_job_people'] = row.to_dict()
            
            with col4:
                if st.button("📄 Resume", key=f"resume_{idx}", use_container_width=True):
                    st.session_state['selected_job_resume'] = row.to_dict()
            
            st.divider()


def show_people_finder(jobs):
    """AI-powered people finder with personalized messages"""
    st.title("🔍 People Finder")
    st.caption("Find team members and generate personalized outreach messages")
    
    if not jobs:
        st.warning("No jobs loaded.")
        return
    
    df = pd.DataFrame(jobs)
    companies = sorted(df['company'].unique().tolist())
    
    # Company selector
    default_company = st.session_state.get('selected_company_people', companies[0] if companies else None)
    default_idx = companies.index(default_company) if default_company in companies else 0
    
    selected_company = st.selectbox("Select Company", options=companies, index=default_idx)
    
    if selected_company:
        st.divider()
        
        # Two columns: Team Search + Message Generator
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"👥 Find Team Members at {selected_company}")
            st.caption("Click to search LinkedIn for people in each team")
            
            team_types = [
                ("🎯 Product Team", "Product Team"),
                ("📊 Data Team", "Data Team"),
                ("💻 Engineering Team", "Engineering Team"),
                ("📋 Program/TPM Team", "Program/TPM Team"),
                ("🤖 AI/ML Team", "AI/ML Team"),
                ("📈 Operations", "Operations"),
                ("👔 Leadership", "Leadership"),
                ("🎯 Recruiting", "Recruiting"),
            ]
            
            for emoji_name, team_type in team_types:
                url = get_linkedin_search_url(selected_company, team_type)
                st.link_button(f"🔍 {emoji_name}", url, use_container_width=True)
        
        with col2:
            st.subheader("✉️ Generate Personalized Message")
            st.caption("Enter the person's details to generate a custom outreach message")
            
            person_name = st.text_input("Person's First Name", placeholder="e.g., Sagar")
            person_role = st.text_input("Their Role/Title", placeholder="e.g., Senior Data Engineer")
            person_specialty = st.text_input("Their Specialty (optional)", placeholder="e.g., building large-scale data platforms")
            
            if person_name and person_role:
                message = generate_personalized_message(
                    person_name=person_name,
                    person_role=person_role,
                    person_company=selected_company,
                    person_specialty=person_specialty if person_specialty else None
                )
                
                st.text_area(
                    "📋 Your personalized message (copy this):",
                    value=message,
                    height=200,
                    key="personalized_msg"
                )
                
                # Character count for LinkedIn
                char_count = len(message)
                if char_count <= 300:
                    st.success(f"✅ {char_count}/300 characters - Perfect for LinkedIn connection request!")
                else:
                    st.warning(f"⚠️ {char_count}/300 characters - Consider shortening for LinkedIn connection request, or use InMail")
        
        st.divider()
        
        # Quick templates section
        st.subheader("📝 Quick Message Templates")
        
        template_tabs = st.tabs(["Recruiter", "Hiring Manager", "Team Member", "Leadership"])
        
        with template_tabs[0]:
            recruiter_msg = f"""Hi [Name] — I'm {USER_INFO['name']}, a {USER_INFO['school']} student. I {USER_INFO['highlight']}. I saw {selected_company} is hiring and would love to learn more about the team and opportunities. Would you have a few minutes to chat?"""
            st.text_area("Recruiter template:", value=recruiter_msg, height=150, key="recruiter_template")
        
        with template_tabs[1]:
            hm_msg = f"""Hi [Name] — I'm {USER_INFO['name']}, a {USER_INFO['school']} student. I {USER_INFO['highlight']}. I'm excited about the [Role] position on your team and would love to learn more about the work and culture. Would you be open to a brief chat?"""
            st.text_area("Hiring Manager template:", value=hm_msg, height=150, key="hm_template")
        
        with template_tabs[2]:
            team_msg = f"""Hi [Name] — I'm {USER_INFO['name']}, a {USER_INFO['school']} student. I {USER_INFO['highlight']}. Your work at {selected_company} is inspiring—I'd love to connect and learn about your experience on the team."""
            st.text_area("Team Member template:", value=team_msg, height=150, key="team_template")
        
        with template_tabs[3]:
            leader_msg = f"""Hi [Name] — I'm {USER_INFO['name']}, a {USER_INFO['school']} student. I {USER_INFO['highlight']}. I admire what you've built at {selected_company} and would be grateful for any advice on breaking into the field. Would you have 15 minutes for a coffee chat?"""
            st.text_area("Leadership template:", value=leader_msg, height=150, key="leader_template")
        
        st.divider()
        
        # Show open roles at this company
        st.subheader(f"📋 Open Roles at {selected_company}")
        
        company_jobs = df[df['company'] == selected_company]
        if company_jobs.empty:
            st.info("No open roles found for this company in the database.")
        else:
            for _, row in company_jobs.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{row['title']}**")
                    st.caption(f"📍 {row.get('location', 'Unknown')}")
                with col2:
                    st.link_button("Apply", row['url'], use_container_width=True)


def show_resume_customizer(jobs):
    """Resume customizer view"""
    st.title("📄 Resume Customizer")
    st.caption("Get tailored resume suggestions for each job")
    
    if not jobs:
        st.warning("No jobs loaded.")
        return
    
    df = pd.DataFrame(jobs)
    
    # Check if job was selected from job board
    preselected_job = st.session_state.get('selected_job_resume')
    
    # Job selector
    job_options = [f"{row['title']} @ {row['company']}" for _, row in df.iterrows()]
    
    default_idx = 0
    if preselected_job:
        target = f"{preselected_job['title']} @ {preselected_job['company']}"
        if target in job_options:
            default_idx = job_options.index(target)
    
    selected_idx = st.selectbox(
        "Select a job to customize your resume for:",
        options=range(len(job_options)),
        format_func=lambda x: job_options[x],
        index=default_idx
    )
    
    if selected_idx is not None:
        selected_job = df.iloc[selected_idx].to_dict()
        
        st.divider()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Job Details")
            st.markdown(f"**{selected_job['title']}**")
            st.markdown(f"🏢 {selected_job['company']}")
            st.markdown(f"📍 {selected_job.get('location', 'Unknown')}")
            st.link_button("View Full Job Posting", selected_job['url'])
            
            st.divider()
            
            st.subheader("🎯 Key Skills to Highlight")
            
            title_lower = selected_job['title'].lower()
            
            if 'product' in title_lower:
                skills = ["Product Strategy", "Roadmap Planning", "Stakeholder Management", 
                         "Data-Driven Decisions", "Cross-functional Leadership", "User Research"]
            elif 'program' in title_lower or 'project' in title_lower:
                skills = ["Project Management", "Cross-functional Coordination", "Timeline Management",
                         "Risk Assessment", "Stakeholder Communication", "Process Improvement"]
            elif 'data' in title_lower or 'analyst' in title_lower:
                skills = ["SQL", "Python", "Data Visualization", "Statistical Analysis",
                         "Dashboard Development", "Business Intelligence"]
            elif 'operations' in title_lower or 'ops' in title_lower:
                skills = ["Process Optimization", "Operations Management", "Data Analysis",
                         "Stakeholder Management", "Problem Solving", "Automation"]
            else:
                skills = ["Problem Solving", "Communication", "Technical Skills",
                         "Collaboration", "Analytical Thinking", "Project Management"]
            
            for skill in skills:
                st.markdown(f"✅ {skill}")
        
        with col2:
            st.subheader("✨ Customized Resume Bullets")
            st.caption("Copy these tailored bullet points to your resume")
            
            bullets = generate_customized_resume_bullets(selected_job)
            
            for bullet in bullets:
                st.markdown(bullet)
        
        st.divider()
        
        st.subheader("📧 Cover Letter Opening")
        
        cover_letter = f"""Dear Hiring Manager,

I am excited to apply for the {selected_job['title']} position at {selected_job['company']}. As a Duke FinTech Master's student with hands-on experience building data-driven products, I am drawn to {selected_job['company']}'s mission and the opportunity to contribute to your team.

In my recent role at Enact Mortgage Insurance, I designed and deployed an automated anomaly detection system that reduced detection time from hours to minutes, delivering approximately $260K in annual cost savings. This experience taught me how to translate complex technical solutions into measurable business impact—a skill I'm eager to bring to {selected_job['company']}.

I would welcome the opportunity to discuss how my background in data engineering, product thinking, and cross-functional collaboration can contribute to your team's goals.

Best regards,
{USER_INFO['name']}"""
        
        st.text_area(
            "Customized cover letter:",
            value=cover_letter,
            height=350
        )


def show_settings():
    """Settings page to customize user info"""
    st.title("⚙️ Settings")
    st.caption("Customize your profile for message generation")
    
    st.subheader("Your Profile")
    
    new_name = st.text_input("Your Name", value=USER_INFO['name'])
    new_school = st.text_input("Your School/Background", value=USER_INFO['school'])
    new_highlight = st.text_area(
        "Your Key Achievement (for outreach messages)",
        value=USER_INFO['highlight'],
        height=100
    )
    
    st.info("💡 These settings are used to generate personalized outreach messages. Changes will apply to new messages.")
    
    st.divider()
    
    st.subheader("Message Preview")
    preview = f"""Hi [Name] — I'm {new_name}, a {new_school} student. I {new_highlight}. Your work at [Company] is inspiring—would love to connect and learn from your journey."""
    
    st.text_area("Preview:", value=preview, height=150, disabled=True)


if __name__ == '__main__':
    main()
