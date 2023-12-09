from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
# Load LLM inference endpoints from an env variable or a file
# See https://microsoft.github.io/autogen/docs/FAQ#set-your-api-endpoints
# and OAI_CONFIG_LIST_sample
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

llm_config = {
    "timeout": 120,
    # "seed": 42,
    "config_list": config_list,
    "temperature": 0,
    # "max_tokens": -1,
    "stream": False,
}

assistant = AssistantAgent("assistant", llm_config=llm_config)
user_proxy = UserProxyAgent(
 name="user_proxy",
 human_input_mode="NEVER",
 max_consecutive_auto_reply=10,
 is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
 code_execution_config={"work_dir": "coding"},
 llm_config=llm_config,
 system_message="""Replay TERMINATE if the task has been solved at full satisfaction. Otherwise, replay CONTINUE, 
 or the reason why the task is not solved yet.""" 
)

task = "Plot a chart of NVDA and APPLE stock price change YTD."
user_proxy.initiate_chat(assistant, message=task)
