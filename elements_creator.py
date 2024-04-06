import json
from typing_extensions import Annotated, Optional
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from postgres import PostgresManager
from dotenv import load_dotenv
import os
from ulid import ULID
from typing import Annotated, Optional
import json

load_dotenv(override=True)
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")

db_connection = PostgresManager()
db_connection.connect_with_url(os.getenv("DB_URI"))

def create_db_id():
    id = ULID()
    return str(id.to_uuid())

def create_element_dict(
    element_type: str,
    id: str,
    flip_id: str, 
    x: float, 
    y: float,
    height: Optional[float],
    width: Optional[float],
    properties: dict
) -> dict:
    base_dict = {
        "id": id,
        "flip_id": flip_id,
        "x_coordinate": x,
        "y_coordinate": y,
        "height": height,
        "width": width,
        "type": element_type,
        "properties": json.dumps(properties)
    }
    return base_dict

def create_sticker_dict(
    id: Annotated[str, "The id of the element"],
    flip_id: Annotated[str, "Flip id"], 
    x: Annotated[float, "The x coordinate of the element"], 
    y: Annotated[float, "The y coordinate of the element"], 
    text: Annotated[str, "The text of the element"],
    color: Annotated[Optional[str], "The color of the element, allowed values are #fff176ff, #FFFFFFff, #EE9595ff, #78C99Aff"] = "#fff176ff",
    height: Optional[float] = 100.0,
    width: Optional[float] = 100.0,
) -> dict:
    if color is None or color == "":
        color = "#fff176ff"
    properties = {
        "fillColor": color,
        "groupId": "",
        "internalId": id,
        "reactions": [],
        "sticker": {
            "isWide": False
        },
        "text": {
            "align": "center",
            "bold": False,
            "caseType": "default",
            "fill": "#000000ff",
            "fontFamily": "Inter",
            "italic": False,
            "placement": "center",
            "relativeFontSize": 0,
            "value": text,
            "wrapWidth": 6.7613525390625
        },
        "zIndex": 244
    }
    return create_element_dict('STICKER', id, flip_id, x, y, height, width, properties)

def create_text_dict(
    id: Annotated[str, "The id of the element"],
    flip_id: Annotated[str, "Flip id"], 
    x: Annotated[float, "The x coordinate of the element"], 
    y: Annotated[float, "The y coordinate of the element"], 
    text: Annotated[str, "The text of the element"],
    height: Optional[float] = 18.16,
    width: Optional[float] = 200,
) -> dict:
    properties = {
        "groupId": "",
        "internalId": id,
        "rotation": 0,
        "text": {
            "align": "left",
            "bold": False,
            "caseType": "default",
            "fill": "#000000ff",
            "fontFamily": "Inter",
            "fontSize": 14,
            "italic": False,
            "value": text,
            "wrapWidth": 200
        },
        "zIndex": 248
    }
    return create_element_dict('TEXT', id, flip_id, x, y, height, width, properties)

def create_arrow_dict(
    id: Annotated[str, "The id of the element"],
    flip_id: Annotated[str, "Flip id"], 
    startElementId: Annotated[str, "The id of the start element"],
    startElementSide: Annotated[str, "The side of the start element, allowed values are TOP, BOTTOM, LEFT, RIGHT"],
    endElementId: Annotated[str, "The id of the end element"],
    endElementSide: Annotated[str, "The side of the end element, allowed values are TOP, BOTTOM, LEFT, RIGHT"],
) -> dict:
    coords = {
        "TOP": [0.5, 0],
        "BOTTOM": [0.5, 1],
        "LEFT": [0, 0.5],
        "RIGHT": [1, 0.5]
    }
    properties = {
        "arrow": {
            "endDecorationType": "arrow",
            "lineStyle": "solid",
            "lineWidth": 2,
            "path": [
                {
                    "elementId": startElementId,
                    "point": {
                        "x": coords[startElementSide][0],
                        "y": coords[startElementSide][1],
                    },
                    "type": "element"
                },
                {
                    "elementId": endElementId,
                    "point": {
                        "x": coords[endElementSide][0],
                        "y": coords[endElementSide][1],
                    },
                    "type": "element"
                }
            ],
            "startDecorationType": "none",
            "type": "curved"
        },
        "fillColor": "#000000ff",
        "groupId": "",
        "internalId": id,
    }
    return create_element_dict('ARROW', id, flip_id, 0, 0, 0, 0, properties)

def relative_position(square1, square2):
    # Check right
    if square2['x'] - square1['x'] == 100 and square2['y'] == square1['y']:
        return ['RIGHT', "LEFT"]
    # Check left
    elif square1['x'] - square2['x'] == 100 and square2['y'] == square1['y']:
        return ['LEFT', "RIGHT"]
    # Check top
    elif square2['y'] - square1['y'] == 100 and square2['x'] == square1['x']:
        return ['TOP', "BOTTOM"]
    # Check bottom
    elif square1['y'] - square2['y'] == 100 and square2['x'] == square1['x']:
        return ['BOTTOM', "TOP"]
    else:
        return ['RIGHT', "LEFT"]
    
def refine(structure: Annotated[str, "The json string to be refined"] ) -> Annotated[str, "The refined json string"]:
    # Parse the JSON string into a Python dictionary
    print("REFINING", structure)
    data = json.loads(structure)
    
    # Initialize a dictionary to keep track of old IDs to new IDs mapping
    id_mapping = {}
    items_mapping = {}
    
    # Update IDs in 'stickers' and 'texts', and populate the id_mapping dictionary
    for category in ['stickers', 'texts']:
        if category not in data:
            continue

        for item in data[category]:
            old_id = item['id']
            new_id = create_db_id()
            item['id'] = new_id
            id_mapping[old_id] = new_id
            items_mapping[new_id] = item

    for item in items_mapping.values():
        if 'connects_to' in item and item['connects_to'] in id_mapping:
            target_id = id_mapping[item['connects_to']]
            target = items_mapping[target_id]
            if target is None:
                continue

            positions = relative_position(item, target)
            arrow = {
                'start_element_id': target['id'] ,
                'start_element_side': positions[1],
                'end_element_id': item['id'],
                'end_element_side': positions[0]
            }

            if 'arrows' not in data:
                data['arrows'] = [arrow]
            else:
                data['arrows'].append(arrow) 

    return data

def refine_and_upsert(structure : Annotated[str, "The json to be refined"] ) -> Annotated[str, "The result of the query"]:
    print("REFINING ELEMENTS")
    refined = refine(structure.replace('\"', '"'))
    print("REFINED ELEMENTS")

    flip_id = refined['flip_id']

    if 'stickers' in refined:
        stickers = refined['stickers']
        for sticker in stickers:
            db_connection.upsert('elements', create_sticker_dict(sticker['id'], flip_id, sticker['x'], sticker['y'], sticker['text'], sticker.get('color')))
        print("UPSERTED STICKERS")


    if 'texts' in refined:
        texts = refined['texts']
        for text in texts:
            db_connection.upsert('elements', create_text_dict(text['id'], flip_id, text['x'], text['y'], text['text']))
        print("UPSERTED TEXTS")
    
    if 'arrows' in refined: 
        arrows = refined['arrows']
        for arrow in arrows:
            db_connection.upsert('elements', create_arrow_dict(
                id=create_db_id(), 
                flip_id=flip_id, 
                startElementId=arrow['start_element_id'], 
                startElementSide=arrow['start_element_side'], 
                endElementId=arrow['end_element_id'], 
                endElementSide=arrow['end_element_side'])
            )
        print("UPSERTED ARROWS")

    return 'OK'


user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "stories", "use_docker": False},
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)


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
    Given a task create elements on a 2D canvas that satisfy the task.
    Available elements are:
    - stickers (used as logical blocks with text, can have arrows to show connections) 
    - texts (used as titles for groups of stickers, usually on top of the stickers)

    Drow it in ACII
    Reply 'TERMINATE' if the task is done""",
)


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
    Given a structure of elements, create the elements on a 2D canvas that satisfy the task. All elements must be evenly spaced in available coordinates.

    respond in json format:
    {
        "flip_id": "flip_id",
        "stickers": [{ # have width of 100 and height of 100, 
            "id": "number",
            "x": 0.0, # from 800000.0 to 800100.0
            "y": 0.0, # from 400000.0 to 400100.0
            "text": "text",
            "connects_to": "id of another sticker", # optional, use to draw and arrow to show relationship, dependency or progress
            "color": "#FFFFFFff" (default) | "#EE9595ff" (negative, unfinished) | "#78C99Aff" (positive, finished)
        }, ...],
        "texts": [{ # have height of 18 and width of 200 and must have gaps around them
            "id": "number",
            "x": 0.0, # from 800000.0 to 800200.0
            "y": 0.0, # from 400000.0 to 400200.0
            "text": "text"
        }, ...]}
    }
    pass the json to refine_and_upsert
    Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    refine_and_upsert,
    caller=elements_creator,
    executor=user_proxy,
    description="upsert into database",
)

groupchat = GroupChat(
    agents=[
        user_proxy, 
        elements_outliner,
        elements_creator,
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

