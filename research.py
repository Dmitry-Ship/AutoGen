from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager
from skills import search_internet, fetch_website

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
    code_execution_config=False,
)
user_proxy.register_for_execution()(search_internet)
user_proxy.register_for_execution()(fetch_website)

planner = AssistantAgent(
    name="Planner",
    # description="Planner should always be called before any of the agents.",
    system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a researcher who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a researcher.
""",
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    },
)

researcher = AssistantAgent(
    name="Researcher", 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0,
    }, 
    human_input_mode="NEVER",
    system_message="""Researcher. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code.""",
    # system_message="Researcher. You follow an approved plan. You are able to search the internet and follow links if necessary to gather up to date information. You don't write code. Do not analyze the content. Reply 'TERMINATE' if the task is done.",
)
# researcher.register_for_llm(description="Search the internet")(search_internet)
# researcher.register_for_llm(description="Follow a link and fetch the content of a website")(fetch_website)

engineer = AssistantAgent(
    name="Engineer",
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    },
    system_message="""Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
""",
)

executor = UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the python or bash code written by the engineer and report the result.",
    description="Executor should always be called after the engineer has written code to be executed.",
    human_input_mode="NEVER",
    code_execution_config={
        # "last_n_messages": 3,
        "work_dir": "paper",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

critic = AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL. Reply 'TERMINATE' if the task is done.",
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    },
)

# graph_dict = {}
# graph_dict[user_proxy] = [planner]
# graph_dict[planner] = [engineer, writer]
# graph_dict[engineer] = [executor]
# graph_dict[executor] = [writer]
# graph_dict[writer] = [critic, user_proxy]
# graph_dict[critic] = [writer]

groupchat = GroupChat(
    agents=[user_proxy, planner, engineer, executor, critic],
    messages=[],
    max_round=20,
    # allowed_or_disallowed_speaker_transitions=graph_dict, speaker_transitions_type="allowed"
    # speaker_transitions_type="allowed",
    speaker_selection_method="auto",
)
manager = GroupChatManager(groupchat=groupchat, llm_config={
    "config_list": config_list,
    "stream": True,
    "temperature": 0.0,
})

user_proxy.reset()
while True:
    task = input("Topic: ")
    if task.lower() == "quit":
        break
    chat_history = user_proxy.initiate_chat(
        manager,
        message=task,
        clear_history=False
    )

    user_proxy.initiate_chat(
        manager,
        message="store the result in an .md file",
        clear_history=False
    )

