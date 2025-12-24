#!/usr/bin/env python3
"""Job Dashboard with NEW badges"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

JOBS_FILE = 'all_jobs.json'

def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def main():
    st.set_page_config(page_title="🚀 Job Dashboard", page_icon="🚀", layout="wide")
    st.title("🚀 Job Dashboard")
    
    jobs = load_jobs()
    
    if not jobs:
        st.warning("No jobs found! Run the scraper first.")
        return
    
    df = pd.DataFrame(jobs)
    
    st.sidebar.header("🔍 Filters")
    
    tiers = st.sidebar.multiselect(
        "Tier",
        options=[1, 2, 3],
        default=[1, 2],
        format_func=lambda x: {1: "🔥 Tier 1", 2: "⭐ Tier 2", 3: "📋 Tier 3"}[x]
    )
    
    show_new_only = st.sidebar.checkbox("🆕 Show NEW jobs only", value=False)
    
    companies = sorted(df['company'].unique())
    selected_companies = st.sidebar.multiselect("Companies", companies)
    
    filtered = df[df['tier'].isin(tiers)]
    
    if show_new_only and 'is_new' in df.columns:
        filtered = filtered[filtered['is_new'] == True]
    
    if selected_companies:
        filtered = filtered[filtered['company'].isin(selected_companies)]
    
    col1, col2, col3, col4 = st.columns(4)
    
    new_count = len(df[df['is_new'] == True]) if 'is_new' in df.columns else 0
    
    col1.metric("Total Jobs", len(df))
    col2.metric("🆕 New (48h)", new_count)
    col3.metric("Showing", len(filtered))
    col4.metric("Companies", df['company'].nunique())
    
    st.divider()
    
    for _, row in filtered.iterrows():
        tier_emoji = {1: "🔥", 2: "⭐", 3: "📋"}.get(row.get('tier', 3), "📋")
        is_new = row.get('is_new', False)
        new_badge = " 🆕" if is_new else ""
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"**{row['title']}**{new_badge}")
            location = str(row.get('location', 'Unknown'))[:40]
            st.caption(f"{tier_emoji} {row['company']} · 📍 {location}")
        
        with col2:
            st.link_button("Apply →", row.get('url', '#'))
        
        st.divider()

if __name__ == '__main__':
    main()
