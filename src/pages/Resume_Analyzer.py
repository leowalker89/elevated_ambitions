import streamlit as st
import openai
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv 
import os
import streamlit as st
import openai
from PyPDF2 import PdfFileReader
from pypdf import PdfReader
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json

# Your API Keys must be in a .env file in the root of this project

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = str(os.getenv("LANGCHAIN_API_KEY"))
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "elevated_ambitions"


st.title("Resume Analyzer")

def analyze_resume(resume_pdf, fields_list=None):
    # read in the resume file, this can be done with PyPDFLoader or UnstructuredPDFLoader
    reader = PdfReader(resume_pdf)
    full_text = str()
    for page in reader.pages:
        # take the page_content and add it to the full_text
        full_text += page.extract_text()

    # Load the prompt template
    with open("prompts/resume_extraction.prompt", "r") as f:
        template = f.read()

    # Load in the extraction results template
    with open("templates/resume_template.json", "r") as f:
        resume_template = f.read()
    
    # Define the prompt
    prompt_template = PromptTemplate(
        template=template,
        input_variables = ['resume', 'fields_list', 'response_template']
        )
    formatted_input = prompt_template.format(resume = full_text, fields_list = fields_list, response_template = resume_template)

    # Define the LLM Chain
    chat_llm = ChatOpenAI()
    analysis_output = chat_llm.invoke(formatted_input)
    return analysis_output.content

# Function to create editable fields for each subfield in a category
def create_editable_fields(category, value, is_list):
    edited_data = [] if is_list else {}
    if is_list:
        for i, item in enumerate(value):
            st.markdown(f"**{category.title()} #{i+1}**")
            # Check if the item is a dictionary before trying to iterate over it
            if isinstance(item, dict):
                edited_item = {}
                for sub_key, sub_value in item.items():
                    # Handle lists of strings differently to display them as bullet points
                    if isinstance(sub_value, list):
                        # Join the list into a bulleted string
                        bullet_list = '\n'.join(f"- {s}" for s in sub_value)
                        # Use a text area for lists of strings
                        new_val = st.text_area(f"{sub_key.replace('_', ' ').title()} #{i+1}", bullet_list, height=200)
                        # Split the edited text back into a list
                        edited_item[sub_key] = new_val.lstrip('- ').split('\n- ')
                    else:
                        # Use a larger text area for long descriptions
                        new_val = st.text_area(f"{sub_key.replace('_', ' ').title()} #{i+1}", str(sub_value), height=100)
                        edited_item[sub_key] = new_val
                edited_data.append(edited_item)
            else:
                # If item is not a dictionary, handle it as a single string
                new_val = st.text_area(f"Edit {category.title()} #{i+1}", item, height=100)
                edited_data.append(new_val)
    else:
        st.markdown(f"**{category.title()}**")
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, dict):
                # Recursive call for nested dictionaries
                edited_data[sub_key] = create_editable_fields(sub_key, sub_value, False)
            elif isinstance(sub_value, list):
                # Join the list into a bulleted string
                bullet_list = '\n'.join(f"- {s}" for s in sub_value)
                # Use a text area for lists of strings
                new_val = st.text_area(f"{sub_key.replace('_', ' ').title()}", bullet_list, height=200)
                # Split the edited text back into a list
                edited_data[sub_key] = new_val.lstrip('- ').split('\n- ')
            else:
                # Use a larger text area for long descriptions
                new_val = st.text_area(f"{sub_key.replace('_', ' ').title()}", str(sub_value), height=100)
                edited_data[sub_key] = new_val
    return edited_data


# Add a file uploader on the left side of the app
uploaded_file = st.sidebar.file_uploader("Upload your Resume in pdf format", type="pdf")

# Add toggles for user to select what the resume includes
categories = [
        "Personal Details",
        "Education",
        "Work Experience",
        "Projects",
        "Skills",
        "Certifications",
        "Publications",
        "Awards"
    ]
selected_categories = st.sidebar.multiselect("Select categories", categories)
# Add a submit button to trigger the analyze_resume function
if st.sidebar.button("Analyze Resume"):
    if uploaded_file is not None:
        # Use the selected categories in the analyze_resume function
        with st.spinner('Analyzing your resume...'):
            resume_breakdown = analyze_resume(uploaded_file, selected_categories)

        if resume_breakdown:
            try:
                resume_data = json.loads(resume_breakdown)

                # Initialize a dictionary to hold the edited data
                edited_resume_data = {}

                # Function to create editable fields for each subfield in a category
                def create_editable_fields(category, value, is_list):
                    edited_data = [] if is_list else {}
                    if is_list:
                        for i, item in enumerate(value):
                            st.markdown(f"**{category.title()} #{i+1}**")
                            edited_item = {}
                            for sub_key, sub_value in item.items():
                                new_val = st.text_input(f"{sub_key.replace('_', ' ').title()} #{i+1}", str(sub_value))
                                edited_item[sub_key] = new_val
                            edited_data.append(edited_item)
                    else:
                        st.markdown(f"**{category.title()}**")
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, dict):
                                # Recursive call for nested dictionaries
                                edited_data[sub_key] = create_editable_fields(sub_key, sub_value, False)
                            else:
                                new_val = st.text_input(f"{sub_key.replace('_', ' ').title()}", str(sub_value))
                                edited_data[sub_key] = new_val
                    return edited_data

                # Iterate through each category in the resume data
                for category, value in resume_data.items():
                    st.subheader(category.replace('_', ' ').title())
                    # Check the type of the value and create editable fields accordingly
                    if isinstance(value, list):
                        edited_resume_data[category] = create_editable_fields(category, value, True)
                    else:
                        edited_resume_data[category] = create_editable_fields(category, value, False)

                # Display the edited data as JSON
                edited_json_str = json.dumps(edited_resume_data, indent=2)
                st.json(edited_json_str)

            except json.JSONDecodeError:
                st.error("There was an error decoding the resume breakdown. Please check the format of the analyzed data.")
    else:
        st.error('No resume uploaded. Please upload a resume to analyze.')
else:
    st.info('Upload a resume and select categories to begin analysis.')

####### Below this is old code: #######


# # Set a default model
# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = list()

# # Display chat messages from history on app rerun
# if st.session_state.messages:
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

# # Accept user input
# if prompt := st.chat_input("What is up?"):
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""

#     for response in openai.ChatCompletion.create(model=st.session_state["openai_model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True,):
#         full_response += response.choices[0].delta.get("content", "")
#         message_placeholder.markdown(full_response + "▌")
#     message_placeholder.markdown(full_response)
#     st.session_state.messages.append({"role": "assistant", "content": full_response})
