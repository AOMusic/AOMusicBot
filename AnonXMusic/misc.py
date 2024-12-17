import os
import asyncio
from .logging import LOGGER
from pyrogram import filters
from . import config  # config ko import kiya hai
def is_heroku():
    return os.environ.get("DYNO", None) is not None
def dbb():
    global db
    db = {}
    LOGGER(__name__).info(f"Local Database Initialized.")
SUDOERS = filters.user()  
async def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
def heroku():
    global HAPP
    if is_heroku:
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = Heroku.app(config.HEROKU_APP_NAME)
            except BaseException:
                LOGGER(__name__).warning(
                    f"Please make sure your Heroku API Key and Your App name are configured correctly in the heroku."
                )
async def main():
    dbb()
    await sudo()
    heroku()
asyncio.run(main())
