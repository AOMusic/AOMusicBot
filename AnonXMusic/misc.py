import socket
import time
import heroku3
from pyrogram import filters
import config
from AnonXMusic.core.mongo import mongodb
from .logging import LOGGER

Sudoers Filter
SUDOERS = filters.user()

Heroku App
HAPP = None

Boot Time
_boot_ = time.time()

def is_heroku():
    """
    Check if the app is running on Heroku.
    
    Returns:
        bool: True if the app is running on Heroku, False otherwise.
    """
    return "heroku" in socket.getfqdn()

Heroku Config Vars
XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(config.HEROKU_API_KEY),
    "https",
    str(config.HEROKU_APP_NAME),
    "HEAD",
    "master",
]

def dbb():
    """
    Initialize the local database.
    """
    global db
    db = {}
    LOGGER(__name__).info(f"Local Database Initialized.")

async def sudo():
    """
    Load sudoers from the database.
    """
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
    LOGGER(__name__).info(f"Sudoers Loaded.")

def heroku():
    """
    Configure the Heroku app.
    """
    global HAPP
    if is_heroku:
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = Heroku.app(config.HEROKU_APP_NAME)
                LOGGER(__name__).info(f"Heroku App Configured")
            except BaseException:
                LOGGER(__name__).warning(
                    f"Please make sure your Heroku API Key and Your App name are configured correctly in the heroku."
)
