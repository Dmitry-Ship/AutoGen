from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat, GroupChat, GroupChatManager
from tools.search import search_internet

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
    human_input_mode="NEVER",
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

suggester = AssistantAgent(
    name="suggester", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""
    Based on the provided information, suggest three search queries that progressivly delve deeper into the subject.
    example:
    {
        "related": ["query_1", "query_2", "query_3"]
    }

    Write the word 'TERMINATE' at the end of the response if the task is done.
""",
)

# groupchat = GroupChat(
#     agents=[user_proxy, searcher, suggester],
#     messages=[],
#     speaker_selection_method="round_robin",
# )
# manager = GroupChatManager(groupchat=groupchat, llm_config={
#     "config_list": config_list,
#     # "stream": True,
#     "temperature": 0.0,
# })

while True:
    query = input("search 🔍: ")
    if query.lower() == "quit":
        break
    # result = user_proxy.initiate_chat(searcher, message=query)
    # user_proxy.initiate_chat(suggester, message=f"initial query: {query}, context: { result.chat_history[-1]['content']}")
    chat_results = user_proxy.initiate_chats([
            {
                "recipient": searcher,
                "message": query,
                "clear_history": True,
            },
            {
                "recipient": suggester,
                "message": "initial query: " + query,
            },
        ])
    # user_proxy.initiate_chat(manager, message=query)


