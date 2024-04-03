from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from art_generation import ArtGeneration
from dotenv import load_dotenv
import os

load_dotenv()
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

art_generation = ArtGeneration(
    email=os.getenv("ART_GENERATION_EMAIL"),
    password=os.getenv("ART_GENERATION_PASSWORD"),
)

def generate_image(prompt: str) -> str:
    return art_generation.generate_image(prompt)

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin. Execute code provided by the combiner.",
    code_execution_config={"work_dir": "stories", "use_docker": False},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

story_outliner = AssistantAgent(
    name="story_outliner", 
    llm_config={
        "config_list": config_list,
        "cache_seed": 41,
        "stream": True,
        "temperature": 0.2,
    }, 
    system_message="""Given a topic, write a story outline including the main characters, acts, key scenes and themes. Reply 'TERMINATE' if the task is done""",
)

writer = AssistantAgent(
    name="writer", 
    llm_config={
        "config_list": config_list,
        "cache_seed": 41,
        "stream": True,
        "temperature": 0.0,
    }, 
    system_message="""
    You are a professional writer. Given a story outline, write a full story. Include descriptions of apparances of main characters, descriptions of their appearance instead, including their age, race, gander, clothing, facial features, hair, etc. 
    Reply 'TERMINATE' if the task is done""",
)

image_generator = AssistantAgent(
    name="image_generator", 
    llm_config={
        "config_list": config_list,
        "cache_seed": 42,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""
    Given a story, write several movie still descriptions that can be used to generate an image. 
    Follow this pattern: [type of shot] of [adjective] [subject] [doing action], [setting], [items in the scene], [lighting], shot on [camera].
    Do not include the square brackets in the description. Avoid abstract concepts. If there is a person in the scene, always write description their age, race, gander, clothing, facial features, hair, etc.
    List all the descriptions, than call generate_image.
    Final output should be a in JSON format, like this: { "images": [{"link":"https://example.com/image.png", "description": "description1"}, {"link":"https://example.com/image.png", "description": "description2"}] }
    Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    generate_image,
    caller=image_generator,
    executor=user_proxy,
    description="Generate an image with a prompt",
)

# image_creator = AssistantAgent(
#     name="image_creator", 
#     llm_config={
#         "config_list": config_list,
#         # "cache_seed": None,
#         "cache_seed": 43,
#         "temperature": 0.0,
#     }, 
#     human_input_mode="NEVER",
#     system_message="""Given a list of prompts, create an image for every prompt.
#     Final output should be a list of all image links, like this:
#     - https://example.com/image.png (short description)
#     Reply 'TERMINATE' if the task is done""",

# )
# agentchat.register_function(
#     generate_image,
#     caller=image_creator,
#     executor=user_proxy,
#     description="Generate an image with a prompt",
# )

combiner = AssistantAgent(
    name="combiner", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    description="Must be called last",
    system_message="""Combine the generated image links from image_generator with the full story from writer. Images must be in the text close to the related story parts. Suggest python code (in a python coding block) or shell script (in a sh coding block) that will save everything in an .md file. Reply 'TERMINATE' if the task is done""",
)

groupchat = GroupChat(
    agents=[
        user_proxy, 
        story_outliner, 
        writer, 
        image_generator, 
        combiner
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
    topic = input("Topic: ")
    if topic.lower() == "quit":
        break
    user_proxy.initiate_chat(manager, message=f"""Write a story outline about {topic}.""")



