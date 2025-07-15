import chainlit as cl
import os
import traceback
import json
from dotenv import load_dotenv
from crew import JobHunterCrew
from utils import save_uploaded_file
from linkedin_scraper import linkedin_job_search_tool
import asyncio
from chainlit import Action

load_dotenv()

@cl.on_chat_start
async def start():
    # Check if we've already shown the welcome message
    if not cl.user_session.get("welcome_shown"):
        jobs_per_page = cl.user_session.get("jobs_per_page", 10)
        sort_field = cl.user_session.get("sort_field", "posted_time")
        sort_dir = cl.user_session.get("sort_dir", "asc")
        welcome_message = f"""👋 Welcome to Job Hunter! I'll help you find jobs, optimize your resume, and find referrals.

🔐 **LinkedIn Authentication Setup:**
Let me set up LinkedIn authentication for better job search results...

**Jobs per page:** {jobs_per_page} (change anytime by sending 'jobs per page: N')
**Sort by:** {sort_field} ({sort_dir}) (change anytime by sending 'sort by <field> [asc|desc]')"""
        await cl.Message(content=welcome_message).send()
        
        # Check if LinkedIn cookies exist
        cookies_file = "linkedin_cookies.json"
        if os.path.exists(cookies_file):
            try:
                with open(cookies_file, 'r') as f:
                    cookies = json.load(f)
                await cl.Message(content="✅ LinkedIn cookies found! You're authenticated for better job search results.").send()
                cl.user_session.set("linkedin_authenticated", True)
            except Exception as e:
                await cl.Message(content="⚠️ LinkedIn cookies found but may be invalid. You'll use public access.").send()
                cl.user_session.set("linkedin_authenticated", False)
        else:
            await cl.Message(content="ℹ️ No LinkedIn cookies found. You'll use public access (limited results).").send()
            await cl.Message(content="💡 **For better results:** Run `python linkedin_auth_helper.py` in your terminal to set up LinkedIn authentication.").send()
            cl.user_session.set("linkedin_authenticated", False)
        
        await cl.Message(content="📝 **How to use:** Enter your job search criteria (e.g., 'Software Engineer, San Francisco, CA, Senior, Tech Company')").send()
        cl.user_session.set("welcome_shown", True)

async def render_jobs_table(jobs):
    headers = [
        "Job Title",
        "Company",
        "Location",
        "Posted"
    ]
    table_md = "| " + " | ".join(headers) + " |\n|" + "---|"*len(headers) + "\n"
    for job in jobs:
        title_link = f"[{job['title']}]({job['url']})"
        company = job['company']
        location = job['location']
        posted = job['posted_time']
        table_md += f"| {title_link} | {company} | {location} | {posted} |\n"
    await cl.Message(content=table_md).send()

@cl.on_message
async def main(message: cl.Message):
    # Allow user to set jobs per page
    if message.content.lower().startswith("jobs per page:"):
        try:
            n = int(message.content.split(":", 1)[1].strip())
            cl.user_session.set("jobs_per_page", n)
            await cl.Message(content=f"✅ Jobs per page set to {n}.").send()
        except Exception:
            await cl.Message(content="❌ Invalid number for jobs per page. Please use e.g. 'jobs per page: 20'").send()
        return
    # Allow user to set sort order
    if message.content.lower().startswith("sort by"):
        parts = message.content.lower().split()
        if len(parts) >= 3:
            field = parts[2]
            valid_fields = {"title": "title", "company": "company", "location": "location", "posted": "posted_time", "posted_time": "posted_time"}
            if field not in valid_fields:
                await cl.Message(content="❌ Invalid sort field. Use one of: title, company, location, posted").send()
                return
            sort_field = valid_fields[field]
            sort_dir = "asc"
            if len(parts) >= 4 and parts[3] in ["asc", "desc"]:
                sort_dir = parts[3]
            cl.user_session.set("sort_field", sort_field)
            cl.user_session.set("sort_dir", sort_dir)
            await cl.Message(content=f"✅ Sort order set to {field} ({sort_dir}).").send()
        else:
            await cl.Message(content="❌ Usage: sort by <field> [asc|desc]").send()
        return
    # Get the job search criteria from user input
    job_criteria = message.content
    
    # Check if user wants to set up LinkedIn authentication
    if "linkedin" in job_criteria.lower() and ("auth" in job_criteria.lower() or "login" in job_criteria.lower()):
        await cl.Message(content="🔐 **LinkedIn Authentication Setup:**\n\nTo set up LinkedIn authentication for better job search results:\n\n1. Open a new terminal\n2. Run: `python linkedin_auth_helper.py`\n3. Follow the prompts to log in to LinkedIn\n4. Come back here and try your job search again\n\nThis will give you access to more job listings!").send()
        return
    
    await cl.Message(content=f"🔍 Searching for jobs matching: {job_criteria}").send()
    progress_msg = await cl.Message(content="⏳ Searching for jobs... [0%]", author="system").send()
    
    # Show authentication status
    linkedin_authenticated = cl.user_session.get("linkedin_authenticated", False)
    li_at_cookie = None
    if linkedin_authenticated:
        await cl.Message(content="✅ Using authenticated LinkedIn access (better results)").send()
        # Load li_at cookie from cookies file
        cookies_file = "linkedin_cookies.json"
        if os.path.exists(cookies_file):
            try:
                import json
                with open(cookies_file, 'r') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    if cookie.get('name') == 'li_at':
                        li_at_cookie = cookie.get('value')
                        break
            except Exception as e:
                await cl.Message(content="⚠️ LinkedIn cookies found but may be invalid. You'll use public access.").send()
                li_at_cookie = None
    else:
        await cl.Message(content="ℹ️ Using public LinkedIn access (limited results)").send()
    
    try:
        # Parse job criteria for direct tool call
        criteria_parts = job_criteria.split(',')
        job_title = criteria_parts[0].strip() if len(criteria_parts) > 0 else "Software Engineer"
        location = criteria_parts[1].strip() if len(criteria_parts) > 1 else "San Francisco"
        experience_level = criteria_parts[3].strip().lower() if len(criteria_parts) > 3 else "mid-senior"
        
        # Validate experience_level
        valid_experience_levels = ["internship", "entry", "associate", "mid-senior", "senior", "executive"]
        exp_level_valid = experience_level in valid_experience_levels
        if experience_level and not exp_level_valid:
            await cl.Message(content=f"⚠️ Experience level '{experience_level}' is not recognized. Proceeding without experience filter.").send()
            experience_level = None
        
        # Debug: Show parsed values
        await cl.Message(content=f"[DEBUG] Parsed job_title: '{job_title}', location: '{location}', experience_level: '{experience_level}'").send()
        
        # Use the new job search tool
        jobs_per_page = cl.user_session.get("jobs_per_page", 10)
        sort_field = cl.user_session.get("sort_field", "posted_time")
        sort_dir = cl.user_session.get("sort_dir", "asc")
        
        # Parse user input for experience level
        experience_levels = []
        if 'experience' in job_criteria:
            # Extract experience level(s) from user_query
            # (Assume you have logic to parse and map user input to LinkedIn experience filters)
            experience_levels = parse_experience_levels(job_criteria)
        
        # When building the LinkedIn job search query:
        query_options = {
            'limit': jobs_per_page,
            'locations': [location],
        }
        if experience_levels:
            query_options['filters'] = {'experience': experience_levels}
        
        jobs = linkedin_job_search_tool(
            job_title=job_title,
            location=location,
            experience_level=experience_level,
            max_jobs=jobs_per_page,
            li_at_cookie=li_at_cookie
        )
        # Sort jobs before displaying
        reverse = sort_dir == "desc"
        jobs = sorted(jobs, key=lambda j: (j.get(sort_field) or "").lower() if isinstance(j.get(sort_field), str) else (j.get(sort_field) or ""), reverse=reverse)
        cl.user_session.set("last_jobs", jobs)
        if not jobs:
            await cl.Message(content="❌ No jobs found for your criteria. Please try different search terms.").send()
            return
        await cl.Message(content=f"✅ Found {len(jobs)} jobs. Displaying results as a table (sorted by {sort_field} {sort_dir}):").send()
        await render_jobs_table(jobs)
        # Proceed with other agents as needed (not shown here)
    except Exception as e:
        # Progress message cannot be removed; just send a new message
        import traceback
        tb = traceback.format_exc()
        await cl.Message(content=f"❌ Error: {str(e)}\n\n[Traceback]\n{tb}").send() 

# Use the correct decorator for Chainlit 2.x
# Remove all sort_field, sort_dir, and sorting logic from the rest of the code
# Remove the @cl.action_callback handle_action function
# Remove any references to sorting in user messages and session state 