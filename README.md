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
   source venv/bin/activate
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
- ✅ **LinkedIn Integration**: OAuth-based job scraping with Selenium
- ✅ **CrewAI Tools**: Proper tool configuration for all agents
- ✅ **Error Handling**: Improved error messages and user guidance
- 🔄 **Next Steps**: Implement database integration and resume optimization

## 🎯 Next Development Steps

1. **Database Integration**: Connect agents to PostgreSQL
2. **Resume Optimization**: Add OpenAI-powered resume rewriting
3. **Network Analysis**: Implement LinkedIn connection scanning
4. **Enhanced Error Handling**: Add more robust validation

## 🛡️ Environment Variables

Required in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL database URL
- `CHAINLIT_AUTH_SECRET`: Chainlit authentication secret

### LinkedIn Authentication (Optional)
Since LinkedIn uses OAuth authentication, you have two options:

**Option 1: Use cookies for better access**
1. Run the authentication helper: `python linkedin_auth_helper.py`
2. Follow the prompts to log in manually and capture cookies
3. The scraper will automatically use the saved cookies

**Option 2: Use public access (limited results)**
- The scraper will work without authentication but with limited job listings

## 📝 Usage

1. **Start the app**: `chainlit run app.py`
2. **Optional LinkedIn Setup**: For better results, run `python linkedin_auth_helper.py` in a separate terminal
3. **Enter job search criteria**: e.g., "Software Engineer, San Francisco, CA, Senior, Tech Company"
4. **Watch the AI agents work**: The app will search LinkedIn, store results, and provide recommendations

### LinkedIn Authentication (Optional)
- **With cookies**: Better access to job listings (run `python linkedin_auth_helper.py`)
- **Without cookies**: Limited results but still functional

## 🙏 Credits

This project uses [py-linkedin-jobs-scraper](https://github.com/spinlud/py-linkedin-jobs-scraper) for robust LinkedIn job scraping. Many thanks to [@spinlud](https://github.com/spinlud) and contributors for their excellent open-source work!

## 🤝 Contributing

This is a working version with LinkedIn job search functionality. The app uses OAuth-based authentication and doesn't require LinkedIn email/password credentials.

### Key Features Implemented:
- ✅ LinkedIn job scraping with Selenium
- ✅ OAuth authentication via cookies
- ✅ CrewAI agent orchestration
- ✅ Chainlit web interface
- 🔄 Database integration (in progress)
- 🔄 Resume optimization (in progress) 