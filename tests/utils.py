import os
import asyncio


def remove_os_env_temporarily() -> dict:
    old_env = os.environ.copy()
    os.environ.clear()
    for key, value in old_env.items():
        if key.startswith("BOLT_PYTHON_"):
            os.environ[key] = value
    return old_env


def restore_os_env(old_env: dict) -> None:
    os.environ.update(old_env)


def get_mock_server_mode() -> str:
    """Returns a str representing the mode.

    :return: threading/multiprocessing
    """
    mode = os.environ.get("BOLT_PYTHON_MOCK_SERVER_MODE")
    if mode is None:
        # We used to use "multiprocessing"" for macOS until Big Sur 11.1
        # Since 11.1, the "multiprocessing" mode started failing a lot...
        # Therefore, we switched the default mode back to "threading".
        return "threading"
    else:
        return mode


def get_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
