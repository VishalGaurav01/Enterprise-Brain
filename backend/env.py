import os
from dotenv import load_dotenv
load_dotenv()

class PostgresConfig:
    def __init__(self):
        self.db = os.getenv("POSTGRES_DB")
        self.user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        self.host = os.getenv("POSTGRES_HOST")
        self.port = os.getenv("POSTGRES_PORT")
        self.url = os.getenv("POSTGRES_URL")

class Env:
    def __init__(self):
        self.postgres = PostgresConfig()