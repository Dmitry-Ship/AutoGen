import hashlib
from bs4 import BeautifulSoup
import requests
from typing_extensions import Annotated
from dotenv import load_dotenv
from brave import Brave
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from autogen import config_list_from_json
load_dotenv()
brave = Brave()

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
llm_config = {
    "config_list": config_list,
    "cache_seed": None,
    "stream": False,
}

recur_spliter = RecursiveCharacterTextSplitter(separators=["\n", "\r", "\t"])

def search_internet(query: Annotated[str, "The query to search for"]) -> Annotated[str, "The answer to the query"]:
    print("🔍 searching ...")
    response = brave.search(q=query, count=5)
    urls_list = [str(url) for url in response.urls]
    for i, url in enumerate(urls_list):
        print(f"✅ search result {i+1}: {url}")
    answer = """"""
    for url in response.urls:
        print("🌐 scraping ", url)
        status, content = scrape_page(url)
        if status == 1:
            print("❌ scraping failed")
            continue
        if len(content) > 1000:
            print("📝 content too long, summarizing", url)
            content = get_summary(str(url), content, query)
        print("✅ scraping complete")
        answer += f"Here is content from {url} : \n {content} \n\n"

    return answer


def get_summary(url, text, question):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    # save text to file
    with open(f"rag_temp/{url_hash}.txt", "w") as f:
        f.write(text)  

    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant",
        human_input_mode="NEVER",
        llm_config=llm_config,
    )
    # assistant.reset()

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        code_execution_config=False,
        human_input_mode="NEVER",
        # is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        retrieve_config={
            "task": "qa",
            "docs_path": f"rag_temp/{url_hash}.txt",
            "collection_name": url_hash, 
            "custom_text_split_function": recur_spliter.split_text,
        },
    )

    response = ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=question)
    return response.chat_history[-1]['content']

def scrape_page(url: Annotated[str, "The url to scrape"]) -> Annotated[tuple[int, str], "The text from the url"]:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return 0, text
        else:
            return 1, "Failed to retrieve the webpage. Status code: {}".format(response.status_code)
    except:
        return 1, "Failed to retrieve the webpage"

    

