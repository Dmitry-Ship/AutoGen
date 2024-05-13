import json
import inquirer
from .agents import search_query_suggester, researcher, user_proxy

selected_suggestion = None
while True:
    if selected_suggestion is None:
        query = input("search 🔍: ")
    else:
        query = selected_suggestion

    user_proxy.initiate_chat(researcher, message=query, clear_history=True, max_turns=2)
    
    # search_result = user_proxy.last_message(researcher)['content'].replace("TERMINATE", "").strip()
    # user_proxy.initiate_chat(search_query_suggester, message=search_result, max_turns=1)

    # suggestions_result = user_proxy.last_message(search_query_suggester)['content'].replace("TERMINATE", "").strip()
    # data = json.loads(suggestions_result)
    # suggestions = data['related']

    # choice = inquirer.prompt([
    #     inquirer.List(
    #         'choice',
    #         message="Here are some suggestions:",
    #         choices=suggestions + ["other"],
    #         carousel=True
    #     )
    # ])

    # query = choice['choice']
    # if query == 'other':
    #     selected_suggestion = None
    #     continue

    # selected_suggestion = query




