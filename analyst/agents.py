import tempfile
from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from .tools import run_query, get_schema
from autogen.coding import LocalCommandLineCodeExecutor

temp_dir = tempfile.TemporaryDirectory()
executor = LocalCommandLineCodeExecutor(
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    system_message="A human admin. Execute provided code",
    code_execution_config={"executor": executor},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE")
)

analyst = AssistantAgent(
    name="analyst", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message=f"""
    You are an analyst. Your goal is to solve a given by retrieving data from the database.
    Here is the schema of the database:
    {get_schema()}

    Use run_query to retrieve data from the database. 
    If you are asked to visualize the data, write python code (in a python coding block) that will create a graph visualization of provided data.
    Write 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    run_query,
    caller=analyst,
    executor=user_proxy,
    description="Run sql query",
)






