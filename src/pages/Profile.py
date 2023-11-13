import streamlit as st
from pymongo import MongoClient

# MongoDB connection setup (modify with your details)
client = MongoClient("your_mongodb_connection_string")
db = client.your_database_name
users_collection = db.users

def main_page():
    st.title("Resume Builder App")
    st.write("Welcome to the Resume Builder. Please select an option to begin.")
    if st.button("Start from your resume"):
        start_from_resume()
    if st.button("Start from scratch"):
        start_from_scratch()

def start_from_resume():
    uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    if uploaded_file is not None:
        # Process the file and extract information
        pass  # Add your file processing logic here

def start_from_scratch():
    choice = st.selectbox("How would you like to proceed?", ["Fill in data myself", "Get interviewed by an expert"])
    
    if choice == "Fill in data myself":
        personal_details = st.text_input("Personal Details")
        education = st.text_input("Education")
        # Add more fields for each category
        if st.button("Submit"):
            save_to_mongodb({"Personal Details": personal_details, "Education": education})
            st.success("Data saved successfully!")

    elif choice == "Get interviewed by an expert":
        # Implement chat prompt screen logic
        pass

def save_to_mongodb(user_data):
    users_collection.insert_one(user_data)

if __name__ == "__main__":
    main_page()
