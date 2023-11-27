# Hanzi Memo

A helper for studying chinese

## How to run
### Environment
1. This project developed on python `3.10.12`
1. Prepare python virtual environment: `python -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate`
   1. Run `deactivate` to deactivate the virtual env
1. Install dependencies: `pip install -r requirements.txt`

### The Database
1. Prepare your database
    1. Or if you have docker, run `docker compose up -d` (with .env setup below)
1. Create `.env` file at project root (change the values accordingly)
    ```dotenv
    DB_USER=postgres
    DB_PASSWORD=somepassword
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=hanzi_memo
    DB_DEBUG=false
    ```
1. Create the tables:
    ```shell
    python -m alfred migrate

    # to drop all tables
    python -m alfred migrate drop
    ```
1. Parse and fill the database initial data, including dictionary, collections and sample text
   ```shell
   # 120,000+ entry, might take a long time
   python -m alfred seed_dict cedict

   # 6000+ entry + checking duplicate, might take a long time
   # you can selectively pick which collection to seed
   python -m alfred seed_coll hsk1 hsk2 hsk3 hsk4 hsk5 hsk6

   # load sample text
   python -m alfred seed_text demo
   ```
### Run the app
   1. To run the app
      ```shell
      # development
      litestar run --reload

      # deploy
      litestar run --host 0.0.0.0
      ```
   1. Schema available at
      ```http request
      GET /schema/
      ```
