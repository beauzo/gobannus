import os
from dotenv import load_dotenv

print(f"{__name__} loaded")

load_dotenv()


def get_env(env_var: str, default=None):
    try:
        env_var_value = os.environ[env_var]
    except KeyError:
        if default:
            return default

        raise KeyError

    return env_var_value
