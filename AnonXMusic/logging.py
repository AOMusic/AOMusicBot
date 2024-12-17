import logging

#Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)

#Suppressing Third-Party Library Logs
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)

def LOGGER(name: str) -> logging.Logger:
    """
    Returns a logger instance with the given name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: A logger instance with the given name.
    """
    return logging.getLogger(name)
