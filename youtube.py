from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from tools.yt import rag_youtube_transcription

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg = lambda x: "content" in x and x["content"].endswith("TERMINATE")
)

transcriber = AssistantAgent(
    name="transcriber", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""Given a youtube link, transcribe the video and answer the question. Write the word 'TERMINATE' at the end of the response if the task is done.""",
)
agentchat.register_function(
    rag_youtube_transcription,
    caller=transcriber,
    executor=user_proxy,
    description="Transcribe youtube video",
)

while True:
    query = input("YouTube 📺: ")
    if query.lower() == "quit":
        break

    user_proxy.initiate_chat(transcriber, message=query)
