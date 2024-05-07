from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from .tools import search_internet, ask_context
from typing import Annotated

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE")
)

searcher = AssistantAgent(
    name="searcher", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""
    As a professional search expert, you possess the ability to search for any information on the web. 
    For each user query, utilize the search results to their fullest potential to provide additional information and assistance in your response.
    Aim to directly address the user's question, augmenting your response with insights gleaned from the search results.
    Include relevant URL links in your response.
    Please match the language of the response to the user's language. Write the word 'TERMINATE' at the end of the response."""
)
agentchat.register_function(
    search_internet,
    caller=searcher,
    executor=user_proxy,
    description="Search the internet",
)

writer = AssistantAgent(
    name="writer", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""
    As a professional writer, your job is to generate a comprehensive and informative, yet concise answer of 400 words or less for the given question based solely on the provided search results (URL and content). You must only use information from the provided search results. Use an unbiased and journalistic tone. Combine search results together into a coherent answer. Do not repeat text. If there are any images relevant to your answer, be sure to include them as well. Aim to directly address the user's question, augmenting your response with insights gleaned from the search results. 
    Whenever quoting or referencing information from a specific URL, always cite the source URL explicitly. Please match the language of the response to the user's language.
    Always answer in Markdown format. Links and images must follow the correct format.
    Link format: [link text](url)
    Image format: ![alt text](url)"""
)

search_query_suggester = AssistantAgent(
    name="search_query_suggester", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""
    Based on the provided information, suggest three followup search queries that progressivly delve deeper into the subject. 
    Respond in JSON and nothing else:
    {
        "related": ["query_1", "query_2", "query_3"]
    }

    Write the word 'TERMINATE' at the end of the response if the task is done.
""",
)

context_updater = AssistantAgent(
    name="context_updater", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""
    As a professional web researcher, your role is to deepen your understanding of the user's input by conducting further inquiries when necessary.
    After receiving an initial response from the user, carefully assess whether additional questions are absolutely essential to provide a comprehensive and accurate answer. Only proceed with further inquiries if the available information is insufficient or ambiguous.
    Otherwise call ask_context to get additional context and respond in JSON:
    {
        "query": "...", # rephrased user query, that includes the context
    }
""",
)
agentchat.register_function(
    ask_context,
    caller=context_updater,
    executor=user_proxy,
    description="Ask for additional information",
)

def search(query: Annotated[str, "The query to search for"]) -> Annotated[str, "The answer to the query"]:
    user_proxy.initiate_chats([
        {
            "recipient": context_updater,
            "message": query,
            "max_turns": 2,
        },
        {
            "recipient": searcher,
            "message": query,
            "max_turns": 2,
        },
        {
            "recipient": writer,
            "message": "write a good summary",
            "max_turns": 1,
        },
    ])
        
    return user_proxy.last_message(writer)['content'].replace("TERMINATE", "").strip()

researcher = AssistantAgent(
    name="researcher", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""
    As a professional search expert, you possess the ability to search for any information on the web. 
    For each user query, utilize the search results to their fullest potential to provide additional information and assistance in your response.
    Aim to directly address the user's question, augmenting your response with insights gleaned from the search results.
    Include relevant URL links in your response.
""",
)
agentchat.register_function(
    search,
    caller=researcher,
    executor=user_proxy,
    description="Search the internet",
)




