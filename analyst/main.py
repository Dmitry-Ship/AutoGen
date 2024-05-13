from .agents import analyst, user_proxy

while True:
    query = input("Analyst 🧑‍🔬: ")
    
    user_proxy.initiate_chat(analyst, message=query, clear_history=False)
