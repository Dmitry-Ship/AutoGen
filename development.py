import tempfile
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from dotenv import load_dotenv
from autogen.coding import LocalCommandLineCodeExecutor
from typing_extensions import Annotated

temp_dir = tempfile.TemporaryDirectory()
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    # human_input_mode="ALWAYS",
    max_consecutive_auto_reply=2,
    code_execution_config={"executor": executor},
)


product_manager = AssistantAgent(
    name="product_manager",
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    },

    system_message="""
   You are a product manager. Your goal is to write a list of functional requirements for a developer. 
   Given an idea from user, analyze it and of it's not clear, ask for clarification by calling ask_context.
    """,
)
def ask_context(question: Annotated[str, "Question to specify context"]) -> Annotated[str, "Additional context"]:
    additional_query = input("❓ " + question + ": ")
    return additional_query

agentchat.register_function(
    ask_context,
    caller=product_manager,
    executor=user_proxy,
    description="Ask for additional information",
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
   I'm code reviewer. I look through the provded code and provide recommendations on how to improve it, for example: magic numbers, unused variables, readability, etc. Write the word 'TERMINATE' at the end of the response if the task is done
    """,
)

groupchat = GroupChat(
    agents=[engineer, user_proxy],
    messages=[],
    max_round=500,
    speaker_selection_method="auto",
    enable_clear_history=True,
)
manager = GroupChatManager(groupchat=groupchat, llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    })


while True:
    query = input("Develop 🛠️: ")

    user_proxy.initiate_chats([
            {
                "recipient": product_manager,
                "message": query,
                "max_turns": 2,
            },
            {
                "recipient": engineer,
                "message": "write the code that is supposed to implement: " + query,
                "max_turns": 1,
            },
            {
                "recipient": code_reviewer,
                "message": "review the code that is supposed to implement: " + query + " and write a better version",
            },
        ])