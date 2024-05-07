from .agents import engineer, user_proxy

while True:
    query = input("Develop 🛠️: ")

    user_proxy.initiate_chat(
        engineer,
        message=query,
        max_turns=3,
    )