
import inquirer
import os
from .agents import get_suggestions, mindmap_creator, user_proxy

flip_id = os.getenv("FLIP_ID")


while True:
    suggestions = get_suggestions(flip_id=flip_id)
    answers = inquirer.prompt([
        inquirer.List(
            'choice',
            message="Here are some suggestions:",
            choices=suggestions + ["other"],
            carousel=True
        )
    ])
    query = answers['choice']

    if query == 'other':
        query = input("mindmap 🗺️: ")

    user_proxy.initiate_chat(
        mindmap_creator,
        message=f"flip_id: '{flip_id}', context: {query}"
    )

