#!/usr/bin/env python3
# app.py - Streamlit Job Dashboard

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

JOBS_FILE = 'all_jobs.json'

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

def main():
    st.set_page_config(
        page_title="🚀 Job Dashboard",
        page_icon="🚀",
        layout="wide"
    )
    
    # Header with refresh button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🚀 Job Search Dashboard")
    with col2:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    st.caption(f"Last loaded: {datetime.now().strftime('%B %d, %Y %I:%M %p')}")
    
    # Load jobs
    jobs = load_jobs()
    
    if not jobs:
        st.warning("No jobs found yet. Wait for the hourly scrape or run manually.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(jobs)
    
    if 'role_category' not in df.columns:
        df['role_category'] = df['title'].apply(get_role_category)
    
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
    
    # Role filter
    all_categories = sorted(df['role_category'].unique().tolist())
    preferred = ["🎯 Product Manager", "📋 Program/Project Manager", "📊 Data/Analytics", 
                 "📈 Ops/GTM/Marketing", "🔬 Research/AI Safety"]
    default_categories = [c for c in preferred if c in all_categories]
    
    selected_categories = st.sidebar.multiselect(
        "Role Type",
        options=all_categories,
        default=default_categories
    )
    
    # Company filter
    all_companies = sorted(df['company'].unique().tolist())
    selected_companies = st.sidebar.multiselect(
        "Company (leave empty for all)",
        options=all_companies
    )
    
    # Search
    search = st.sidebar.text_input("🔎 Search titles", "")
    
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
    c1.metric("Total Jobs", len(df))
    c2.metric("Filtered", len(filtered))
    c3.metric("Tier 1", len(df[df['tier'] == 1]))
    c4.metric("Companies", df['company'].nunique())
    
    st.divider()
    
    if filtered.empty:
        st.info("No jobs match your filters.")
        return
    
    # Sort
    cat_order = {"🎯 Product Manager": 1, "📋 Program/Project Manager": 2, "📊 Data/Analytics": 3,
                 "📈 Ops/GTM/Marketing": 4, "🔬 Research/AI Safety": 5, "🔧 Solutions/Sales Eng": 6,
                 "💻 Software Engineering": 7, "⚙️ Other Engineering": 8, "👥 HR/Recruiting": 9, "📁 Other": 10}
    filtered['_order'] = filtered['role_category'].map(cat_order).fillna(10)
    filtered = filtered.sort_values(['tier', '_order', 'company'])
    
    # Display
    for _, row in filtered.iterrows():
        tier_emoji = "🔥" if row['tier'] == 1 else "⭐" if row['tier'] == 2 else "📋"
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{row['title']}**")
            st.caption(f"{tier_emoji} {row['company']} · 📍 {str(row.get('location', 'Unknown'))[:35]} · {row['role_category']}")
        with col2:
            st.link_button("Apply →", row['url'], use_container_width=True)
        st.divider()

if __name__ == '__main__':
    main()
