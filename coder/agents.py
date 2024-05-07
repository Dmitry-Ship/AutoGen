
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from dotenv import load_dotenv
from .tools import see_file, list_dir, create_file_with_code, modify_code

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    system_message="A human admin.",
    code_execution_config=False,
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

engineer = AssistantAgent(
    name="Engineer",
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    },
    system_message="""
    I'm Engineer. I'm expert in python programming. I'm executing code tasks required by Admin.
    """,
)
agentchat.register_function(
    list_dir,
    caller=engineer,
    executor=user_proxy,
    description="List files in choosen directory.",
)
agentchat.register_function(
    see_file,
    caller=engineer,
    executor=user_proxy,
    description="Check the contents of a chosen file.",
)
agentchat.register_function(
    modify_code,
    caller=engineer,
    executor=user_proxy,
    description="Replace old piece of code with new one. Proper indentation is important.",
)
agentchat.register_function(
    create_file_with_code,
    caller=engineer,
    executor=user_proxy,
    description="Create a new file with code.",
)

groupchat = GroupChat(
    agents=[engineer, user_proxy],
    messages=[],
    max_round=500,
    speaker_selection_method="round_robin",
    enable_clear_history=True,
)
manager = GroupChatManager(groupchat=groupchat, llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    })
