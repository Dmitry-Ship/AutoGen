from typing_extensions import Annotated
from dotenv import load_dotenv
from tavily import TavilyClient
import os

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_internet(query: Annotated[str, "The query to search for"]) -> Annotated[str, "The answer to the query"]:
    print("🔍 searching ...")
    response = tavily.search(query=query, search_depth="advanced")
    context = [{"url": obj["url"], "content": obj["content"]} for obj in response['results']]

    return context
    # return """[{"url": "https://www.marvel.com/movies", "content": "Endgame\n2019\nCaptain Marvel\n2019\nAnt-Man and The Wasp\n2018\nAvengers: Infinity War\n2018\nBlack Panther\n2018\nThor: Ragnarok\n2017\nSpider-Man: Homecoming\n2017\nGuardians of the Galaxy Vol. 2\n2017\nDoctor Strange\n2016\nCaptain America: Civil War\n2016\nAnt-Man\n2015\nAvengers: Age of Ultron\n2015\nGuardians of the Galaxy\n2014\nCaptain America: The Winter Soldier\n2014\nThor: The Dark World\n2013\nIron Man 3\n2013\n The Avengers\n2012\nCaptain America: The First Avenger\n2011\nOther Movies\nX-Men: Dark Phoenix\n2019\nVenom\n2018\nDeadpool 2\n2018\nLogan\n2017\nX-Men: Apocalypse\n2016\nDeadpool\n2016\nX-Men: Days of Future Past\n2014\nThe Amazing Spider-Man\n2012\nSpider-Man 3\n2007\nSpider-Man 2\n2004\nSpider-Man\n2002\nMARVEL MUSIC PLAYLIST\nGet Rewarded for Being a Marvel Fan\nAccess Over 30,000+ Digital Comics Doctor Strange in the Multiverse of Madness\n2022\nSpider-Man: No Way Home\n2021\nEternals\n2021\nShang-Chi and The Legend of The Ten Rings\n2021\nBlack Widow\n2021\nSpider-Man: Far From Home\n2019\nAvengers: The Marvels\n2023\nGuardians of the Galaxy Vol. 3\n2023\nAnt-Man and The Wasp: Quantumania\n2023\nBlack Panther: Blade\nNOV 7, 2025\nThunderbolts\nJUL 25, 2025\nFantastic Four\nMAY 2, 2025\nCaptain America:"}]"""


    

