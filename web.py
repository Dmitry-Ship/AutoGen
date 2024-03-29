from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from brave import Brave
from typing_extensions import Annotated
from dotenv import load_dotenv
load_dotenv()
brave = Brave()



config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Execute code provided by the saver.",
    code_execution_config={"work_dir": "coding", "use_docker": False},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

searcher = AssistantAgent(
    name="searcher", 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "cache_seed": 41,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""Look up the internet for links that match the query. The final output should be a list of website links. Reply 'TERMINATE' if the task is done""",
)
def search_internet(query: Annotated[str, "The query to search for"]) -> Annotated[list[str], "List of results"]:
    return brave.search(q=query, count=2)

agentchat.register_function(
    search_internet,
    caller=searcher,
    executor=user_proxy,
    description="Search the internet",
)

summary_writer = AssistantAgent(
    name="summary_writer",
    llm_config={
        "config_list": config_list,
        "stream": True,
        "cache_seed": 42,
        "temperature": 0.0,
    },
    system_message="""Given parsed content, summarize it as an article in a markdown format, include links. Reply 'TERMINATE' if the task is done""",
)

saver = AssistantAgent(
    name="saver",
    llm_config={
        "config_list": config_list,
        "stream": True,
        "cache_seed": None,
        "temperature": 0.0,
    },
    system_message="""Suggest python code (in a python coding block) or shell script (in a sh coding block) for the Admin to execute. The code should save the summary to an .md file.""",
)

groupchat = GroupChat(
    agents=[user_proxy, searcher, summary_writer, saver],
    messages=[],
    max_round=20,
    speaker_selection_method="auto",
)
manager = GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
    "stream": True,
    "temperature": 0.0,
})

while True:
    task = input("Topic: ")
    if task.lower() == "quit":
        break

    user_proxy.initiate_chat(manager, message=task)


