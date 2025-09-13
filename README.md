
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
   - (setx OPENAI_API_KEY "OPENAI_API_KEY")

Notes:
 - The sample data is synthetic for demonstration and hackathon use.
 - The app expects that Azure/OpenAI will return a JSON-parsable output if used; otherwise it will fallback to local parsing and scoring.
 - Feel free to edit app.py to change heuristics, add more fields, or integrate other LLM providers.


Example Prompts:

Create WSR for Sprint 4 and Identify all tasks where the owner is handling more than 3 high-priority items and explain the increased risk

Create WSR for Sprint 5 and Identify all tasks where the owner is handling more than 3 high-priority items and explain the increased risk

Create WSR for Sprint 3 and Show tasks most at risk of scope creep if customers request additional requirements mid-project

Create WSR for Sprint 2 and Detect tasks where unclear specifications or prototypes could cause quality or timeline issues.
