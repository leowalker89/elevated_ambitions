# Elevated Ambitions

## Introduction to the LLM Resume Parser Project

In response to the increasing complexity and diversity of resumes in today's remote work-driven job market, the Elevated Ambitions project introduces the LLM Resume Parser. This innovative tool leverages advanced AI models, like GPT-4 and GPT-3.5 Turbo, to efficiently parse varied resume formats, overcoming challenges such as intricate content diversity and complex formatting. By employing novel techniques in prompt engineering and structured data processing, the LLM Resume Parser not only enhances the accuracy and adaptability of talent acquisition processes but also marks a significant stride in the application of AI in modern recruitment practices.

## Requirements

To run this project, you will need to install the following:

```cmd
pip install -r requirements.txt
```

1. Create a `.env` file in the root directory of your project.
2. Add the following lines to the `.env` file:
    ```
    OPENAI_API_KEY='place your openai api key here'
    LANGCHAIN_API_KEY='place your langchain api key here'
    WEBSCRAPING_API_KEY='place your webscraping api key here'
    ANTHROPIC_API_KEY='place your anthropic api key here'
    ```

While this project is still under development the main components as of now are the notebooks. However the notebooks do utilize the prompts folder and the resume_template.py file.

The evaluation portion also requires access to LangSmith or LangHub. There is currently a waitlist to have access to it.