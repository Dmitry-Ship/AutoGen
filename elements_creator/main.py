
import json
import inquirer
import os
from .agents import suggester, suggester_user, mindmap_creator, user_proxy

flip_id = os.getenv("FLIP_ID")


def get_suggestions(flip_id):
    suggester_user.initiate_chat(suggester, message=f"flip_id: '{flip_id}'", max_turns=2)
    last_message = suggester_user.last_message()['content'].replace("TERMINATE", "").strip()
    data = json.loads(last_message)
    return data['suggestions']

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

