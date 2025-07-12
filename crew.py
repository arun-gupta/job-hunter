from crewai import Crew, Task
from agents import JobSearchAgent, DatabaseAgent, ResumeOptimizationAgent, ReferralNetworkAgent

class JobHunterCrew:
    def __init__(self):
        self.job_search_agent = JobSearchAgent()
        self.database_agent = DatabaseAgent()
        self.resume_agent = ResumeOptimizationAgent()
        self.referral_agent = ReferralNetworkAgent()

    def get_crew(self, job_criteria, resume_path=None):
        # Parse job criteria (format: "Software Engineer, San Francisco, CA, Senior, Tech Company")
        criteria_parts = job_criteria.split(',')
        job_title = criteria_parts[0].strip() if len(criteria_parts) > 0 else "Software Engineer"
        location = criteria_parts[1].strip() if len(criteria_parts) > 1 else "San Francisco"
        experience_level = criteria_parts[3].strip().lower() if len(criteria_parts) > 3 else "mid-senior"
        
        # Define tasks for each agent
        tasks = [
            Task(
                description=f"""
                Search LinkedIn for job opportunities matching the following criteria:
                - Job Title: {job_title}
                - Location: {location}
                - Experience Level: {experience_level}
                
                Use the linkedin_job_search_tool to find relevant job postings.
                Return a detailed list of job opportunities with company names, locations, and job URLs.
                Focus on high-quality positions that match the user's criteria.
                """,
                agent=self.job_search_agent.agent,
                expected_output="A comprehensive list of job postings with details including title, company, location, URL, and posting date"
            ),
            Task(
                description="""
                Store the job postings found by the Job Search Agent in the database.
                For each job, extract and store:
                - Job title
                - Company name
                - Location
                - Job URL
                - Posted date
                - Source (LinkedIn)
                
                Ensure data is properly formatted and stored for future reference.
                """,
                agent=self.database_agent.agent,
                expected_output="Confirmation that all job postings have been successfully stored in the database"
            ),
            Task(
                description=f"""
                Analyze the job postings and optimize the resume for better alignment.
                Focus on:
                - Matching keywords from job descriptions
                - Highlighting relevant experience
                - Tailoring skills and achievements
                
                Resume path: {resume_path if resume_path else 'No resume provided'}
                
                Create optimized versions of the resume for each job category found.
                """,
                agent=self.resume_agent.agent,
                expected_output="Optimized resume versions tailored to the job opportunities found"
            ),
            Task(
                description="""
                Analyze the job postings and identify potential referral opportunities.
                For each company with job openings, look for:
                - Connections at those companies
                - Alumni from the user's network
                - People who could provide referrals
                
                Provide a list of potential referral contacts with their connection to the target companies.
                """,
                agent=self.referral_agent.agent,
                expected_output="List of potential referral contacts for the job opportunities found"
            ),
        ]
        
        return Crew(
            agents=[
                self.job_search_agent.agent,
                self.database_agent.agent,
                self.resume_agent.agent,
                self.referral_agent.agent
            ],
            tasks=tasks,
            verbose=True,
            memory=True
        ) 