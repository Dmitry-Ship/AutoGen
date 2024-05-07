
import json
from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from tools.elements_creator_tools import upsert_mindmap, get_all_text_from_flip, parse_mindmap_markdown
from dotenv import load_dotenv
import os
import inquirer

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    system_message="A human admin.",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE")
)

mindmap_creator = AssistantAgent(
    name="mindmap_creator", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        # "stream": True,
        "cache_seed": None
    }, 
    system_message="""
    Given a content, create a mindmap with at least 3 levels. 10 items maximum. Respond in markdown format. 
    Example:
    # Modern Psychology

    ## Branches of Psychology
    - **Clinical Psychology**
        - Psychotherapy
        - Psychological Testing
        - Mental Health Disorders
    - **Cognitive Psychology**
        - Perception
        - Memory
        - Decision Making

    ## Key Concepts
    - **Behaviorism**
        - Classical Conditioning
        - Operant Conditioning
    - **Psychoanalysis**
        - Id, Ego, and Superego
        - Defense Mechanisms
            # Artificial Intelligence
            - **Machine Learning**
                - *Supervised Learning*
                    - Classification
                    - Regression
                - *Unsupervised Learning*
                    - Clustering
                    - Association
    
    Pass the markdown to the upsert_mindmap function
    Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    upsert_mindmap,
    caller=mindmap_creator,
    executor=user_proxy,
    description="upsert into database",
)

def get_suggestions(flip_id):
    suggester_user = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE")
    )
    suggester = AssistantAgent(
        name="suggester", 
        llm_config={
            "config_list": config_list,
            "cache_seed": None,
            "temperature": 0.0,
        }, 
        system_message="""
        Get all texts from elements of a 2D canvas and suggest three topics for mindmaps based on them. If there is no text, suggest topics about AI.

        Respond in JSON and nothing else: 
        {
            "suggestions": ["..."]
        }
    """,
    )
    agentchat.register_function(
        get_all_text_from_flip,
        caller=suggester,
        executor=suggester_user,
        description="Get all text from a canvas",
    )

    suggester_user.initiate_chat(suggester, message=f"flip_id: '{flip_id}'", max_turns=2)
    last_message = suggester_user.last_message()['content'].replace("TERMINATE", "").strip()
    data = json.loads(last_message)
    return data['suggestions']

flip_id = os.getenv("FLIP_ID")


while True:
    suggestions = get_suggestions(flip_id=flip_id)
    answers = inquirer.prompt([
        inquirer.List(
            'choice',
            message="Here are some suggestions:",
            choices=suggestions + ["other"],
            carousel=True
        )
    ])
    query = answers['choice']

    if query == 'other':
        query = input("mindmap 🗺️: ")

    user_proxy.initiate_chat(
        mindmap_creator,
        message=f"flip_id: '{flip_id}', context: {query}"
    )

