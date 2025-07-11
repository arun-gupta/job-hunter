from crewai import Agent

# Agent 1: Job Search
class JobSearchAgent:
    def __init__(self):
        self.agent = Agent(
            role="Job Search Specialist",
            goal="Find relevant job postings on LinkedIn based on user criteria",
            backstory="You are an expert in LinkedIn job search.",
            verbose=True,
            allow_delegation=False,
            tools=[] # Add LinkedIn search tool here
        )

# Agent 2: Database
class DatabaseAgent:
    def __init__(self):
        self.agent = Agent(
            role="Database Manager",
            goal="Store matched jobs in the database",
            backstory="You are a database expert.",
            verbose=True,
            allow_delegation=False,
            tools=[] # Add DB tool here
        )

# Agent 3: Resume Optimization
class ResumeOptimizationAgent:
    def __init__(self):
        self.agent = Agent(
            role="Resume Optimizer",
            goal="Rewrite resumes to align with job listings and store them.",
            backstory="You are an AI resume writer.",
            verbose=True,
            allow_delegation=False,
            tools=[] # Add resume tool here
        )

# Agent 4: Referral Network
class ReferralNetworkAgent:
    def __init__(self):
        self.agent = Agent(
            role="Referral Finder",
            goal="Scan LinkedIn connections for referral opportunities.",
            backstory="You are a networking expert.",
            verbose=True,
            allow_delegation=False,
            tools=[] # Add LinkedIn network tool here
        ) 