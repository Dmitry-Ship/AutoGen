

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
from skills import search_internet, fetch_website

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
llm_config = {
    "config_list": config_list,
}

assistant = AssistantAgent("assistant", llm_config=llm_config)

user_proxy = UserProxyAgent(
    "user_proxy", 
    code_execution_config={"work_dir": "coding", "use_docker": False},
    human_input_mode="NEVER",
    system_message="""Replay TERMINATE if the task has been solved at full satisfaction. Otherwise, replay CONTINUE, 
 or the reason why the task is not solved yet.""" ,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

user_proxy.register_for_execution()(search_internet)
assistant.register_for_llm(description="Search the internet")(search_internet)
    
user_proxy.register_for_execution()(fetch_website)
assistant.register_for_llm(description="Fetch the content of a website")(fetch_website)

while True:
    user_proxy.reset()
    task = input("Task: ")
    user_proxy.initiate_chat(
        assistant,
        message=task,
    )
