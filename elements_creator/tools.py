import json
from typing import Annotated, Optional
from infra.postgres import PostgresManager
from dotenv import load_dotenv
import os
from ulid import ULID
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

def refine(structure: Annotated[dict, "The json string to be refined"]) -> Annotated[dict, "The refined data"]:
    # Parse the JSON string into a Python dictionary
    # Initialize a dictionary to keep track of old IDs to new IDs mapping
    id_mapping = {}
    items_mapping = {}

    # Update IDs in 'stickers' and 'texts', and populate the id_mapping dictionary
    for category in ['stickers', 'texts']:
        if category not in structure:
            continue

        for item in structure[category]:
            old_id = item['id']
            new_id = create_db_id()
            item['id'] = new_id
            id_mapping[old_id] = new_id
            items_mapping[new_id] = item

    # Update arrows with relative positions for items pointing to multiple targets
    for item in items_mapping.values():
        if 'points_to' in item:
            updated_pointing_ids = []
            for point_id in item['points_to']:
                if point_id in id_mapping:
                    updated_pointing_ids.append(id_mapping[point_id])

            for new_id in updated_pointing_ids:
                target = items_mapping.get(new_id)
                if target is None:
                    continue

                positions = relative_position(item, target)
                arrow = {
                    'start_element_id': item['id'],
                    'start_element_side': positions[0],
                    'end_element_id': target['id'],
                    'end_element_side': positions[1]
                }

                if 'arrows' not in structure:
                    structure['arrows'] = [arrow]
                else:
                    structure['arrows'].append(arrow)

            item['points_to'] = updated_pointing_ids  # Update points_to with new IDs

    return structure 

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


# MIND MAP

def parse_line(line):
    """Parse the markdown line to determine its level and clean content."""
    if line.strip().startswith('#'):
        return 0, clean_text(line.strip('# ').strip())
    match = re.match(r"(\s*)-", line)
    if match:
        level = len(match.group(1)) // 4 + 1
        return level, clean_text(line.strip())
    return None, None

def create_sticker(id, text, x, y, level):
    """Create a sticker dictionary based on provided specifications."""
    colors = {0:"#EE9595ff", 1: "#F2BD8Dff", 2: "#fff176ff", 3: "#78C99Aff"}
    default_color = "#FFFFFFff"
    color = colors.get(level, default_color)
    return {
        "id": id, "text": text, "x": x, "y": y, "color": color, 
        "height": 100, "width": 100, "points_to": []
    }

def calculate_position(
        root_x: Annotated[int, "The root x position"], 
        root_y: Annotated[int, "The root y position"], 
        level: Annotated[int, "The level of the sticker"], 
        depth_count: Annotated[dict, "The dictionary of depth counts"], 
        x_increment=200, y_spacing=200):
    """Calculate position of the sticker based on its level and count."""
    x = root_x + (level * x_increment)
    y = root_y + (depth_count[level] * y_spacing)
    return x, y

def parse_mindmap_markdown(md_text):
    lines = md_text.strip().split('\n')
    mind_map = []
    path = []
    depth_count = {}

    # Canvas settings
    canvas_width, canvas_height = 1000, 500
    root_x, root_y = canvas_width // 2, canvas_height // 2

    root_found = False
    for line in lines:
        level, content = parse_line(line)
        if level is None:
            continue

        if level == 0 and not root_found:
            root_sticker = create_sticker(len(mind_map) + 1, content, root_x, root_y, level)
            mind_map.append(root_sticker)
            path.append(root_sticker)
            depth_count[level] = 1
            root_found = True
            continue

        if level > 0:
            if level <= len(path):
                path = path[:level]

            if level not in depth_count:
                depth_count[level] = 0

            x, y = calculate_position(root_x, root_y, level, depth_count)
            sticker = create_sticker(len(mind_map) + 1, content, x, y, level)
            mind_map.append(sticker)

            if path:
                path[-1]['points_to'].append(sticker['id'])

            path.append(sticker)
            depth_count[level] += 1

    return {"stickers": mind_map}

# def parse_mindmap_markdown(md_text):
#     lines = md_text.strip().split('\n')
#     mind_map = []
#     path = []
#     depth_count = {}  # Dictionary to count the number of items at each depth

#     # Canvas settings
#     canvas_width = 1000
#     canvas_height = 500
#     root_x = canvas_width // 2
#     root_y = canvas_height // 2

#     root_found = False

#     for line in lines:
#         if line.strip().startswith('#') and not root_found:
#             root_content = clean_text(line.strip('# ').strip())
#             root_sticker = {
#                 "id": len(mind_map) + 1,
#                 "text": root_content,
#                 "x": root_x,
#                 "y": root_y,
#                 "color": "#EE9595ff",
#                 "height": 100,
#                 "width": 100,
#                 "points_to": []  # Initialize points_to as an empty list
#             }
#             mind_map.append(root_sticker)
#             path.append(root_sticker)
#             depth_count[0] = 1  # Initialize root level count
#             root_found = True
#             continue

#         if not line.strip().startswith('-'):
#             continue

#         match = re.match(r"(\s*)-", line)
#         if not match:
#             continue

#         level = len(match.group(1)) // 4 + 1

#         if level <= len(path):
#             path = path[:level]

#         if level not in depth_count:
#             depth_count[level] = 0  # Initialize this level in depth_count if it's not already there

#         # Adjust spacing to fit within canvas
#         x_increment = 200  # Adjusted horizontal shift
#         y_spacing = 200  # Adjusted vertical spacing

#         content = clean_text(line.strip())
#         sticker = {
#             "id": len(mind_map) + 1,
#             "text": content,
#             "x": root_x + (level * x_increment),
#             "y": root_y + (depth_count[level] * y_spacing),
#             "color": "#F2BD8Dff" if level == 1 else "#fff176ff" if level == 2 else "#78C99Aff" if level == 3 else "#FFFFFFff",
#             "height": 100,
#             "width": 100,
#             "points_to": []
#         }

#         mind_map.append(sticker)
#         if path and level > 0:
#             path[-1]['points_to'].append(sticker['id'])
#         path.append(sticker)
#         depth_count[level] += 1  # Increment the count of elements at this level

#     return {"stickers": mind_map}

def clean_text(text):
    # Removes markdown symbols used for formatting
    return re.sub(r"[\*\_\-]+", "", text)

def upsert_mindmap(markdown: Annotated[str, "The markdown to be upserted"], flip_id: Annotated[str, "Flip id"]) -> Annotated[str, "The result of the query"]:
    print("parsing ...")
    structure = parse_mindmap_markdown(markdown)
    print("refining ...")
    refined = refine(structure)
    print("upserting ...")
    return upsert(refined, flip_id)

def get_all_text_from_flip(flip_id: Annotated[str, "Flip id"]) -> Annotated[str, "The result of the query"]:
    return db_connection.run_sql(f"""SELECT (e.properties)->'text'->'value' AS text_value
   FROM elements e
   WHERE flip_id = '{flip_id}'
   AND type IN ('STICKER', 'TEXT');""")
