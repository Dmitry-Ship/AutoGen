from typing_extensions import Annotated
import autogen
from autogen import config_list_from_json 
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")


user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

writer = autogen.AssistantAgent(
    name="Writer",
    llm_config={"config_list": config_list},
    system_message="""
    You are a professional writer, known for your insightful and engaging articles.
    You transform complex concepts into compelling narratives.
    You should imporve the quality of the content based on the feedback from the user.
    """,
)

critic = autogen.AssistantAgent(
    name="Critic",
    llm_config={"config_list": config_list},
    system_message="""
    You are a critic, known for your thoroughness and commitment to standards.
    Your task is to scrutinize content for any harmful elements or regulatory violations, ensuring
    all materials align with required guidelines.
    For code
    """,
)

critic_executor = autogen.UserProxyAgent(
    name="Critic_Executor",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    code_execution_config={
        "last_n_messages": 1,
        "work_dir": "tasks",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)


@critic_executor.register_for_execution()
@critic.register_for_llm(name="check_harmful_content", description="Check if content contain harmful keywords.")
def check_harmful_content(content: Annotated[str, "Content to check if harmful keywords."]):
    # List of harmful keywords for demonstration purposes
    harmful_keywords = ["violence", "hate", "bullying", "death"]

    # Normalize the input text to lower case to ensure case-insensitive matching
    text = content.lower()

    print(f"Checking for harmful content...{text}", "yellow")
    # Check if any of the harmful keywords appear in the text
    for keyword in harmful_keywords:
        if keyword in text:
            return "Denied. Harmful content detected:" + keyword  # Harmful content detected

    return "Approve. TERMINATE"  # No harmful content detected


def reflection_message_no_harm(recipient, messages, sender, config):
    print("Reflecting...", "yellow")
    return f"Reflect and provide critique on the following writing. Ensure it does not contain harmful content. You can use tools to check it. \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}"


user_proxy.register_nested_chats(
    [
        {
            "sender": critic_executor,
            "recipient": critic,
            "message": reflection_message_no_harm,
            "max_turns": 2,
            "summary_method": "last_msg",
        }
    ],
    trigger=writer,  # condition=my_condition,
)

task = """Write a concise but engaging blogpost about Navida."""
res = user_proxy.initiate_chat(recipient=writer, message=task, max_turns=2, summary_method="last_msg")