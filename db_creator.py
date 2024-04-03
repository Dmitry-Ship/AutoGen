import json
from typing_extensions import Annotated, Optional
from autogen import config_list_from_json, GroupChat, AssistantAgent, UserProxyAgent, GroupChatManager, agentchat
from postgres import PostgresManager
from dotenv import load_dotenv
import os
from ulid import ULID
from typing import Annotated, Optional
import json

load_dotenv()
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
            "type": "straight"
        },
        "fillColor": "#000000ff",
        "groupId": "",
        "internalId": id,
    }
    return create_element_dict('ARROW', id, flip_id, 0, 0, 0, 0, properties)

def refine(json_string : Annotated[str, "The json string to be refined"] ) -> Annotated[str, "The refined json string"]:
    # Parse the JSON string into a Python dictionary
    data = json.loads(json_string)
    
    # Initialize a dictionary to keep track of old IDs to new IDs mapping
    id_mapping = {}
    
    # Update IDs in 'stickers' and 'texts', and populate the id_mapping dictionary
    for category in ['stickers', 'texts']:
        if category in data:
            for item in data[category]:
                old_id = item['id']
                new_id = create_db_id()
                item['id'] = new_id
                id_mapping[old_id] = new_id
                
    # Update 'start_element_id' and 'end_element_id' in 'arrows'
    for arrow in data.get('arrows', []):
        if 'start_element_id' in arrow and arrow['start_element_id'] in id_mapping:
            arrow['start_element_id'] = id_mapping[arrow['start_element_id']]
        if 'end_element_id' in arrow and arrow['end_element_id'] in id_mapping:
            arrow['end_element_id'] = id_mapping[arrow['end_element_id']]
    # Convert the updated dictionary back to a JSON string
    return data

def refine_and_upsert(json_string : Annotated[str, "The json string to be refined"] ) -> Annotated[str, "The result of the query"]:
    refined = refine(json_string)
    print("REFINED ELEMENTS")


    # make stickers field exists
    if 'stickers' in refined:
        stickers = refined['stickers']
        for sticker in stickers:
            db_connection.upsert('elements', create_sticker_dict(sticker['id'], sticker['flip_id'], sticker['x'], sticker['y'], sticker['text'], sticker.get('color')))
        print("UPSERTED STICKERS")


    if 'texts' in refined:
        texts = refined['texts']
        for text in texts:
            db_connection.upsert('elements', create_text_dict(text['id'], text['flip_id'], text['x'], text['y'], text['text']))
        print("UPSERTED TEXTS")
    
    if 'arrows' in refined: 
        arrows = refined['arrows']
        for arrow in arrows:
            db_connection.upsert('elements', create_arrow_dict(
                id=create_db_id(), 
                flip_id=arrow['flip_id'], 
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
    You are working with a 2D canvas. Given a task create elements that satisfy the task. The result should be within these coorinates:
    x: from 863700.0 to 864700.0 
    y: from 479200.0 to 480200.0
    Elements should be have gaps between them.
    respond in json format:
    {
        "stickers": [{ # stickers are used as logical blocks with text, they have width of 100 and height of 100. A sticker without text implies a placeholder.
            "id": "number",
            "flip_id": "flip_id",
            "x": 0.0,
            "y": 0.0,
            "text": "text"
            "color": "#fff176ff" (negative, unfinished, hard) | "#FFFFFFff" (positive, finished, easy) | "#EE9595ff" (neutral) | "#78C99Aff" (default) # optional field
        }, ...],
        "texts": [{ # text elements are used as a title for groups of elements, they have height of 18 and width of 200
            "id": "number",
            "flip_id": "flip_id",
            "x": 0.0,
            "y": 0.0,
            "text": "text"
        }, ...]}
        "arrows": [{ # arrows are used to connect elements to show a relation between them.
            "flip_id": "flip_id",
            "start_element_id": "id if an element",
            "end_element_id": "id if an element",
            "start_element_side": "TOP" | "BOTTOM" | "LEFT" | "RIGHT", 
            "end_element_side": "TOP" | "BOTTOM" | "LEFT" | "RIGHT"
        }, ...]
    }
    call refine_and_upsert to upsert the elements into the database
    Reply 'TERMINATE' if the task is done""",
)
agentchat.register_function(
    refine_and_upsert,
    caller=elements_creator,
    executor=user_proxy,
    description="upsert into database",
)

# groupchat = GroupChat(
#     agents=[
#         user_proxy, 
#         elements_creator,
#         # sql_runner
#     ],
#     messages=[],
#     max_round=20,
#     allow_repeat_speaker=False,
#     speaker_selection_method='auto',
# )

# manager = GroupChatManager(
#     groupchat=groupchat, 
#     llm_config={
#         "config_list": config_list,
#         "stream": True,
#         "temperature": 0.0,
#     })

while True:
    user_proxy.reset()
    elements_creator.reset()
    query = input("Topic: ")
    if query.lower() == "quit":
        break
    
    user_proxy.initiate_chat(elements_creator, message=f"given this flip_id '018ea043-9e96-450c-49ad-ae8bcda3ea3e', create {query}")

