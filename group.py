from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
llm_config = {
    "config_list": config_list,
}

coder = AssistantAgent(name="coder", llm_config=llm_config)
pm = AssistantAgent(name="product_manager", system_message="Break down the idea into a well scoped requirement for the coder", llm_config=llm_config)

user_proxy = UserProxyAgent(
    "user_proxy", 
    code_execution_config={"work_dir": "coding", "use_docker": False},
    human_input_mode="ALWAYS",
)

group_chat = GroupChat(agents=[user_proxy, coder, pm], messages=[])
group_chat_manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)

user_proxy.reset()

while True:
    task = input("Task: ")
    user_proxy.initiate_chat(
        group_chat_manager,
        message=task,
    )
