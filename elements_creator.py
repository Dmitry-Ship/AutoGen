from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from dotenv import load_dotenv
from tools.elements_creator_tools import refine_and_upsert
import os

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")


user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "stories", "use_docker": False},
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

    # example:
    # Overall structure: tree
    # 1. Text: "Registration Process User Flow for flip_id: 018eb39e-535e-0e4d-8590-d147a4ad751d" (Place this text at the top center of the canvas)
    # 2. Sticker: "Start" (Place this sticker at the top left corner of the canvas)
    # 3. Sticker: "Enter Email and Password" (Place this sticker below the "Start" sticker)
    # 4. Sticker: "Upload Profile Picture" (Place this sticker below and to the right of the "Enter Email and Password" sticker)

    # Now, draw arrows to connect the stickers in the following sequence:
    # - Start -> Enter Email and Password
    # - Enter Email and Password -> Upload Profile Picture


    # - drawing (used to draw a shape)
elements_outliner = AssistantAgent(
    name="elements_outliner", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    }, 
    human_input_mode="NEVER",
    system_message="""
    Given a task create elements on a 1000x500 2D canvas that satisfy the task.
    Available elements are:
    - stickers (used as logical blocks with text, can have arrows to show connections) 
    - texts (used as titles for groups of stickers, usually on top of the stickers)

    Reply 'TERMINATE' if the task is done""",
)


        # "drawing": { # have height and width of 100, use to draw on the canvas
        #     "x": 0.0, # 1000.0 max
        #     "y": 0.0, # 500.0 max
        #     "path": [0.0, 0.0, 0.1, 0.1, ...90.0, 90.0], # [x1, y1, x2, y2, ...] 0.0 to 100.0
        # }
elements_creator = AssistantAgent(
    name="elements_creator", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    }, 
    human_input_mode="NEVER",
    system_message="""
    Given a structure of elements, create elements on a 1000x500 2D canvas that satisfy the task.
    respond in json format:
    {
        "flip_id": "flip_id",
        "stickers": [{ # have height and width of 100, must have margin around them of at least 50px
            "id": "number",
            "x": 0.0, # 1000.0 max
            "y": 0.0, # 500.0 max
            "text": "text",
            "points_to": "id of another sticker", # optional, use to draw and arrow to show relationship, dependency or progress
            "color": "#FFFFFFff" (default) | "#EE9595ff" (negative, unfinished) | "#78C99Aff" (positive, finished)
        }, ...],
        "texts": [{ # have height of 18 and width of 200 and must have gaps around them
            "id": "number",
            "x": 0.0, # 1000.0 max
            "y": 0.0, # 500.0 max
            "text": "text"
        }, ...]}

    }
    pass the json to refine_and_upsert
    Reply 'TERMINATE' if the task is done""",
)

coordinator = AssistantAgent(
    name="coordinator", 
    llm_config={
        "config_list": config_list,
        "temperature": 0.0,
        "stream": True,
        "cache_seed": None
    }, 
    human_input_mode="NEVER",
    system_message="""
    Given a structure of elements, refine their x and y coordinates, so that elements have margins around them of at least 50px and spaced in a meaningful way.
    The canvas is 1000x500, stickers are 100x100, texts are 200x18.
    pass the json to refine_and_upsert
    Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    refine_and_upsert,
    caller=coordinator,
    executor=user_proxy,
    description="upsert into database",
)

groupchat = GroupChat(
    agents=[
        user_proxy, 
        # elements_outliner,
        elements_creator,
        coordinator,
    ],
    messages=[],
    max_round=20,
    allow_repeat_speaker=False,
    speaker_selection_method='round_robin',
)

manager = GroupChatManager(
    groupchat=groupchat, 
    llm_config={
        "config_list": config_list,
        "stream": True,
        "temperature": 0.0,
    })

while True:
    flip_id = os.getenv("FLIP_ID")
    user_proxy.reset()
    manager.reset()
    query = input("Topic: ")
    if query.lower() == "quit":
        break
    
    user_proxy.initiate_chat(manager, message=f"given this flip_id '{flip_id}', create {query}")

