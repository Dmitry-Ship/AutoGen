from typing import Annotated
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from art_generation import ArtGeneration
from dotenv import load_dotenv
import json
import os

def store_data(
    title: Annotated[str, "Story title"],
    chapters: Annotated[list[str], "List of full chapters"],
    images: Annotated[list[str], "List of image links corresponding to each chapter"]
) -> Annotated[str, "Stories stored successfully"]:

    if not os.path.exists('./stories/'):
        os.makedirs('./stories/')
        
    file_path = './stories/stories.json'
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump({'stories': []}, file)

    if 'stories' not in open(file_path, 'r').read():
        with open(file_path, 'w') as file:
            json.dump({'stories': []}, file)

    with open(file_path, 'r') as file:
        data = json.load(file)

    data['stories'].append({
        'title': title,
        'chapters': [{'chapter': chapter, 'image': image} for chapter, image in zip(chapters, images)]
    })

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

    return "Stories stored successfully"

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
    is_termination_msg=lambda x: x.get("content", "").rstrip().lower().endswith("terminate"),
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
    You are a professional writer. Given a story outline, write a full story. Include descriptions of apparances of main characters. You transform complex concepts into compelling narratives. 
    Reply 'TERMINATE' if the task is done""",
)

image_prompt_generator = AssistantAgent(
    name="image_prompt_generator", 
    llm_config={
        "config_list": config_list,
        "cache_seed": 42,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""
    Given a story, write a list of movie still descriptions that can be understood without the story context and names of the characters. Add as many details as possible.
    Follow this pattern: [type of shot] of [adjective] [subject] [doing action], [setting description], [description items in the scene], [lighting description], shot on [camera setting description].
    Do not include the square brackets. Avoid abstract concepts. If there is a person in the scene, always write description of their appearance.
    Reply 'TERMINATE' if the task is done""",
)


image_creator = AssistantAgent(
    name="image_creator", 
    llm_config={
        "config_list": config_list,
        # "cache_seed": None,
        "cache_seed": 43,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    system_message="""Given a list of prompts, create an image for every prompt. The final output should be a list of image links. Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    generate_image,
    caller=image_creator,
    executor=user_proxy,
    description="Generate an image with a prompt",
)

combiner = AssistantAgent(
    name="combiner", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
    }, 
    human_input_mode="NEVER",
    description="Must be called last",
    system_message="""Combine the generated image links from image_creator with the full story from writer. Suggest python code (in a python coding block) or shell script (in a sh coding block) that will save everything in an .md file. Reply 'TERMINATE' if the task is done""",
)


groupchat = GroupChat(
    agents=[
        user_proxy, 
        story_outliner, 
        writer, 
        image_prompt_generator, 
        image_creator, 
        combiner
    ],
    messages=[],
    allow_repeat_speaker=False,
    speaker_selection_method="auto",
)

manager = GroupChatManager(
    groupchat=groupchat, 
    # system_message="""Break down the task into subtasks. Decide who to assign the subtasks to according the their desceription.""",
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



