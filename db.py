from typing_extensions import Annotated
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from postgres import PostgresManager
from dotenv import load_dotenv
import os

load_dotenv()
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

db_connection = PostgresManager()
db_connection.connect_with_url(os.getenv("DB_URI"))

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Execute code provided by the combiner.",
    code_execution_config={"work_dir": "stories", "use_docker": False},
    human_input_mode="TERMINATE",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)
schema = db_connection.get_table_definitions_for_prompt()

print(f"schema: {schema}")
def run_query(query: Annotated[str, "The sql query to run"]) -> Annotated[str, "The result of the query"]:
    return db_connection.run_sql(query)

analyst = AssistantAgent(
    name="analyst", 
    llm_config={
        "config_list": config_list,
        "cache_seed": 42,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message=f"""
    You are an analyst. Given this database schema, suggest a query to extract data that can answer the question.
    schema: {schema}
    Reply 'TERMINATE' if the task is done""",
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
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""given a query result, suggest python code (in a python coding block) that will create a graph from the result. Reply 'TERMINATE' if the task is done""",
)

groupchat = GroupChat(
    agents=[
        user_proxy, 
        analyst, 
        graph_creator
    ],
    messages=[],
    max_round=20,
    allow_repeat_speaker=False,
    speaker_selection_method="auto",
)

manager = GroupChatManager(
    groupchat=groupchat, 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    })

while True:
    query = input("Topic: ")
    if query.lower() == "quit":
        break
    user_proxy.initiate_chat(manager, message=query)

