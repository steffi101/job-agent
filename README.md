# Job Search Agent 🔍

An AI-powered job search agent that monitors your email for job alerts, extracts and classifies job listings, and prioritizes them based on your preferences.

## Features

- 📧 **Gmail Integration**: Automatically fetches job alert emails from LinkedIn, Indeed, and other sources
- 🏢 **Company Tiering**: Classifies companies into 3 tiers based on your preferences
- 🎯 **Smart Filtering**: Filters for relevant job titles and experience levels
- 🔄 **Deduplication**: Tracks seen jobs to only show new opportunities
- ⚡ **Prioritization**: Shows Tier 1 (dream companies) first

## Setup

### 1. Install Dependencies

```bash
cd job_agent
pip install -r requirements.txt
```

### 2. First-Time Authentication

Run the authentication script:

```bash
python auth.py
```

This will:
1. Open your browser
2. Ask you to sign in to Google
3. Ask you to grant read-only access to Gmail
4. Save a token locally for future use

**Note**: You may see a warning that "Google hasn't verified this app" — click "Advanced" then "Go to Job Search Agent (unsafe)" to proceed. This is normal for personal OAuth apps.

### 3. Set Up Job Alerts

Make sure you have job alerts set up:

**LinkedIn:**
1. Go to LinkedIn Jobs
2. Search with your filters (entry level, United States)
3. Click "Set Alert" 
4. Set frequency to Daily

**Indeed:**
1. Go to Indeed.com
2. Search for jobs
3. Click "Get new jobs for this search by email"

### 4. Run the Agent

```bash
python main.py
```

Or specify how many days back to look:

```bash
python main.py 3  # Look at last 3 days of emails
```

## Configuration

Edit `config.py` to customize:

- **TIER_1_COMPANIES**: Your dream companies (immediate alert)
- **TIER_2_COMPANIES**: Strong companies (hourly alert)
- **PRIMARY_TITLES**: Job titles you're most interested in
- **SECONDARY_TITLES**: Other relevant titles
- **EXPERIENCE_EXCLUDE**: Keywords to filter out (senior, staff, etc.)

## File Structure

```
job_agent/
├── credentials.json     # Google OAuth credentials (DO NOT SHARE)
├── token.pickle        # Saved auth token (created after first run)
├── seen_jobs.json      # Database of tracked jobs
├── config.py           # Your preferences and filters
├── auth.py             # Gmail authentication
├── fetch_emails.py     # Email fetching
├── parse_linkedin.py   # LinkedIn email parser
├── parse_indeed.py     # Indeed email parser
├── database.py         # Job tracking and deduplication
├── main.py             # Main orchestrator
└── requirements.txt    # Python dependencies
```

## Output Example

```
======================================================================
 New Job Opportunities
======================================================================

🔥 TIER 1 - Dream Companies (3 jobs)
--------------------------------------------------
✅ Product Manager, New Grad
   Google | Mountain View, CA
   🔗 https://www.linkedin.com/jobs/view/123456

✅ Associate Product Manager
   Stripe | San Francisco, CA
   🔗 https://www.linkedin.com/jobs/view/789012

⭐ TIER 2 - Strong Companies (5 jobs)
--------------------------------------------------
...
```

## Automation (Coming Soon)

To run automatically every hour:

```bash
# Add to crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd /path/to/job_agent && python main.py >> job_search.log 2>&1
```

## Security Notes

- `credentials.json` contains your OAuth client secret — don't share it
- `token.pickle` contains your access token — don't share it
- The agent only requests **read-only** access to Gmail
- No data is sent anywhere except to Google's API

## Troubleshooting

**"Token has been expired or revoked"**
- Delete `token.pickle` and run `python auth.py` again

**"Access blocked: This app's request is invalid"**
- Make sure your email is added as a test user in Google Cloud Console

**No jobs found**
- Check that you have job alerts set up and emails are arriving
- Try increasing the lookback period: `python main.py 7`
