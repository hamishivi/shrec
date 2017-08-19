# shrec
Get Shreced

## Setting up dev environment

Requirements:
- `virtualenv`

```sh
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

There should be a `config.py` file in the root folder of the project. You can use the following template to create it.

```
# Steam API key
API_KEY = "1234"
```

## Running the server
```
./run.py
```
