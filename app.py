import os
import streamlit as st
import pandas as pd
from openai import OpenAI
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from io import BytesIO
import math
import json
import re
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
st.set_page_config(page_title="📊PM Project Lens", layout="wide")
st.title("📊 PM Project Lens - Risk Analysis & Mitigation Plan")

prompt_input = st.text_area(
    "Enter your risk analysis prompt", 
    "Identify tasks that are most likely to cause delays due to vague requirements or high priority."
)

# 🔹 Slider to control number of records
max_records = st.slider(
    "Select number of records to display:",
    min_value=1,
    max_value=len(tasks_df),
    value=min(5, len(tasks_df)),  # default 5 or less if fewer tasks
    step=1
)

def create_wsr_pptx_from_df(results_df, template_path="WSR_Framework.pptx",
                            title_text="Risks and Mitigation Plan",
                            max_rows_per_slide=12):
    """
    Create a PPTX (bytes) using a template if available and inserting the
    results_df as a table titled `title_text`. Splits into multiple slides
    if rows exceed max_rows_per_slide.

    results_df must contain columns: task_name, owner, risk_score, mitigation_plan
    """
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    from io import BytesIO
    import math

    # Validate columns
    expected_cols = ["task_name", "owner", "risk_score", "mitigation_plan"]
    for c in expected_cols:
        if c not in results_df.columns:
            raise ValueError(f"Missing column in results_df: {c}")

    # Try to load template; if not found, create a blank Presentation
    try:
        prs = Presentation(template_path)
    except Exception:
        prs = Presentation()  # blank

    # Function to add a single slide with a table for a chunk of rows
    def _add_table_slide(prs, df_chunk, title_text):
        # Choose a blank layout if available, otherwise first layout
        layout = None
        for l in prs.slide_layouts:
            if len(l.placeholders) == 0:  # blank layout
                layout = l
                break
        if layout is None:
            layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]

        slide = prs.slides.add_slide(layout)

        # Add title
        left = Inches(0.5)
        top = Inches(0.2)
        width = Inches(9)
        height = Inches(0.6)
        title_box = slide.shapes.add_textbox(left, top, width, height)
        title_tf = title_box.text_frame
        title_tf.text = title_text
        title_tf.paragraphs[0].font.size = Pt(24)
        title_tf.paragraphs[0].font.bold = True
        title_tf.paragraphs[0].alignment = PP_ALIGN.LEFT

        # --- Fix: compute widths in inches ---
        try:
            slide_width_emus = prs.slide_width
            slide_width_inches = slide_width_emus / 914400.0  # 1 inch = 914400 EMU
        except Exception:
            slide_width_inches = 10.0  # default

        table_width_inches = slide_width_inches - 0.8
        col_widths = [
            Inches(table_width_inches * 0.25),
            Inches(table_width_inches * 0.15),
            Inches(table_width_inches * 0.12),
            Inches(table_width_inches * 0.48),
        ]

        # Table size
        rows = len(df_chunk) + 1
        cols = 4
        left = Inches(0.4)
        top = Inches(1.0)
        table_width = Inches(table_width_inches)
        height = Inches(0.5 + 0.3 * rows)

        table = slide.shapes.add_table(rows, cols, left, top, table_width, height).table

        # Set column widths
        for i, w in enumerate(col_widths):
            table.columns[i].width = w

        # Header row
        headers = ["Task", "Owner", "Risk Score", "Mitigation Plan"]
        for col_idx, header in enumerate(headers):
            cell = table.cell(0, col_idx)
            cell.text = header
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(12)

        # Fill table
        for r, (_, row) in enumerate(df_chunk.iterrows(), start=1):
            table.cell(r, 0).text = str(row.get("task_name", ""))
            table.cell(r, 1).text = str(row.get("owner", ""))
            table.cell(r, 2).text = str(row.get("risk_score", ""))
            table.cell(r, 3).text = str(row.get("mitigation_plan", ""))

            for cidx in range(cols):
                p = table.cell(r, cidx).text_frame.paragraphs[0]
                p.font.size = Pt(10)

    # Split the DataFrame into chunks
    total_rows = len(results_df)
    n_slides = math.ceil(total_rows / max_rows_per_slide) if total_rows > 0 else 0
    for i in range(n_slides):
        start = i * max_rows_per_slide
        end = start + max_rows_per_slide
        chunk = results_df.iloc[start:end]
        _add_table_slide(prs, chunk, title_text)

    if total_rows == 0:
        _add_table_slide(prs, results_df.head(0), title_text)

    # Save to bytes
    bio = BytesIO()
    prs.save(bio)
    bio.seek(0)
    return bio.getvalue()

if st.button("Analyze Risks"):
    with st.spinner("Analyzing tasks..."):
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
            Filter only Top {max_records} records
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
                #st.subheader("Risk Analysis Output (JSON)")
                #st.code(output_text, language="json")
                
                # Try parsing JSON output into DataFrame
                try:
                    output_json = json.loads(output_text)
                    output_df = pd.DataFrame(output_json)
                    
                     # 🔹 Apply record count filter
                    filtered_results = output_df.head(max_records)
                    st.subheader("Risk Analysis Table")
                    #st.dataframe(output_df)
                    filtered_results.insert(0, "S.No", range(1, 1 + len(filtered_results)))
                    st.dataframe(filtered_results, hide_index=True, use_container_width=True)
                    final_df = filtered_results.copy()
                    # Optionally allow CSV download
                    csv = output_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download CSV", csv, "risk_analysis.csv", "text/csv", key='download-csv'
                    )
                    for col in ["task_name", "owner", "risk_score", "mitigation_plan"]:
                        if col not in final_df.columns:
                            final_df[col] = ""

                    # Create PPTX bytes
                    pptx_bytes = None
                    try:
                        pptx_bytes = create_wsr_pptx_from_df(final_df, template_path="WSR_Framework.pptx",
                                                             title_text="Risks and Mitigation Plan",
                                                             max_rows_per_slide=12)
                    except Exception as e:
                        st.error(f"Failed to generate PPTX from template: {e}")
                        # Try without template
                        pptx_bytes = create_wsr_pptx_from_df(final_df, template_path=None,
                                                             title_text="Risks and Mitigation Plan",
                                                             max_rows_per_slide=12)
                    st.download_button(
                        "⬇ Download WSR (Risks and Mitigation Plan PPTX)",
                        data=pptx_bytes,
                        file_name="WSR_Risks_and_Mitigation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
                except Exception as e:
                    st.error(f"Failed to parse JSON output: {e}")

            except Exception as e:
                st.error(f"Error calling OpenAI API: {e}")
