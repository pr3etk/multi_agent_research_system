# Multi-Agent Research System A **4-stage research system** built using **LangChain**, **LangGraph**, **Mistral AI**, **Tavily Search**, and **BeautifulSoup** that autonomously searches the web, extracts relevant information, generates a structured research report, and performs AI-based critique for quality assurance. The system exposes a **FastAPI** backend, enabling seamless integration with modern frontend applications. --- ## ✨ Features - 🔍 AI-powered web search using Tavily Search - 🌐 Intelligent webpage scraping with BeautifulSoup - 📝 Automated research report generation - 🤖 AI-based report review and quality feedback - ⚡ FastAPI backend with REST APIs - 🎨 React (Vite + TypeScript) frontend integration - 🔒 Environment variable management using .env - 🚀 Modular multi-agent architecture --- # 🏗️ System Architecture
text
User
  |
  v
React Frontend (Vite + TypeScript)
  |
  |  POST /research with { topic }
  v
FastAPI Backend
  |
  |  validates input with Pydantic
  |  allows browser access with CORS
  |  runs long work in a thread
  v
Research Pipeline
  |
  +--> Search Agent ----> Tavily web search
  |
  +--> Reader Agent -----> requests + BeautifulSoup scrape web page
  |
  +--> Writer Chain ------> generates structured report
  |
  +--> Critic Chain ------> reviews report and gives score
  |
  v
Structured JSON Response
  |
  v
Frontend Dashboard
  |
  +--> Introduction
  +--> Key Findings
  +--> Conclusion
  +--> Sources
  +--> Feedback / Score
  +--> Raw search and scrape output
--- # ⚙️ Tech Stack ### Backend - FastAPI - Python - Pydantic ### AI & LLM - LangChain - LangGraph - Mistral AI ### Research Tools - Tavily Search API - BeautifulSoup - Requests ### Frontend - React - Vite - TypeScript ### Utilities - Python Dotenv - Rich --- # 📂 Project Structure
text
multi_agent/
│
├── app/
│   ├── api.py
│   ├── agents.py
│   ├── pipeline.py
│   ├── tools.py
│   └── __init__.py
│
├── frontend/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
--- # 🚀 Installation ## 1. Clone the repository
bash
git clone https://github.com/<your-username>/multi-agent-research-system.git

cd multi-agent-research-system
--- ## 2. Create a virtual environment
bash
python -m venv .venv
### Windows
bash
.venv\Scripts\activate
### Linux / macOS
bash
source .venv/bin/activate
--- ## 3. Install dependencies
bash
pip install -r requirements.txt
--- ## 4. Configure environment variables Create a .env file in the project root.
env
OPENAI_API_KEY=
MISTRAL_API_KEY=
TAVILY_API_KEY=
--- # ▶️ Running the Backend
bash
uvicorn app.api:app --reload
Backend:
http://127.0.0.1:8000
Swagger UI:
http://127.0.0.1:8000/docs
--- # 💻 Running the Frontend
bash
cd frontend

npm install

npm run dev
Frontend:
http://localhost:5173
--- # 📡 API ## POST /research ### Request
json
{
    "topic": "Latest developments in AI Agents"
}
--- ### Response
json
{
    "search_result": "...",
    "reader_result": "...",
    "report": "...",
    "feedback": "..."
}
--- # 🔄 Workflow 1. User enters a research topic in the frontend. 2. FastAPI receives the request. 3. Search Agent performs web search using Tavily. 4. Reader Agent scrapes the most relevant webpage. 5. Writer Chain generates a comprehensive research report. 6. Critic Chain evaluates the report and provides feedback. 7. FastAPI returns a structured JSON response. 8. React frontend displays the report in organized sections. --- # 📊 Frontend Dashboard The frontend presents the research in an easy-to-read format: - 📖 Introduction - 🔑 Key Findings - 📚 Detailed Report - 📌 Conclusion - 🌐 Sources - ⭐ Critic Feedback & Score - 📝 Raw Search Results - 📄 Raw Scraped Content --- # 🔮 Future Improvements - Server-Sent Events (SSE) for live streaming responses - WebSocket support - Parallel multi-source research - PDF export - Research history - Authentication - Vector database integration - Multi-LLM support (OpenAI, Claude, Gemini, Mistral) - Docker support - AWS deployment - CI/CD with GitHub Actions --- # 🤝 Contributing Contributions, feature requests, and pull requests are welcome. 1. Fork the repository. 2. Create a new feature branch. 3. Commit your changes. 4. Push the branch. 5. Open a Pull Request.
