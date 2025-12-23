#!/usr/bin/env python3
# notifier.py - Send email notifications for new jobs

import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === CREDENTIALS ===
SENDER_EMAIL = "steffimathew2901@gmail.com"
SENDER_PASSWORD = os.environ.get('GMAIL_PASSWORD', 'qhku yyhn srpr sodr')
RECIPIENT_EMAIL = "steffimathew2901@gmail.com"

def get_role_category(title):
    """Categorize roles - lower number = better fit"""
    title_lower = title.lower()
    
    if any(kw in title_lower for kw in ['product manager', 'product management', 'apm', 'associate product']):
        return 1, "🎯 Product Manager"
    if any(kw in title_lower for kw in ['program manager', 'project manager', 'tpm', 'technical program']):
        return 2, "📋 Program / Project Manager"
    if any(kw in title_lower for kw in ['data analyst', 'analytics', 'data scientist', 'business analyst', 'business intelligence', 'insights']):
        return 3, "📊 Data / Analytics"
    if any(kw in title_lower for kw in ['operations', 'strategy', 'gtm', 'go-to-market', 'marketing', 'growth', 'partnerships', 'bizops']):
        return 4, "📈 Ops / GTM / Marketing"
    if any(kw in title_lower for kw in ['research', 'ai safety', 'policy', 'trust', 'safety', 'responsible ai']):
        return 5, "🔬 Research / AI Safety"
    if any(kw in title_lower for kw in ['solutions engineer', 'sales engineer', 'technical account', 'implementation', 'support engineer']):
        return 6, "🔧 Solutions / Sales Engineering"
    if any(kw in title_lower for kw in ['software engineer', 'backend', 'frontend', 'full stack', 'fullstack', 'swe', 'developer', 'mobile engineer']):
        return 7, "💻 Software Engineering"
    if any(kw in title_lower for kw in ['engineer', 'infrastructure', 'platform', 'sre', 'devops', 'security', 'ml engineer', 'data engineer']):
        return 8, "⚙️ Other Engineering"
    if any(kw in title_lower for kw in ['recruiter', 'recruiting', 'hr ', 'human resources', 'people ops', 'talent', 'admin', 'coordinator']):
        return 9, "👥 HR / Recruiting / Admin"
    return 10, "📁 Other"


def send_job_alert(new_jobs, old_jobs=None, recipient=RECIPIENT_EMAIL):
    """Send email with jobs"""
    if not new_jobs and not old_jobs:
        print("No jobs to send.")
        return False
    
    jobs = new_jobs if new_jobs else []
    total = len(jobs)
    
    # Add category to each job
    for job in jobs:
        job['_cat_num'], job['_cat_name'] = get_role_category(job['title'])
    
    html = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.5;">
        <h1 style="color: #2563eb; font-size: 22px;">🚀 {total} Jobs - {datetime.now().strftime('%B %d, %Y %I:%M %p')}</h1>
        <div style="background: #dbeafe; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <strong>Entry-level (≤2 yrs) | US only</strong>
        </div>
    """
    
    tier_names = {
        1: "🔥 TIER 1 - Dream Companies", 
        2: "⭐ TIER 2 - Strong Companies", 
        3: "📋 TIER 3 - Other"
    }
    
    category_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for tier in [1, 2, 3]:
        tier_jobs = [j for j in jobs if j.get('tier') == tier]
        if not tier_jobs:
            continue
        
        bg_color = "#fef2f2" if tier == 1 else "#fffbeb" if tier == 2 else "#f9fafb"
        html += f"<h2 style='color: #1f2937; font-size: 16px; margin-top: 25px; background: {bg_color}; padding: 10px; border-radius: 5px;'>{tier_names[tier]} ({len(tier_jobs)})</h2>"
        
        for cat_num in category_order:
            cat_jobs = [j for j in tier_jobs if j.get('_cat_num') == cat_num]
            if not cat_jobs:
                continue
            
            cat_name = cat_jobs[0]['_cat_name']
            html += f"<h3 style='color: #059669; font-size: 14px; margin-top: 15px; margin-bottom: 8px;'>{cat_name} ({len(cat_jobs)})</h3>"
            
            cat_jobs_sorted = sorted(cat_jobs, key=lambda j: j.get('company', ''))
            
            for job in cat_jobs_sorted:
                border_color = "#ef4444" if tier == 1 else "#f59e0b" if tier == 2 else "#6b7280"
                html += f"""<div style="margin: 5px 0; padding: 8px 12px; background: #f9fafb; border-left: 3px solid {border_color}; font-size: 13px;">
                    <span style="font-weight: bold; color: #1f2937;">{job['title']}</span> — <span style="color: #059669;">{job['company']}</span><br>
                    <span style="color: #6b7280; font-size: 12px;">📍 {job.get('location', 'Unknown')[:35]} | <a href="{job['url']}" style="color: #2563eb;">Apply →</a></span>
                </div>"""
    
    html += """
        <hr style="margin-top: 30px; border: none; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 11px; text-align: center;">Job Search Agent 🤖 | Runs every hour via GitHub Actions</p>
    </body>
    </html>
    """
    
    # Plain text
    text = f"Found {total} jobs!\n\n"
    for job in jobs:
        text += f"• {job['title']} @ {job['company']}\n  {job['url']}\n\n"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 {total} Jobs Found - {datetime.now().strftime('%b %d %I:%M%p')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        print(f"✅ Email sent to {recipient} with {total} jobs!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == '__main__':
    pass
