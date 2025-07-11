# Job Hunter - Chainlit + CrewAI App

A Python-based web application using Chainlit and CrewAI for automated job hunting with four intelligent agents.

## 🚀 Features

### AI Agents
1. **Job Search Agent**: Searches LinkedIn for jobs matching your criteria
2. **Database Agent**: Stores matched jobs in the database
3. **Resume Optimization Agent**: Rewrites your resume to align with specific job requirements
4. **Referral Network Agent**: Finds potential referrals in your LinkedIn network

## 🛠️ Setup

1. **Activate the virtual environment**:
   ```bash
   source job_hunter_env/bin/activate
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database settings
   ```

3. **Run the application**:
   ```bash
   chainlit run app.py
   ```

4. **Access the app**: Open http://localhost:8000 in your browser

## 📁 Project Structure

```
job-hunter/
├── app.py              # Chainlit entrypoint
├── agents.py           # CrewAI agent definitions
├── crew.py             # CrewAI crew orchestration
├── models.py           # SQLAlchemy database models
├── db.py               # Database configuration
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── resumes/            # Directory for uploaded resumes
```

## 🔧 Current Status

- ✅ **Scaffold Complete**: Basic structure with Chainlit UI
- ✅ **Dependencies Installed**: All required packages
- ✅ **Demo Working**: App runs and shows agent workflow simulation
- 🔄 **Next Steps**: Implement actual agent tools and LinkedIn integration

## 🎯 Next Development Steps

1. **Implement LinkedIn Scraping**: Add Selenium-based job search
2. **Database Integration**: Connect agents to PostgreSQL
3. **Resume Optimization**: Add OpenAI-powered resume rewriting
4. **Network Analysis**: Implement LinkedIn connection scanning
5. **Error Handling**: Add robust error handling and validation

## 🛡️ Environment Variables

Required in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `LINKEDIN_EMAIL`: LinkedIn account email
- `LINKEDIN_PASSWORD`: LinkedIn account password
- `DATABASE_URL`: PostgreSQL database URL
- `CHAINLIT_AUTH_SECRET`: Chainlit authentication secret

## 📝 Usage

1. Start the app with `chainlit run app.py`
2. Upload your resume file
3. Enter job search criteria
4. Watch the AI agents work their magic!

## 🤝 Contributing

This is a scaffold/demo version. The actual agent implementations need to be added for full functionality. 