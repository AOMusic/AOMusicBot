from AnonXMusic.core.bot import Anony
from AnonXMusic.core.dir import dirr
from AnonXMusic.core.git import git
from AnonXMusic.core.userbot import Userbot
from AnonXMusic.misc import dbb, heroku
from .logging import LOGGER

#Initializing Directories
dirr()

#Initializing Database
dbb()

#Initializing Heroku
heroku()

#Initializing Bot and Userbot
app = Anony()
userbot = Userbot()

#Importing Platforms
from .platforms import *

#Initializing Platforms
Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
