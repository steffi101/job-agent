# config.py - Configuration for Job Search Agent

# ============================================================
# TIER 1: Dream Companies (Immediate Alert)
# ============================================================
TIER_1_COMPANIES = {
    # Big Tech
    "google", "alphabet", "meta", "facebook", "amazon", "apple", "microsoft",
    "netflix", "nvidia",
    
    # AI Labs
    "anthropic", "openai", "deepmind", "cohere", "mistral", "hugging face",
    "huggingface", "scale ai", "scaleai", "databricks", "xai",
    
    # Top Fintech
    "stripe", "plaid", "paypal", "square", "block", "coinbase", "robinhood",
    "chime", "affirm", "sofi", "brex", "ramp", "ripple", "klarna", "revolut",
    
    # Other Tech Giants
    "salesforce", "adobe", "oracle", "cisco", "intel", "qualcomm", "ibm", "tesla",
    
    # Ride-sharing / Gig
    "uber", "lyft", "airbnb", "doordash", "instacart",
    
    # Social / Consumer
    "tiktok", "bytedance", "snap", "snapchat", "pinterest", "spotify", "discord",
    
    # Finance / Banks
    "goldman sachs", "goldman", "jpmorgan", "jp morgan", "morgan stanley",
    "citadel", "two sigma", "jane street", "blackstone", "blackrock", "kkr",
    "evercore", "moelis", "visa", "mastercard", "capital one", "american express",
    "amex", "fidelity", "charles schwab", "citi", "citibank", "bank of america",
    "barclays", "deutsche bank", "ubs",
}

# ============================================================
# TIER 2: Strong Companies (Hourly Alert)
# ============================================================
TIER_2_COMPANIES = {
    # Growth Fintech
    "marqeta", "toast", "bill.com", "checkout.com", "pagaya", "nova credit",
    "bilt", "mercury", "varo", "current", "acorns", "betterment", "wealthfront",
    "public.com", "fundrise", "figure", "anchorage", "circle", "fireblocks",
    "alchemy", "chainalysis",
    
    # Enterprise SaaS
    "snowflake", "datadog", "mongodb", "elastic", "twilio", "okta", "crowdstrike",
    "palo alto networks", "cloudflare", "hashicorp", "confluent", "palantir",
    "servicenow", "workday", "splunk", "figma", "notion", "airtable", "asana",
    "monday.com", "canva",
    
    # AI/ML Startups
    "weights & biases", "wandb", "anyscale", "modal", "replicate", "pinecone",
    "weaviate", "inflection", "adept", "runway", "midjourney", "jasper",
    "copy.ai", "character.ai", "perplexity", "you.com", "glean", "harvey", "writer",
    
    # Consulting
    "mckinsey", "bain", "bcg", "boston consulting", "deloitte", "ey", "ernst young",
    "pwc", "kpmg", "accenture", "capgemini", "oliver wyman", "kearney",
    
    # Other Tech
    "shopify", "atlassian", "zoom", "slack", "docusign", "dropbox", "box",
    "zendesk", "hubspot", "intuit", "autodesk", "unity", "epic games", "roblox",
    "ea", "electronic arts", "activision",
}

# ============================================================
# JOB TITLE FILTERS
# ============================================================
# Primary targets - high relevance
PRIMARY_TITLES = [
    "product manager",
    "associate product manager",
    "apm",
    "technical program manager",
    "tpm",
    "program manager",
    "ai safety",
    "ai policy",
    "trust and safety",
    "trust & safety",
    "data scientist",
    "ml engineer",
    "machine learning engineer",
    "applied scientist",
]

# Secondary targets - good opportunities
SECONDARY_TITLES = [
    "business analyst",
    "strategy and operations",
    "strategy & operations",
    "solutions engineer",
    "technical account manager",
    "data analyst",
    "quantitative analyst",
    "quant",
    "research scientist",
    "ai research",
    "software engineer",  # Cast wide net
    "data engineer",
]

# Experience level keywords to include
EXPERIENCE_INCLUDE = [
    "new grad",
    "entry level",
    "entry-level",
    "early career",
    "associate",
    "junior",
    "level 1",
    "level 2",
    "l1",
    "l2",
    "0-2 years",
    "1-2 years",
    "0-3 years",
    "recent graduate",
    "university grad",
    "college grad",
]

# Experience level keywords to exclude
EXPERIENCE_EXCLUDE = [
    "senior",
    "staff",
    "principal",
    "lead",
    "director",
    "vp",
    "vice president",
    "head of",
    "5+ years",
    "7+ years",
    "10+ years",
    "manager of managers",
]

# ============================================================
# LOCATION FILTERS
# ============================================================
LOCATIONS_INCLUDE = [
    "united states",
    "usa",
    "us",
    "remote",
    "hybrid",
    # Major cities (for reference, but we're accepting all US)
    "san francisco",
    "new york",
    "seattle",
    "austin",
    "boston",
    "los angeles",
    "chicago",
    "denver",
    "washington",
    "atlanta",
    "miami",
]

# ============================================================
# EMAIL PARSING CONFIG
# ============================================================
JOB_ALERT_SENDERS = [
    "jobs-noreply@linkedin.com",
    "jobalerts-noreply@linkedin.com", 
    "jobs@linkedin.com",
    "alert@indeed.com",
    "noreply@indeed.com",
    "jobhuntalerts@glassdoor.com",
    "careers-noreply@google.com",
]

# How far back to look for emails (in days)
EMAIL_LOOKBACK_DAYS = 1

# ============================================================
# NOTIFICATION CONFIG
# ============================================================
NOTIFICATION_EMAIL = "steffi.mathew@duke.edu"

# ============================================================
# DYNAMIC CLASSIFICATION RULES
# ============================================================
# For companies not in Tier 1 or Tier 2, classify based on:
# - Employee count > 1000 → Tier 1
# - Employee count > 200 → Tier 2
# - Series D+ funding → Tier 1
# - Series B/C funding → Tier 2
# - 50+ H1B filings → Tier 1
# - 10+ H1B filings → Tier 2

def classify_company(company_name):
    """Classify a company into tiers"""
    company_lower = company_name.lower().strip()
    
    # Check explicit tier lists
    for tier1_co in TIER_1_COMPANIES:
        if tier1_co in company_lower or company_lower in tier1_co:
            return 1
    
    for tier2_co in TIER_2_COMPANIES:
        if tier2_co in company_lower or company_lower in tier2_co:
            return 2
    
    # Default to Tier 3 for unknown companies
    # In production, this would query external APIs
    return 3


def is_relevant_title(title):
    """Check if a job title matches our filters"""
    title_lower = title.lower()
    
    # Check for exclusions first
    for exclude in EXPERIENCE_EXCLUDE:
        if exclude in title_lower:
            return False
    
    # Check primary titles
    for primary in PRIMARY_TITLES:
        if primary in title_lower:
            return True
    
    # Check secondary titles
    for secondary in SECONDARY_TITLES:
        if secondary in title_lower:
            return True
    
    return False


def is_relevant_experience_level(description):
    """Check if job description indicates entry-level"""
    desc_lower = description.lower()
    
    # Check for exclusions
    for exclude in EXPERIENCE_EXCLUDE:
        if exclude in desc_lower:
            # But check if it's negated or in a different context
            # Simple heuristic: if "senior" appears but so does "new grad", keep it
            has_include = any(inc in desc_lower for inc in EXPERIENCE_INCLUDE)
            if not has_include:
                return False
    
    # Check for inclusions
    for include in EXPERIENCE_INCLUDE:
        if include in desc_lower:
            return True
    
    # Default to True if no strong signals either way
    # (we don't want to miss opportunities)
    return True
