from .agents import image_generator, prompt_generator, user_proxy

while True:
    topic = input("🏞️ : ")

    user_proxy.initiate_chats([
        {
            "recipient": prompt_generator,
            "message": topic,
            "max_turns": 1,
        },
        {
            "recipient": image_generator,
            "message": "generate an image",
            "max_turns": 2,
        },
    ])



