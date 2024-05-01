
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from dotenv import load_dotenv
from tools.elements_creator_tools import upsert_mindmap
import os

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")


user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "stories", "use_docker": False},
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

mindmap_creator = AssistantAgent(
    name="mindmap_creator", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
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

groupchat = GroupChat(
    agents=[
        user_proxy, 
        mindmap_creator,
        # elements_creator,
    ],
    messages=[],
    max_round=20,
    allow_repeat_speaker=False,
    speaker_selection_method='round_robin',
)

manager = GroupChatManager(
    groupchat=groupchat, 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    })

while True:
    flip_id = os.getenv("FLIP_ID")
    user_proxy.reset()
    manager.reset()
    query = input("Topic: ")
    if query.lower() == "quit":
        break
    
    user_proxy.initiate_chat(manager, message=f"flip_id: '{flip_id}', context: {query}")

