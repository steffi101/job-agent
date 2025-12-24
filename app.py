#!/usr/bin/env python3
"""Job Dashboard with NEW badges and all filters"""

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
    if any(kw in title_lower for kw in ['data analyst', 'analytics', 'business analyst']):
        return "📊 Data Analyst"
    if any(kw in title_lower for kw in ['data scientist', 'machine learning', 'ml engineer']):
        return "🤖 Data Science/ML"
    if any(kw in title_lower for kw in ['data engineer', 'data platform']):
        return "🔧 Data Engineer"
    if any(kw in title_lower for kw in ['software engineer', 'backend', 'frontend', 'fullstack']):
        return "💻 Software Engineer"
    if any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'marketing', 'growth']):
        return "📈 Ops/Strategy/Marketing"
    if any(kw in title_lower for kw in ['research', 'scientist']):
        return "🔬 Research"
    return "📁 Other"

def main():
    st.set_page_config(page_title="🚀 Job Dashboard", page_icon="🚀", layout="wide")
    st.title("🚀 Job Dashboard")
    
    jobs = load_jobs()
    
    if not jobs:
        st.warning("No jobs found! Run the scraper first.")
        return
    
    df = pd.DataFrame(jobs)
    
    # Add role category
    df['role_category'] = df['title'].apply(get_role_category)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Tier filter
    tiers = st.sidebar.multiselect(
        "Tier",
        options=[1, 2, 3],
        default=[1, 2],
        format_func=lambda x: {1: "🔥 Tier 1", 2: "⭐ Tier 2", 3: "📋 Tier 3"}[x]
    )
    if not tiers:
        tiers = [1, 2, 3]
    
    # Role category filter
    role_categories = sorted(df['role_category'].unique())
    selected_roles = st.sidebar.multiselect("Role Type", role_categories)
    
    # New only filter
    show_new_only = st.sidebar.checkbox("🆕 Show NEW jobs only", value=False)
    
    # Company filter
    companies = sorted(df['company'].unique())
    selected_companies = st.sidebar.multiselect("Companies", companies)
    
    # Apply filters
    filtered = df[df['tier'].isin(tiers)]
    
    if selected_roles:
        filtered = filtered[filtered['role_category'].isin(selected_roles)]
    
    if show_new_only and 'is_new' in filtered.columns:
        filtered = filtered[filtered['is_new'] == True]
    
    if selected_companies:
        filtered = filtered[filtered['company'].isin(selected_companies)]
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    new_count = 0
    if 'is_new' in df.columns:
        new_count = len(df[df['is_new'] == True])
    
    col1.metric("Total Jobs", len(df))
    col2.metric("🆕 New (48h)", new_count)
    col3.metric("Showing", len(filtered))
    col4.metric("Companies", df['company'].nunique())
    
    st.divider()
    
    # Show jobs
    for idx, row in filtered.iterrows():
        tier_emoji = {1: "🔥", 2: "⭐", 3: "📋"}.get(row.get('tier', 3), "📋")
        is_new = row.get('is_new', False) if 'is_new' in row else False
        new_badge = " 🆕" if is_new else ""
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{row['title']}**{new_badge}")
            location = str(row.get('location', 'Unknown'))[:40]
            st.caption(f"{tier_emoji} {row['company']} · 📍 {location} · {row['role_category']}")
        
        with col2:
            st.link_button("Apply →", row.get('url', '#'))
        
        st.divider()

if __name__ == '__main__':
    main()
