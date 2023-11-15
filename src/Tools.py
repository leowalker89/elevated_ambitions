def analyze_resume(full_text, model='gpt-3.5-turbo-1106'):
    """
    Analyze a resume text and extract structured information using a specified language model.

    Parameters:
    full_text (str): The text content of the resume.
    model (str): The language model to use for processing the text.

    Returns:
    dict: A dictionary containing structured information extracted from the resume.
    """
    # Load the prompt template and response template for resume analysis
    with open("../prompts/resume_extraction.prompt", "r") as f:
        template = f.read()
    with open("../templates/scale_profile_template.json", "r") as f:
        resume_template = f.read()

    # Format the input for the language model
    prompt_template = PromptTemplate(template=template, input_variables=['resume', 'response_template'])
    formatted_input = prompt_template.format(resume=full_text, response_template=resume_template)

    # Invoke the language model and process the resume
    chat_llm = ChatOpenAI(model=model)
    analysis_output = chat_llm.invoke(formatted_input)

    return analysis_output

def upgrade_experience_bullet(user_experience, bullet, model='gpt-3.5-turbo-1106'):
    """
    Enhance a bullet point in a user's experience section using a language model.

    Parameters:
    user_experience (dict): A dictionary containing details of a user's experience.
    bullet (str): The bullet point to be enhanced.
    model (str): The language model to use for enhancement.

    Returns:
    str: The enhanced bullet point.
    """
    # Load the bullet enhancement template
    with open("../prompts/synthetic_bullet_builder.prompt", "r") as f:
        template = f.read()

    # Format the input for the language model
    prompt_template = PromptTemplate(template=template, input_variables=['user_summary', 'bullet_point'])
    formatted_input = prompt_template.format(user_summary=user_experience, bullet_point=bullet)

    # Invoke the language model and enhance the bullet point
    chat_llm = ChatOpenAI(model=model)
    analysis_output = chat_llm.invoke(formatted_input)

    return analysis_output.content

def upgrade_resume_bullets(extracted_resume):
    """
    Iterate through the work experience in a resume and upgrade each bullet point.

    Parameters:
    extracted_resume (dict): A dictionary containing a structured resume.

    Returns:
    dict: The resume dictionary with enhanced bullet points in the work experience section.
    """
    # Enhance bullet points for each work experience entry
    for experience in extracted_resume['work_experience']:
        experience_desc = ' '.join([experience[field] for field in ['company', 'title', 'duration', 'description']])
        # skip experience if there is no achievements
        if not experience['achievements']:
            continue
        else:
            for i, bullet in enumerate(experience['achievements']):
                # skip bullet if it is empty
                if bullet == '':
                    continue
                else:
                    experience['achievements'][i] = upgrade_experience_bullet(experience_desc, bullet)

    return extracted_resume

def generate_questions(user_profile, model='gpt-3.5-turbo-1106'):
    """
    Generate interview questions based on a user's profile using a language model.

    Parameters:
    user_profile (dict): A dictionary containing the user's profile information.
    model (str): The language model to use for question generation.

    Returns:
    dict: A dictionary containing generated interview questions.
    """
    # Load the question generation template and response template
    with open("../prompts/question_generation.prompt", "r") as f:
        question_template = f.read()
    with open("../templates/profile_interview_template.json", "r") as f:
        profile_template = f.read()

    # Format the input for the language model
    prompt_template = PromptTemplate(template=question_template, input_variables=['user_profile', 'response_template'])
    formatted_input = prompt_template.format(user_profile=user_profile, response_template=profile_template)

    # Invoke the language model and generate questions
    chat_llm = ChatOpenAI(model=model)
    response = chat_llm.invoke(formatted_input)

    return json.loads(response.content)

def generate_synthetic_responses(user_profile, questions, model='gpt-3.5-turbo-1106'):
    """
    Generate synthetic interview responses for a set of questions based on a user's profile.

    Parameters:
    user_profile (dict): A dictionary containing the user's profile information.
    questions (dict): A dictionary containing interview questions.
    model (str): The language model to use for generating responses.

    Returns:
    dict: A dictionary containing synthetic responses to the interview questions.
    """
    # Load the interview response generation template
    with open("../prompts/synthetic_interview_responses.prompt", "r") as f:
        resume_template = f.read()
    with open("../templates/profile_interview_template.json", "r") as f:
        interview_template = f.read()

    # Format the input for the language model
    prompt_template = PromptTemplate(template=resume_template, input_variables=['user_profile', 'questions', 'template'])
    formatted_input = prompt_template.format(user_profile=user_profile, questions=questions, template=interview_template)

    # Invoke the language model and generate responses
    chat_llm = ChatOpenAI(model=model)
    response = chat_llm.invoke(formatted_input)

    return json.loads(response.content)