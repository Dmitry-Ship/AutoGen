
import hashlib
import os
from dotenv import load_dotenv
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from autogen import config_list_from_json
load_dotenv()

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
recur_spliter = RecursiveCharacterTextSplitter(separators=["\n", "\r", "\t"])

def get_summary(text, question):
    hash = hashlib.md5(text.encode('utf-8')).hexdigest()
    file_path = f"rag_temp/{hash}.txt"

    if not os.path.isfile(file_path):
        with open(file_path, "w") as f:
            f.write(text)

    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant, responsible for summarizing information.",
        llm_config={
            "config_list": config_list,
            "cache_seed": None,
            "stream": False,
        },
    )
    # assistant.reset()

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        code_execution_config=False,
        # is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        retrieve_config={
            "task": "qa",
            "docs_path": file_path,
            "collection_name": hash, 
            "custom_text_split_function": recur_spliter.split_text,
            "get_or_create": True,
        },
    )

    ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=question, max_turns=1)
    return ragproxyagent.last_message()['content']