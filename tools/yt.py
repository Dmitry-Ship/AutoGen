import re
from youtube_transcript_api import YouTubeTranscriptApi
from typing_extensions import Annotated
from .common import get_summary

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Args:
        url: The YouTube URL as a string.
    Returns:
        The extracted video ID as a string, or None if the URL is invalid.
    """
    # Define a regular expression pattern to match different YouTube URL formats
    pattern = r"(?:v=|be/|/watch\?v=|\?feature=youtu.be/)([\w-]+)"

    # Use re.search to find the first match of the pattern in the URL
    match = re.search(pattern, url)

    # If a match is found, return the captured group (video ID)
    if match:
        return match.group(1)
    else:
        return None
    
def retreive_youtube_transcription(youtube_url: Annotated[str, "The youtube url to retreive transcriptions from"]) -> Annotated[str, "The combined transcript"]:
    """
    Useful to search for video transcriptions from the given url
    The input should be a youtube url string
    :param youtube_url: str, youtube url to retreive transcriptions
    """

    # Extract the video id from the youtube link
    video_id = get_video_id(youtube_url)

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Combine the text into single text
    combined_transcript = " ".join([item.get("text", "") for item in transcript])

    return combined_transcript

def rag_youtube_transcription(youtube_url: Annotated[str, "The youtube url to retreive transcriptions from"], question: Annotated[str, "The question to ask"]) -> Annotated[str, "The combined transcript"]:
    print("📝 transcribing ...")
    transcription = retreive_youtube_transcription(youtube_url)

    return get_summary(transcription, question)