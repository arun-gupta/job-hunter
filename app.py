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
    # Get the job search criteria from user input
    job_criteria = message.content
    
    await cl.Message(content=f"🔍 Searching for jobs matching: {job_criteria}").send()
    
    try:
        # Create the job hunter crew
        crew = JobHunterCrew().get_crew(job_criteria)
        
        # Run the crew to execute the job search workflow
        await cl.Message(content="🤖 Starting the AI agents to find your perfect job opportunities...").send()
        
        result = crew.kickoff()
        
        # Display the results
        await cl.Message(content="✅ **Job Search Complete!** Here's what the AI agents found:").send()
        
        # Format and display the results
        if result:
            await cl.Message(content=f"📋 **Results Summary:**\n\n{result}").send()
        else:
            await cl.Message(content="❌ No results found. Please try different search criteria.").send()
            
    except Exception as e:
        await cl.Message(content=f"❌ Error during job search: {str(e)}").send()
        await cl.Message(content="💡 Try using a different job title or location.").send() 