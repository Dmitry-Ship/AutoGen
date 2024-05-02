
from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from tools.elements_creator_tools import upsert_mindmap
from dotenv import load_dotenv
import os

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    system_message="A human admin.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "stories", "use_docker": False},
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
    human_input_mode="NEVER",
    system_message="""
    Given a content, create a mindmap with at least 3 levels. Respond in markdown format. 
    Example:
    # AI Mindmap

    - **Artificial Intelligence**
    - **Machine Learning**
        - *Supervised Learning*
            - Classification
            - Regression
        - *Unsupervised Learning*
            - Clustering
            - Association
    
    pass the markdown to the upsert_mindmap function
    Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    upsert_mindmap,
    caller=mindmap_creator,
    executor=user_proxy,
    description="upsert into database",
)

flip_id = os.getenv("FLIP_ID")

while True:
    query = input("mindmap 🗺️: ")
    if query.lower() == "quit":
        break
    
    user_proxy.initiate_chat(mindmap_creator, message=f"flip_id: '{flip_id}', context: {query}")

