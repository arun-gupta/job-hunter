import chainlit as cl
import os
from dotenv import load_dotenv
from crew import JobHunterCrew
from utils import save_uploaded_file

load_dotenv()

@cl.on_chat_start
async def start():
    # Check if we've already shown the welcome message
    if not cl.user_session.get("welcome_shown"):
        await cl.Message(content="👋 Welcome to Job Hunter! I'll help you find jobs, optimize your resume, and find referrals.\n\nPlease enter your job search criteria (e.g., 'Software Engineer, San Francisco, CA, Senior, Tech Company'):").send()
        cl.user_session.set("welcome_shown", True)

@cl.on_message
async def main(message: cl.Message):
    # For now, let's create a simple demo without file upload
    await cl.Message(content="🤖 This is a demo of the Job Hunter app!").send()
    
    # Simulate the workflow
    await cl.Message(content="1️⃣ **Job Search Agent**: Searching LinkedIn for 'Software Engineer' positions in 'San Francisco'...").send()
    await cl.Message(content="2️⃣ **Database Agent**: Storing 5 matching job postings...").send()
    await cl.Message(content="3️⃣ **Resume Agent**: Optimizing your resume for each job...").send()
    await cl.Message(content="4️⃣ **Referral Agent**: Finding 3 potential referrals in your network...").send()
    
    await cl.Message(content="✅ **Demo Complete!** In the full version, you would see:\n- Actual job listings from LinkedIn\n- Optimized resumes tailored to each job\n- Database storage of all results\n- Referral recommendations from your network").send() 