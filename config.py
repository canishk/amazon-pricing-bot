import os
from dotenv import load_dotenv

class Config:
    def __init__(self, env_path=".env"):
        load_dotenv(env_path)

    def get(self, key, default=None):
        return os.getenv(key, default)