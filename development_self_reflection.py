import tempfile
from autogen import config_list_from_json, AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
from autogen.coding import LocalCommandLineCodeExecutor

temp_dir = tempfile.TemporaryDirectory()
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    code_execution_config={"executor": executor},
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
    I'm an Engineer. I'm expert in python programming.
    """,
)

code_reviewer = AssistantAgent(
    name="code_reviewer",
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    },
    system_message="""
   I'm code reviewer. I look through the provded code and provide recommendations on how to improve it, for example: magic numbers, unused variables, readability, etc.
    """,
)

def reflection_message(recipient, messages, sender, config):
    print("Reflecting...")
    return f"Reflect and provide critique on the following code. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"

user_proxy.register_nested_chats(
    [
        {
            "recipient": code_reviewer,
            "message": reflection_message,
            "max_turns": 1,
        },
    ],
    trigger=engineer,
    # position=4,
)

while True:
    query = input("Develop 🛠️: ")

    user_proxy.initiate_chat(
        engineer,
        message=query,
        max_turns=3,
    )