from typing_extensions import Annotated
import os

default_path = "test_app/"

def list_dir(directory: Annotated[str, "Directory to check."]) -> Annotated[list[str], "List of files in the directory"]:
    files = os.listdir(default_path + directory)
    return 0, files

def see_file(filename: Annotated[str, "Name and path of file to check."]) -> Annotated[str, "File contents"]:
    with open(default_path + filename, "r") as file:
        lines = file.readlines()
    formatted_lines = [f"{i+1}:{line}" for i, line in enumerate(lines)]
    file_contents = "".join(formatted_lines)

    return 0, file_contents

def modify_code(
    filename: Annotated[str, "Name and path of file to change."],
    start_line: Annotated[int, "Start line number to replace with new code."],
    end_line: Annotated[int, "End line number to replace with new code."],
    new_code: Annotated[str, "New piece of code to replace old code with. Remember about providing indents."],
) -> Annotated[tuple[int, str], "Status code and message"]:
    with open(default_path + filename, "r+") as file:
        file_contents = file.readlines()
        file_contents[start_line - 1 : end_line] = [new_code + "\n"]
        file.seek(0)
        file.truncate()
        file.write("".join(file_contents))
    return 0, "Code modified"


def create_file_with_code(
    filename: Annotated[str, "Name and path of file to create."], code: Annotated[str, "Code to write in the file."]
) -> Annotated[tuple[int, str], "Status code and message"]:
    with open(default_path + filename, "w") as file:
        file.write(code)
    return 0, "File created successfully"