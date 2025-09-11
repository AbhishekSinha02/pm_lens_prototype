
PM Project Lens - Hackathon Package
==================================

Contents:
 - tasks.csv (100 synthetic project tasks)
 - team.csv (30 synthetic team members)
 - app.py (Streamlit single-file app to parse prompts and score tasks)
 - README.md (this file)

How to run:a
1. Install dependencies:
   pip install streamlit pandas openai
2. Run the app:
   streamlit run app.py
3. To enable Azure OpenAI or OpenAI modes, set environment variables or enter keys in the sidebar:
   - Azure: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT
   - OpenAI: OPENAI_API_KEY
4. If no keys are provided the app will use a small local fallback parser that extracts priorities, skills, and deadline numbers from your prompt.

Notes:
 - The sample data is synthetic for demonstration and hackathon use.
 - The app expects that Azure/OpenAI will return a JSON-parsable output if used; otherwise it will fallback to local parsing and scoring.
 - Feel free to edit app.py to change heuristics, add more fields, or integrate other LLM providers.

