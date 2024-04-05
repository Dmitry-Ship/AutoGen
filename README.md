# AutoGen

## ⚡️ Quick Start

1. create a file `OAI_CONFIG_LIST` and specify your model config

example:

```
[
    {
        "base_url": "http://0.0.0.0:8000",
        "api_key": "NULL"
    }
]
```

2. 

```
ART_GENERATION_EMAIL=qwerty
ART_GENERATION_PASSWORD=example@mail.com
ART_GENERATION_MODEL=138
BRAVE_API_KEY=qwerty
DB_URI=postgresql://<user>:<password>@<host>:<port>/<database>
```

2. scrpts


```
python storybook.py
```

```
python db.py
```

```
python db_writer.py
```