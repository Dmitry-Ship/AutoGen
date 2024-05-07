from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from .tools import rag_youtube_transcription

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE"),
)

youtube_transcriber = AssistantAgent(
    name="youtube_transcriber",
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    },
    system_message="Given a youtube link, transcribe the video and return the result.",
)
agentchat.register_function(
    rag_youtube_transcription,
    caller=youtube_transcriber,
    executor=user_proxy,
    description="Transcribe youtube video",
)

suggester = AssistantAgent(
    name="suggester",
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    },
    system_message="""
    Based on the provided information, suggest three search queries that progressivly delve deeper into the subject.
    Respond in JSON and nothing else:
    {
        "related": ["query_1", "query_2", "query_3"]
    }

    Write the word 'TERMINATE' at the end of the response if the task is done.
""",
)
