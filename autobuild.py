from autogen import config_list_from_json, GroupChat, GroupChatManager
from autogen.agentchat.contrib.agent_builder import AgentBuilder

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
builder = AgentBuilder(config_file_or_env="OAI_CONFIG_LIST", builder_model='gpt-3.5-turbo-0125', agent_model='gpt-3.5-turbo-0125')

def start_task(execution_task: str, agent_list: list, llm_config: dict):
    group_chat = GroupChat(agents=agent_list, messages=[], max_round=12, allow_repeat_speaker=False)
    manager = GroupChatManager(
        groupchat=group_chat, llm_config={"config_list": config_list, **llm_config}
    )
    agent_list[0].initiate_chat(manager, message=execution_task)

while True:
    task = input("Topic: ")
    if task.lower() == "quit":
        break
    agent_list, agent_configs = builder.build(task, default_llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    }, coding=True)

    start_task(
        execution_task=task,
        agent_list=agent_list,
        llm_config={
            "config_list": config_list,
            "stream": True,
            "temperature": 0.0,
        }
    )

    builder.clear_all_agents(recycle_endpoint=True)