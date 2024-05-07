from .agents import get_suggestions, analyst, graph_creator, user_proxy
import inquirer

while True:
    suggestions = get_suggestions()
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

    user_proxy.initiate_chats([
        {
            "recipient": analyst,
            "message": query,
            "max_turns": 3,
        },
        {
            "recipient": graph_creator,
            "message": "initial query: " + query,
        },
    ])