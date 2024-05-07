from .agents import manager, user_proxy

chat_result = user_proxy.initiate_chat(
    manager,
    message="""
You will need to work on the codebase in the current directory. For now, check out all the files, try to understand them and wait for next instructions.
""",
)