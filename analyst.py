import json
import tempfile
from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
import inquirer
from tools.analyst_tools import run_query, get_schema
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
    You are an analyst. Retrieve the database schema, suggest a query to extract data that can answer the question, pass it to the run_query function. 
    Return the result of run_query
    Write 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    get_schema,
    caller=analyst,
    executor=user_proxy,
    description="Retrieve database schema",
)
agentchat.register_function(
    run_query,
    caller=analyst,
    executor=user_proxy,
    description="Run sql query",
)

graph_creator = AssistantAgent(
    name="graph_creator", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""given a query result, suggest python code (in a python coding block) that will create a graph from the result. Reply 'TERMINATE' if the task is done""",
)

def get_suggestions():
    suggester_user = UserProxyAgent(
        name="User",
        code_execution_config=False,
        is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE")
    )
    suggester = AssistantAgent(
        name="suggester", 
        llm_config={
            "config_list": config_list,
            "cache_seed": None,
            "temperature": 0.0,
        }, 
        system_message=f"""
        Retrieve the database schema, suggest three question that can be asked to reveal interesting correlations in the data.

        Respond in JSON an nothing else: 
        {{
            "suggestions": ["..."]
        }}
    """,
    )
    agentchat.register_function(
        get_schema,
        caller=suggester,
        executor=suggester_user,
        description="Retrieve database schema",
    )

    suggester_user.initiate_chat(suggester, message=f"suggest three questions", max_turns=2)
    if suggester_user.last_message()['content'] is None:
        return []
    
    last_message = suggester_user.last_message()['content'].replace("TERMINATE", "").strip()
    data = json.loads(last_message)
    return data['suggestions']

while True:
    suggestions = get_suggestions()
    answers = inquirer.prompt([
        inquirer.List(
            'choice',
            message="Here are some suggestions:",
            choices=suggestions + ["other"],
            carousel=True
        )
    ])
    query = answers['choice']

    if query == 'other':
        query = input("mindmap 🗺️: ")

    user_proxy.initiate_chats([
        {
            "recipient": analyst,
            "message": query,
            "max_turns": 3,
        },
        {
            "recipient": graph_creator,
            "message": "initial query: " + query,
        },
    ])


