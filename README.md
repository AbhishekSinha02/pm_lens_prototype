
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

Steps to Get Latest Code from Git and Run Locally 

# workspace
mkdir $env:USERPROFILE\projects; cd $env:USERPROFILE\projects

# Run below command to update pip
python -m pip install --upgrade pip
pip install -r requirements.txt --user  # or pip install streamlit openai pandas python-pptx

# clone repo (requires Git)
git clone https://github.com/AbhishekSinha02/pm_lens_prototype.git
cd pm_lens_prototype

# install python from python.org (manual) -> after installing, reopen terminal

# create venv & activate
python -m venv venv
.\venv\Scripts\activate

# install deps (inside venv)
pip install --upgrade pip
pip install -r requirements.txt

# set API key for current session
$env:OPENAI_API_KEY = "sk-REPLACE_WITH_YOUR_KEY"

# run app
streamlit run app.py


Notes:
 - The sample data is synthetic for demonstration and hackathon use.
 - The app expects that OpenAI will return a JSON-parsable output if used; otherwise it will fallback to local parsing and scoring.
 - Feel free to edit app.py to change heuristics, add more fields, or integrate other LLM providers.


Example Prompts:

Create WSR for Sprint 4 and Identify all tasks where the owner is handling more than 3 high-priority items and explain the increased risk

Create WSR for Sprint 5 and Identify all tasks where the owner is handling more than 3 high-priority items and explain the increased risk

Create WSR for Sprint 3 and Show tasks most at risk of scope creep if customers request additional requirements mid-project

Create WSR for Sprint 2 and Detect tasks where unclear specifications or prototypes could cause quality or timeline issues.
