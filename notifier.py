#!/usr/bin/env python3
# notifier.py - Send email notifications for new jobs

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === YOUR CREDENTIALS ===
SENDER_EMAIL = "steffimathew2901@gmail.com"
SENDER_PASSWORD = "qhku yyhn srpr sodr"
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


def build_jobs_section(jobs, section_title, is_new=True):
    """Build HTML for a section of jobs"""
    if not jobs:
        return ""
    
    # Add category to each job
    for job in jobs:
        job['_cat_num'], job['_cat_name'] = get_role_category(job['title'])
    
    tier_names = {
        1: "🔥 TIER 1 - Dream Companies", 
        2: "⭐ TIER 2 - Strong Companies", 
        3: "📋 TIER 3 - Other"
    }
    
    category_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    html = ""
    
    if not is_new:
        # Collapsible section for old jobs
        html += f"""
        <details style="margin-top: 30px; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px;">
            <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: #6b7280; padding: 10px;">
                📂 {section_title} ({len(jobs)} jobs) — Click to expand
            </summary>
            <div style="padding-top: 15px;">
        """
    else:
        html += f"<h2 style='color: #059669; font-size: 18px; margin-top: 25px;'>🆕 {section_title} ({len(jobs)} jobs)</h2>"
    
    for tier in [1, 2, 3]:
        tier_jobs = [j for j in jobs if j.get('tier') == tier]
        if not tier_jobs:
            continue
        
        bg_color = "#fef2f2" if tier == 1 else "#fffbeb" if tier == 2 else "#f9fafb"
        html += f"<h3 style='color: #1f2937; font-size: 15px; margin-top: 20px; background: {bg_color}; padding: 8px; border-radius: 5px;'>{tier_names[tier]} ({len(tier_jobs)})</h3>"
        
        for cat_num in category_order:
            cat_jobs = [j for j in tier_jobs if j.get('_cat_num') == cat_num]
            if not cat_jobs:
                continue
            
            cat_name = cat_jobs[0]['_cat_name']
            html += f"<h4 style='color: #059669; font-size: 13px; margin-top: 15px; margin-bottom: 8px;'>{cat_name} ({len(cat_jobs)})</h4>"
            
            cat_jobs_sorted = sorted(cat_jobs, key=lambda j: j.get('company', ''))
            
            for job in cat_jobs_sorted:
                border_color = "#ef4444" if tier == 1 else "#f59e0b" if tier == 2 else "#6b7280"
                html += f"""<div style="margin: 5px 0; padding: 8px 12px; background: #f9fafb; border-left: 3px solid {border_color}; font-size: 13px;">
                    <span style="font-weight: bold; color: #1f2937;">{job['title']}</span> — <span style="color: #059669;">{job['company']}</span><br>
                    <span style="color: #6b7280; font-size: 12px;">📍 {job.get('location', 'Unknown')[:35]} | <a href="{job['url']}" style="color: #2563eb;">Apply →</a></span>
                </div>"""
    
    if not is_new:
        html += "</div></details>"
    
    return html


def send_job_alert(new_jobs, old_jobs=None, recipient=RECIPIENT_EMAIL):
    """Send email with new jobs at top, old jobs collapsible"""
    if not new_jobs and not old_jobs:
        print("No jobs to send.")
        return False
    
    total_new = len(new_jobs) if new_jobs else 0
    total_old = len(old_jobs) if old_jobs else 0
    
    html = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.5;">
        <h1 style="color: #2563eb; font-size: 22px;">🚀 Job Alert - {datetime.now().strftime('%B %d, %Y %I:%M %p')}</h1>
        <div style="background: #dbeafe; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <strong>🆕 {total_new} New Jobs</strong> | 📂 {total_old} Previously Seen<br>
            <span style="color: #6b7280; font-size: 13px;">Entry-level (≤2 yrs) | US only</span>
        </div>
    """
    
    # New jobs section (expanded)
    if new_jobs:
        html += build_jobs_section(new_jobs, "NEW JOBS", is_new=True)
    else:
        html += "<p style='color: #6b7280;'>No new jobs since last check.</p>"
    
    # Old jobs section (collapsible)
    if old_jobs:
        html += build_jobs_section(old_jobs, "Previously Seen Jobs", is_new=False)
    
    html += """
        <hr style="margin-top: 30px; border: none; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 11px; text-align: center;">Job Search Agent 🤖 | Runs every hour</p>
    </body>
    </html>
    """
    
    # Plain text
    text = f"Found {total_new} new jobs, {total_old} previously seen.\n\n"
    if new_jobs:
        text += "=== NEW JOBS ===\n"
        for job in new_jobs:
            text += f"• {job['title']} @ {job['company']}\n  {job['url']}\n\n"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 {total_new} New Jobs | {total_old} Saved - {datetime.now().strftime('%b %d %I:%M%p')}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        print(f"✅ Email sent! {total_new} new, {total_old} old jobs")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == '__main__':
    # Test
    new = [{'title': 'Product Manager', 'company': 'Anthropic', 'location': 'SF', 'url': 'https://anthropic.com', 'tier': 1}]
    old = [{'title': 'Data Analyst', 'company': 'Stripe', 'location': 'NYC', 'url': 'https://stripe.com', 'tier': 1}]
    send_job_alert(new, old)
