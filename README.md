# AutoGen

## Install

```
pip install -r requirements.txt
```

## Environment variables

1. create a  `OAI_CONFIG_LIST` file and specify your model config

example:

```
[
    {
        "base_url": "http://0.0.0.0:8000",
        "api_key": "NULL"
    }
]
```

2. Create a `.env` file

```
ART_GENERATION_EMAIL=qwerty
ART_GENERATION_PASSWORD=example@mail.com
ART_GENERATION_MODEL=138
BRAVE_API_KEY=qwerty
DB_URI=postgresql://<user>:<password>@<host>:<port>/<database>
```

## Commands

```
python -m image_generation.main
```

```
python -m research.main
```

```
python -m analyst.main
```

```
python -m elemens_creator.main
```