import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

import streamlit as st

st.set_page_config(page_title="Elevated Ambitions", page_icon=":helicopter:", layout="wide")

st.title(":helicopter: Elevated Ambitions \n\n **Turning dreams into opportunities**")

st.balloons()

# st.success("""
# If you'd like to learn more about the technical details of FinSight, check out the LlamaIndex blogpost below where I do a deep dive into the project:
           
# [How I built the Streamlit LLM Hackathon winning app — FinSight using LlamaIndex.](https://blog.llamaindex.ai/how-i-built-the-streamlit-llm-hackathon-winning-app-finsight-using-llamaindex-9dcf6c46d7a0)
        
# """)

# with open("docs/news.md", "r") as f:
#     st.success(f.read())

with open("docs/main.md", "r") as f:
    st.info(f.read())
