#!/usr/bin/env python3
# app.py - Streamlit Job Dashboard

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

JOBS_FILE = 'all_jobs.json'

def load_jobs():
    """Load all jobs from JSON file"""
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    """Save jobs to JSON file"""
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2, default=str)

def get_role_category(title):
    """Categorize roles"""
    title_lower = title.lower()
    
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm', 'associate product']):
        return "🎯 Product Manager"
    if any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm', 'technical program']):
        return "📋 Program/Project Manager"
    if any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist', 'business analyst', 'business intelligence']):
        return "📊 Data/Analytics"
    if any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing', 'growth', 'partnerships']):
        return "📈 Ops/GTM/Marketing"
    if any(kw in title_lower for kw in ['research', 'ai safety', 'policy', 'trust', 'safety']):
        return "🔬 Research/AI Safety"
    if any(kw in title_lower for kw in ['solutions engineer', 'sales engineer', 'technical account']):
        return "🔧 Solutions/Sales Eng"
    if any(kw in title_lower for kw in ['software engineer', 'backend', 'frontend', 'full stack', 'developer', 'mobile']):
        return "💻 Software Engineering"
    if any(kw in title_lower for kw in ['engineer', 'infrastructure', 'platform', 'sre', 'devops', 'ml engineer']):
        return "⚙️ Other Engineering"
    if any(kw in title_lower for kw in ['recruiter', 'recruiting', 'hr ', 'talent', 'admin', 'coordinator']):
        return "👥 HR/Recruiting"
    return "📁 Other"

def main():
    st.set_page_config(
        page_title="Job Search Dashboard",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 Job Search Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
    
    # Load jobs
    jobs = load_jobs()
    
    if not jobs:
        st.warning("No jobs found. Run the scraper first: `python3 run_agent.py`")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(jobs)
    
    # Add role category if not present
    if 'role_category' not in df.columns:
        df['role_category'] = df['title'].apply(get_role_category)
    
    # Add status if not present
    if 'status' not in df.columns:
        df['status'] = 'New'
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Tier filter
    tier_options = {1: "🔥 Tier 1 - Dream", 2: "⭐ Tier 2 - Strong", 3: "📋 Tier 3 - Other"}
    selected_tiers = st.sidebar.multiselect(
        "Company Tier",
        options=[1, 2, 3],
        default=[1, 2],
        format_func=lambda x: tier_options[x]
    )
    
    # Role category filter
    all_categories = df['role_category'].unique().tolist()
    preferred_categories = [
        "🎯 Product Manager",
        "📋 Program/Project Manager", 
        "📊 Data/Analytics",
        "📈 Ops/GTM/Marketing",
        "🔬 Research/AI Safety"
    ]
    default_categories = [c for c in preferred_categories if c in all_categories]
    
    selected_categories = st.sidebar.multiselect(
        "Role Type",
        options=all_categories,
        default=default_categories
    )
    
    # Company filter
    all_companies = sorted(df['company'].unique().tolist())
    selected_companies = st.sidebar.multiselect(
        "Company (leave empty for all)",
        options=all_companies,
        default=[]
    )
    
    # Status filter
    status_options = ['New', 'Applied', 'Skipped', 'All']
    selected_status = st.sidebar.selectbox("Status", status_options, index=0)
    
    # Search box
    search_term = st.sidebar.text_input("🔎 Search job titles", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_tiers:
        filtered_df = filtered_df[filtered_df['tier'].isin(selected_tiers)]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['role_category'].isin(selected_categories)]
    
    if selected_companies:
        filtered_df = filtered_df[filtered_df['company'].isin(selected_companies)]
    
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(search_term.lower())]
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jobs", len(df))
    col2.metric("Filtered", len(filtered_df))
    col3.metric("Tier 1", len(df[df['tier'] == 1]))
    col4.metric("New", len(df[df['status'] == 'New']))
    
    st.divider()
    
    # Display jobs
    if filtered_df.empty:
        st.info("No jobs match your filters.")
        return
    
    # Sort by tier, then role category
    category_order = {
        "🎯 Product Manager": 1,
        "📋 Program/Project Manager": 2,
        "📊 Data/Analytics": 3,
        "📈 Ops/GTM/Marketing": 4,
        "🔬 Research/AI Safety": 5,
        "🔧 Solutions/Sales Eng": 6,
        "💻 Software Engineering": 7,
        "⚙️ Other Engineering": 8,
        "👥 HR/Recruiting": 9,
        "📁 Other": 10
    }
    filtered_df['_cat_order'] = filtered_df['role_category'].map(category_order).fillna(10)
    filtered_df = filtered_df.sort_values(['tier', '_cat_order', 'company'])
    
    # Display as cards
    for idx, row in filtered_df.iterrows():
        tier_emoji = "🔥" if row['tier'] == 1 else "⭐" if row['tier'] == 2 else "📋"
        
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.markdown(f"**{row['title']}**")
                st.caption(f"{tier_emoji} {row['company']} · 📍 {row.get('location', 'Unknown')[:30]} · {row['role_category']}")
            
            with col2:
                st.link_button("Apply →", row['url'], use_container_width=True)
            
            with col3:
                status_key = f"status_{idx}"
                new_status = st.selectbox(
                    "Status",
                    options=['New', 'Applied', 'Skipped'],
                    index=['New', 'Applied', 'Skipped'].index(row.get('status', 'New')),
                    key=status_key,
                    label_visibility="collapsed"
                )
                if new_status != row.get('status', 'New'):
                    # Update status in original data
                    for job in jobs:
                        if job.get('url') == row['url']:
                            job['status'] = new_status
                    save_jobs(jobs)
            
            st.divider()

if __name__ == '__main__':
    main()
