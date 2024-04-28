from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from tools.search import search_internet

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin.",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

searcher = AssistantAgent(
    name="searcher", 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""Search the internet for information that solves the task. Include links in the final answer. Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    search_internet,
    caller=searcher,
    executor=user_proxy,
    description="Search the internet",
)

while True:
    query = input("🔍: ")
    if query.lower() == "quit":
        break

    user_proxy.initiate_chat(searcher, message=query)


