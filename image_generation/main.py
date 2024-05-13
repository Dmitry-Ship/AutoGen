from .agents import image_generator, user_proxy

while True:
    topic = input("🏞️ : ")

    user_proxy.initiate_chat(image_generator, message=topic, max_turns=2, clear_history=False)




