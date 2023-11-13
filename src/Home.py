import sys
from pathlib import Path
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# from authlib.integrations.requests_client import OAuth2Session
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
# client_id = os.getenv("GOOGLE_CLIENT_ID")
# client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

st.set_page_config(page_title="Elevated Ambitions", page_icon=":helicopter:", layout="wide")

st.title(":helicopter: Elevated Ambitions \n\n **Turning dreams into opportunities**")

st.balloons()

# oauth = OAuth2Session(client_id, client_secret, redirect_uri='your_redirect_uri')

# Streamlit app
# def main():

#     if 'auth_token' not in st.session_state:
#         # Display login button
#         if st.button("Login with Google"):
#             authorization_url, state = oauth.create_authorization_url(
#                 "https://accounts.google.com/o/oauth2/auth",
#                 scope=["openid", "email", "profile"],
#                 response_type="code"
#             )
#             st.session_state['oauth_state'] = state
#             st.rerun()

#     # Callback handling and token exchange would go here

# if __name__ == "__main__":
#     main()


# st.success("""
# If you'd like to learn more about the technical details of FinSight, check out the LlamaIndex blogpost below where I do a deep dive into the project:
           
# [How I built the Streamlit LLM Hackathon winning app — FinSight using LlamaIndex.](https://blog.llamaindex.ai/how-i-built-the-streamlit-llm-hackathon-winning-app-finsight-using-llamaindex-9dcf6c46d7a0)
        
# """)

# with open("docs/news.md", "r") as f:
#     st.success(f.read())

with open("docs/main.md", "r") as f:
    st.info(f.read())
