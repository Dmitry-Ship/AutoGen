from .agents import youtube_transcriber, suggester, user_proxy

def main():
    """Main function"""
    while True:
        query = input("YouTube 📺:")

        user_proxy.initiate_chats(
            [
                {
                    "recipient": youtube_transcriber,
                    "message": query,
                    "max_turns": 2,
                },
                {
                    "recipient": suggester,
                    "message": "initial query: " + query,
                },
            ]
        )


if __name__ == "__main__":
    main()

