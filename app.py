import os
import streamlit as st
import pandas as pd
from openai import OpenAI
import json

# -----------------------------
# Initialize OpenAI client
# -----------------------------
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# -----------------------------
# Load data
# -----------------------------
tasks_df = pd.read_csv("tasks.csv")
team_df = pd.read_csv("team.csv")

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("PM Project Lens - Risk Analysis & Mitigation Plan")

prompt_input = st.text_area(
    "Enter your risk analysis prompt", 
    "Identify tasks that are most likely to cause delays due to vague requirements or high priority."
)

if st.button("Analyze Risks"):
    if not prompt_input.strip():
        st.warning("Please enter a prompt for risk analysis.")
    else:
        # -----------------------------
        # Prepare tasks data for LLM
        # -----------------------------
        tasks_json = tasks_df.to_dict(orient="records")
        team_json = team_df.to_dict(orient="records")

        system_message = f"""
        You are a project management assistant. 
        Given a list of tasks and team info, analyze the risk for each task based on the following criteria:
        - Vague requirements
        - High priority
        - Capacity of assigned owner

        Data provided:
        Tasks: {json.dumps(tasks_json)}
        Team: {json.dumps(team_json)}

        Your output must be JSON array with fields:
        - task_name
        - owner
        - risk_score (High, Medium, Low)
        - mitigation_plan (suggested actions to reduce risk)
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt_input}
                ],
                temperature=0.3,
            )
            
            output_text = response.choices[0].message.content
            st.subheader("Risk Analysis Output (JSON)")
            st.code(output_text, language="json")
            
            # Try parsing JSON output into DataFrame
            try:
                output_json = json.loads(output_text)
                output_df = pd.DataFrame(output_json)
                st.subheader("Risk Analysis Table")
                st.dataframe(output_df)
                
                # Optionally allow CSV download
                csv = output_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download CSV", csv, "risk_analysis.csv", "text/csv", key='download-csv'
                )
            except Exception as e:
                st.error(f"Failed to parse JSON output: {e}")

        except Exception as e:
            st.error(f"Error calling OpenAI API: {e}")
