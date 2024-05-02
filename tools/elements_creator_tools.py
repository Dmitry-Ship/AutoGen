import json
from typing_extensions import Annotated, Optional
from infra.postgres import PostgresManager
from dotenv import load_dotenv
import os
from ulid import ULID
from typing import Annotated, Optional
import json
import re

load_dotenv(override=True)

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
        "x_coordinate": x + 80000,
        "y_coordinate": y + 40000,
        "height": height,
        "width": width,
        "type": element_type,
        "properties": json.dumps(properties)
    }
    return base_dict

def find_extremes(arr):
    # Assuming the array always has an even number of elements and at least one pair (x, y)
    min_x = max_x = arr[0]  # Initialize with the first x value
    min_y = max_y = arr[1]  # Initialize with the first y value
    
    for i in range(0, len(arr), 2):  # Step through the array in pairs
        x, y = arr[i], arr[i + 1]
        # Update min and max for x
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        # Update min and max for y
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
            
    return min_x, max_x, min_y, max_y

def create_drawing_dict(
    id: Annotated[str, "The id of the element"],
    flip_id: Annotated[str, "Flip id"], 
    x: Annotated[float, "The x coordinate of the element"], 
    y: Annotated[float, "The y coordinate of the element"], 
    path: Annotated[list[float], "The path of the element"],
) -> dict:
    properties = {
        "drawing": {
            "color": "#eb5757",
            "lineWidth": 10,
            "opacity": 1,
            "path": path,
        },
        "groupId": "",
        "internalId": id,
        "rotation": 0,
        "zIndex": 51
    }

    min_x, max_x, min_y, max_y = find_extremes(path)


    print("MIN MAX", min_x, max_x, min_y, max_y)

    return create_element_dict('DRAWING', id, flip_id, x, y, max_y, max_x, properties)
    
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
        if 'points_to' in item and item['points_to'] in id_mapping:
            target_id = id_mapping[item['points_to']]
            target = items_mapping[target_id]
            if target is None:
                continue

            positions = relative_position(item, target,)
            arrow = {
                'start_element_id':  item['id'],
                'start_element_side': positions[1],
                'end_element_id': target['id'],
                'end_element_side':  positions[0]
            }

            if 'arrows' not in data:
                data['arrows'] = [arrow]
            else:
                data['arrows'].append(arrow) 

    return data

def upsert(refined : Annotated[dict, "The json to be refined"], flip_id) -> Annotated[str, "The result of the query"]:
    if 'stickers' in refined:
        stickers = refined['stickers']
        print("💿 upserting stickers")
        for sticker in stickers:
            db_connection.upsert('elements', create_sticker_dict(sticker['id'], flip_id, sticker['x'], sticker['y'], sticker['text'], sticker.get('color')))

    if 'texts' in refined:
        texts = refined['texts']
        print("💿 upserting texts")
        for text in texts:
            db_connection.upsert('elements', create_text_dict(text['id'], flip_id, text['x'], text['y'], text['text']))
    
    if 'drawing' in refined: 
        drawing = refined['drawing']
        print("💿 upserting drawing")
        db_connection.upsert('elements', create_drawing_dict(
            id=create_db_id(), 
            flip_id=flip_id, 
            path=drawing['path'], 
            x=drawing['x'], 
            y=drawing['y'], 
        ))
    
    if 'arrows' in refined: 
        arrows = refined['arrows']
        print("💿 upserting arrows")
        for arrow in arrows:
            db_connection.upsert('elements', create_arrow_dict(
                id=create_db_id(), 
                flip_id=flip_id, 
                startElementId=arrow['start_element_id'], 
                startElementSide=arrow['start_element_side'], 
                endElementId=arrow['end_element_id'], 
                endElementSide=arrow['end_element_side'])
            )

    return 'OK'



def parse_markdown(md_text):
    lines = md_text.strip().split('\n')
    mind_map = []
    path = []
    depth_count = {}  # Dictionary to count the number of items at each depth

    # Canvas settings
    canvas_width = 1000
    canvas_height = 500
    root_x = canvas_width // 2
    root_y = canvas_height // 2

    root_found = False

    for line in lines:
        if line.strip().startswith('#') and not root_found:
            root_content = clean_text(line.strip('# ').strip())
            root_sticker = {
                "id": len(mind_map) + 1,
                "text": root_content,
                "x": root_x,
                "y": root_y,
                "color": "#EE9595ff",
                "height": 100,
                "width": 100,
            }
            mind_map.append(root_sticker)
            path.append(root_sticker)
            depth_count[0] = 1  # Initialize root level count
            root_found = True
            continue

        if not line.strip().startswith('-'):
            continue

        match = re.match(r"(\s*)-", line)
        if not match:
            continue

        level = len(match.group(1)) // 4 + 1

        if level < len(path):
            path = path[:level]

        parent_id = path[-1]['id'] if path and level > 0 else None

        if level not in depth_count:
            depth_count[level] = 0

        # Adjust spacing to fit within canvas
        x_increment = 150  # Adjusted horizontal shift
        y_spacing = 60  # Adjusted vertical spacing

        content = clean_text(line.strip())
        sticker = {
            "id": len(mind_map) + 1,
            "text": content,
            "x": root_x + (level * x_increment * (-1 if depth_count[level] % 2 else 1)),
            "y": root_y + (depth_count[level] * y_spacing * (-1 if depth_count[level] % 2 else 1)),
            "color": "#F2BD8Dff" if level == 1 else "#fff176ff" if level == 2 else "#78C99Aff" if level == 3 else "#FFFFFFff",
            "height": 100,
            "width": 100,
        }

        if parent_id:
            sticker['points_to'] = parent_id

        mind_map.append(sticker)
        path.append(sticker)
        depth_count[level] += 1

    return json.dumps({"stickers": mind_map}, indent=4)

def clean_text(text):
    # Removes markdown symbols used for formatting
    return re.sub(r"[\*\_\-]+", "", text)

def upsert_mindmap(markdown: Annotated[str, "The markdown to be upserted"], flip_id: Annotated[str, "Flip id"]) -> Annotated[str, "The result of the query"]:
    json_string = parse_markdown(markdown)
    refined = refine(json_string.replace('\"', '"'))

    return upsert(refined, flip_id)