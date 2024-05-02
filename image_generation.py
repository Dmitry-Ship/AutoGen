from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from tools.art_generation import generate_image

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

user_proxy = UserProxyAgent(
    name="User",
    system_message="A human admin.",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=lambda x: "content" in x and x["content"] is not None and x["content"].rstrip().endswith("TERMINATE")
)

prompt_generator = AssistantAgent(
    name="prompt_generator", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        # "stream": True,
        "temperature": 1.0,
    }, 
    system_message="""Given a topic, write an image description.
Follow this pattern: [type of shot] of [subject], [setting], [items in the scene], [lighting], shot on [camera]
Reply 'TERMINATE' if the task is done""",
)
    
image_generator = AssistantAgent(
    name="image_generator", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        # "stream": True,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""Given image descriptions, generate images. Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    generate_image,
    caller=image_generator,
    executor=user_proxy,
    description="Generate an image with a prompt",
)

groupchat = GroupChat(
    agents=[
        user_proxy, 
        prompt_generator, 
        image_generator,
    ],
    messages=[],
    max_round=10,
    allow_repeat_speaker=False,
    speaker_selection_method="round_robin",
)

manager = GroupChatManager(
    groupchat=groupchat, 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    })

while True:
    topic = input("🏞️ : ")
    if topic.lower() == "quit":
        break

    user_proxy.initiate_chat(manager, message=topic)



