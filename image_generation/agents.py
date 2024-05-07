from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, agentchat
from .tools import generate_images

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
        "temperature": 1.0,
    }, 
    system_message="""Given a topic, write an image description.
Follow this pattern: [type of shot] of [subject], [description of the subject], [setting], [items in the scene], [lighting], shot on [camera]
Write 'TERMINATE' if the task is done""",
)
    
image_generator = AssistantAgent(
    name="image_generator", 
    llm_config={
        "config_list": config_list,
        "cache_seed": None,
        "temperature": 0.0,
    }, 
    system_message="""Given image description, generate images. Write the word 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    generate_images,
    caller=image_generator,
    executor=user_proxy,
    description="Generate images with a prompt",
)



