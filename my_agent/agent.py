from google.adk.agents import Agent

from .tools import (
    calculate_average,
    create_file,
    push_project_to_github,
    push_to_github,
)


root_agent = Agent(
    name="student_assistant",
    model="gemini-3.6-flash",
    description="A student assistant that can answer questions using study documents and manage code files.",
    instruction="""
    You are a helpful student assistant.

    Help students with questions about their studies.

    When the user asks you to calculate an average,
    use the calculate_average tool.

    When the user asks you to create a file,
    use the create_file tool.

    When the user asks you to push a single file or code snippet to GitHub,
    use the push_to_github tool.

    When the user asks you to push the entire project to GitHub,
    use the push_project_to_github tool.

    Answer clearly and concisely.
    """,
    tools=[
        calculate_average,
        create_file,
        push_to_github,
        push_project_to_github,
    ],
)