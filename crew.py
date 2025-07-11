from crewai import Crew, Task
from agents import JobSearchAgent, DatabaseAgent, ResumeOptimizationAgent, ReferralNetworkAgent

class JobHunterCrew:
    def __init__(self):
        self.job_search_agent = JobSearchAgent()
        self.database_agent = DatabaseAgent()
        self.resume_agent = ResumeOptimizationAgent()
        self.referral_agent = ReferralNetworkAgent()

    def get_crew(self, job_criteria, resume_path):
        # Define tasks for each agent
        tasks = [
            Task(
                description=f"Search LinkedIn for jobs matching: {job_criteria}",
                agent=self.job_search_agent.agent,
                expected_output="List of job postings"
            ),
            Task(
                description="Store matched jobs in the database.",
                agent=self.database_agent.agent,
                expected_output="Jobs stored in DB"
            ),
            Task(
                description=f"Rewrite resume at {resume_path} to align with jobs and store.",
                agent=self.resume_agent.agent,
                expected_output="Optimized resumes stored"
            ),
            Task(
                description="Scan LinkedIn connections for referral opportunities.",
                agent=self.referral_agent.agent,
                expected_output="Referral candidates found"
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