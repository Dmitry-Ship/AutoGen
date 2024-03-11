from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
llm_config = {
    "config_list": config_list,
    "stream": True,
}

assistant = AssistantAgent("assistant", llm_config=llm_config)

user_proxy = UserProxyAgent(
    "user_proxy", 
    code_execution_config={"work_dir": "coding", "use_docker": False},
    human_input_mode="NEVER",
#     system_message="""Replay TERMINATE if the task has been solved at full satisfaction. Otherwise, replay CONTINUE, 
#  or the reason why the task is not solved yet.""" ,
#     is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
)

# Start the chat
user_proxy.initiate_chat(
    assistant,
    # message="Plot a chart of NVDA and TESLA stock price change YTD.",
    message="Write and run a snake game in python",
)