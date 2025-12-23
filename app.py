#!/usr/bin/env python3
# app.py - Job Dashboard with People Finder & Resume Customizer

import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime

JOBS_FILE = 'all_jobs.json'
RESUME_FILE = 'resume_base.txt'

def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2, default=str)

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

def get_linkedin_search_url(company, role="recruiter"):
    """Generate LinkedIn search URL for people at a company"""
    company_clean = company.replace(' ', '%20')
    if role == "recruiter":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_clean}%20recruiter&origin=GLOBAL_SEARCH_HEADER"
    elif role == "hiring_manager":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_clean}%20hiring%20manager&origin=GLOBAL_SEARCH_HEADER"
    elif role == "pm":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_clean}%20product%20manager&origin=GLOBAL_SEARCH_HEADER"
    elif role == "data":
        return f"https://www.linkedin.com/search/results/people/?keywords={company_clean}%20data%20analyst&origin=GLOBAL_SEARCH_HEADER"
    else:
        return f"https://www.linkedin.com/search/results/people/?keywords={company_clean}&origin=GLOBAL_SEARCH_HEADER"

def generate_outreach_message(job, user_name="Steffi"):
    """Generate a personalized outreach message"""
    company = job.get('company', 'your company')
    title = job.get('title', 'the role')
    
    message = f"""Hi [Name],

I came across the {title} role at {company} and I'm very excited about the opportunity! 

I'm a Duke FinTech Master's student with experience in data engineering and product development. At Enact Mortgage Insurance, I built an anomaly detection system that reduced detection time from hours to minutes and saved ~$260K annually.

I'd love to learn more about the team and the role. Would you have 15 minutes for a quick chat?

Best,
{user_name}"""
    
    return message

def generate_customized_resume_bullets(job):
    """Generate customized resume bullet points based on job title"""
    title_lower = job.get('title', '').lower()
    company = job.get('company', '')
    
    base_bullets = {
        'anomaly_detection': "Built and productionized automated anomaly detection system using Python and Snowflake, reducing detection time from hours to minutes and delivering ~$260K in annual cost savings",
        'data_pipeline': "Designed and implemented end-to-end data pipelines monitoring 15+ critical metrics with real-time alerting via Microsoft Teams integration",
        'dashboard': "Created interactive Streamlit dashboards enabling operations teams to visualize trends and investigate anomalies in real-time",
        'cross_functional': "Collaborated cross-functionally with engineering, operations, and business teams to define requirements and deliver impactful solutions",
        'ml_project': "Developed machine learning models for volatility forecasting using LSTM neural networks, achieving improved prediction accuracy",
    }
    
    customized = []
    
    if any(kw in title_lower for kw in ['product manager', 'product', 'pm']):
        customized = [
            f"💡 **For {company} PM role, emphasize:**",
            "• Led end-to-end development of anomaly detection product, from requirements gathering to deployment, reducing operational overhead by 40%",
            "• Collaborated with stakeholders to prioritize features and define product roadmap for data monitoring tools",
            "• Drove adoption of automated alerting system across 3 business units, improving incident response time by 80%",
            base_bullets['cross_functional'],
        ]
    elif any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm']):
        customized = [
            f"💡 **For {company} Program Manager role, emphasize:**",
            "• Managed cross-functional project delivering automated monitoring system on time and under budget",
            "• Coordinated between engineering, data, and operations teams to ensure seamless integration",
            "• Established project milestones and KPIs, tracking progress through weekly stakeholder updates",
            base_bullets['cross_functional'],
        ]
    elif any(kw in title_lower for kw in ['data analyst', 'analyst', 'analytics', 'data scientist']):
        customized = [
            f"💡 **For {company} Data/Analytics role, emphasize:**",
            base_bullets['anomaly_detection'],
            base_bullets['data_pipeline'],
            base_bullets['dashboard'],
            "• Applied statistical analysis (IQR methodology) to identify outliers and anomalies in large datasets",
        ]
    elif any(kw in title_lower for kw in ['operations', 'ops', 'strategy']):
        customized = [
            f"💡 **For {company} Operations role, emphasize:**",
            "• Automated manual monitoring processes, freeing up 10+ hours/week for the operations team",
            base_bullets['anomaly_detection'],
            "• Developed SOPs and documentation for anomaly investigation workflows",
            base_bullets['cross_functional'],
        ]
    else:
        customized = [
            f"💡 **For {company} role, emphasize:**",
            base_bullets['anomaly_detection'],
            base_bullets['data_pipeline'],
            base_bullets['cross_functional'],
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
        ["🏠 Job Board", "🔍 People Finder", "📄 Resume Customizer"],
        index=0
    )
    
    jobs = load_jobs()
    
    if page == "🏠 Job Board":
        show_job_board(jobs)
    elif page == "🔍 People Finder":
        show_people_finder(jobs)
    elif page == "📄 Resume Customizer":
        show_resume_customizer(jobs)


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
        "Company Tier",
        options=[1, 2, 3],
        default=[1, 2],
        format_func=lambda x: tier_options[x]
    )
    
    all_categories = sorted(df['role_category'].unique().tolist())
    preferred = ["🎯 Product Manager", "📋 Program/Project Manager", "📊 Data/Analytics", 
                 "📈 Ops/GTM/Marketing", "🔬 Research/AI Safety"]
    default_cats = [c for c in preferred if c in all_categories]
    
    selected_categories = st.sidebar.multiselect(
        "Role Type", options=all_categories, default=default_cats
    )
    
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
                # Link to People Finder for this company
                if st.button("👥 Find People", key=f"people_{idx}"):
                    st.session_state['selected_company'] = row['company']
                    st.session_state['selected_job'] = row.to_dict()
                    st.switch_page = "🔍 People Finder"
            
            with col4:
                if st.button("📄 Customize", key=f"resume_{idx}"):
                    st.session_state['selected_job_resume'] = row.to_dict()
            
            st.divider()


def show_people_finder(jobs):
    """People finder view"""
    st.title("🔍 People Finder")
    st.caption("Find recruiters and hiring managers to reach out to")
    
    if not jobs:
        st.warning("No jobs loaded.")
        return
    
    df = pd.DataFrame(jobs)
    companies = sorted(df['company'].unique().tolist())
    
    # Company selector
    selected_company = st.selectbox(
        "Select Company",
        options=companies,
        index=0 if not st.session_state.get('selected_company') else 
              companies.index(st.session_state.get('selected_company')) if st.session_state.get('selected_company') in companies else 0
    )
    
    if selected_company:
        st.subheader(f"Find People at {selected_company}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Search LinkedIn")
            
            st.link_button(
                "🔍 Find Recruiters",
                get_linkedin_search_url(selected_company, "recruiter"),
                use_container_width=True
            )
            
            st.link_button(
                "🔍 Find Hiring Managers",
                get_linkedin_search_url(selected_company, "hiring_manager"),
                use_container_width=True
            )
            
            st.link_button(
                "🔍 Find Product Managers",
                get_linkedin_search_url(selected_company, "pm"),
                use_container_width=True
            )
            
            st.link_button(
                "🔍 Find Data Analysts",
                get_linkedin_search_url(selected_company, "data"),
                use_container_width=True
            )
        
        with col2:
            st.markdown("### 📧 Outreach Template")
            
            # Get a job from this company for context
            company_jobs = df[df['company'] == selected_company]
            if not company_jobs.empty:
                sample_job = company_jobs.iloc[0].to_dict()
                message = generate_outreach_message(sample_job)
                
                st.text_area(
                    "Copy this message:",
                    value=message,
                    height=300,
                    key="outreach_msg"
                )
                
                st.info("💡 **Tips:**\n- Personalize [Name] with the person's actual name\n- Mention something specific about their work\n- Keep it short and focused")
        
        # Show jobs at this company
        st.divider()
        st.subheader(f"📋 Open Roles at {selected_company}")
        
        company_jobs = df[df['company'] == selected_company]
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
    
    # Job selector
    job_options = [f"{row['title']} @ {row['company']}" for _, row in df.iterrows()]
    
    selected_idx = st.selectbox(
        "Select a job to customize your resume for:",
        options=range(len(job_options)),
        format_func=lambda x: job_options[x]
    )
    
    if selected_idx is not None:
        selected_job = df.iloc[selected_idx].to_dict()
        
        st.divider()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"📋 Job Details")
            st.markdown(f"**{selected_job['title']}**")
            st.markdown(f"🏢 {selected_job['company']}")
            st.markdown(f"📍 {selected_job.get('location', 'Unknown')}")
            st.link_button("View Full Job Posting", selected_job['url'])
        
        with col2:
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
            else:
                skills = ["Problem Solving", "Communication", "Technical Skills",
                         "Collaboration", "Analytical Thinking"]
            
            for skill in skills:
                st.markdown(f"• {skill}")
        
        st.divider()
        
        st.subheader("✨ Customized Resume Bullets")
        st.caption("Use these tailored bullet points in your resume")
        
        bullets = generate_customized_resume_bullets(selected_job)
        
        for bullet in bullets:
            st.markdown(bullet)
        
        st.divider()
        
        st.subheader("📧 Cover Letter Opening")
        
        cover_letter = f"""Dear Hiring Manager,

I am excited to apply for the {selected_job['title']} position at {selected_job['company']}. As a Duke FinTech Master's student with hands-on experience building data-driven products, I am drawn to {selected_job['company']}'s mission and the opportunity to contribute to your team.

In my recent role at Enact Mortgage Insurance, I designed and deployed an automated anomaly detection system that reduced detection time from hours to minutes, delivering approximately $260K in annual cost savings. This experience taught me how to translate complex technical solutions into measurable business impact—a skill I'm eager to bring to {selected_job['company']}.

[Continue with specific reasons why you're interested in this role and company...]
"""
        
        st.text_area(
            "Customized cover letter opening:",
            value=cover_letter,
            height=300
        )


if __name__ == '__main__':
    main()
