import asyncio
import os
import re
from typing import Union, List, Dict
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic.utils.database import is_on_off
from AnonXMusic.utils.formatters import time_to_seconds

cookies_file = os.environ.get("COOKIES_FILE", "AnonXMusic/assets/cookies.txt")

async def execute_shell_command(cmd: str) -> str:
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, errorz = await proc.communicate()
        error_msg = errorz.decode("utf-8") if errorz else None
        if error_msg and "unavailable videos are hidden" not in error_msg.lower():
            return error_msg
        return out.decode("utf-8")
    except Exception as e:
        return f"Error: {e}"

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def _get_video_details(self, link: str):
        """Generic function to get various details about the video."""
        results = VideosSearch(link, limit=1)
        video_info = await results.next()
        if video_info.get("result"):
            return video_info["result"][0]
        return None

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        """Check if the link is a valid YouTube video link."""
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        """Extract URL from the message or its reply."""
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        return message.text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None) -> Dict[str, Union[str, int]]:
        """Fetch video details like title, duration, and thumbnail."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        video = await self._get_video_details(link)
        if video:
            title = video.get("title")
            duration_min = video.get("duration", 0)
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            thumbnail = video["thumbnails"][0]["url"].split("?")[0]
            vidid = video["id"]
            return {"title": title, "duration_min": duration_min, "duration_sec": duration_sec, "thumbnail": thumbnail, "vidid": vidid}
        return {}

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        """Fetch the title of the video."""
        details = await self.details(link, videoid)
        return details.get("title", "")

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> str:
        """Fetch the duration of the video."""
        details = await self.details(link, videoid)
        return details.get("duration_min", "")

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        """Fetch the thumbnail URL of the video."""
        details = await self.details(link, videoid)
        return details.get("thumbnail", "")

    async def video(self, link: str, videoid: Union[bool, str] = None) -> Union[int, str]:
        """Fetch the video URL."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookies_file,
            "-g", "-f", "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, stderr.decode())

    async def playlist(self, link: str, limit: int, user_id: str, videoid: Union[bool, str] = None) -> List[str]:
        """Fetch a playlist from YouTube."""
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await execute_shell_command(
            f"yt-dlp --cookies {cookies_file} -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        return [item for item in playlist.split("\n") if item]

    async def formats(self, link: str, videoid: Union[bool, str] = None) -> List[Dict[str, str]]:
        """Fetch available formats for the video."""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        ydl_opts = {"quiet": True, "cookiefile": cookies_file}
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        formats_available = []

        try:
            r = ydl.extract_info(link, download=False)
            for format in r.get("formats", []):
                if not "dash" in str(format.get("format", "")).lower():
                    formats_available.append({
                        "format": format["format"],
                        "filesize": format.get("filesize"),
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format.get("format_note"),
                        "yturl": link,
                    })
        except Exception as e:
            return f"Error fetching formats: {e}"

        return formats_available

    async def download(self, link: str, mystic, video: Union[bool, str] = None, songaudio: Union[bool, str] = None,
                       songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
        """Download the video/audio based on specified options."""
        loop = asyncio.get_running_loop()

        def download_audio():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"downloads/{title}.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookies_file,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                file_path = f"downloads/{info['id']}.{info['ext']}"
                if not os.path.exists(file_path):
                    ydl.download([link])
                return file_path

        async def download(self, link: str, mystic, video: Union[bool, str] = None, songaudio: Union[bool, str] = None,
                   songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
    #"""Download the video/audio based on specified options."""
    loop = asyncio.get_running_loop()

    def download_audio():
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"downloads/{title}.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": cookies_file,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            file_path = f"downloads/{info['id']}.{info['ext']}"
            if not os.path.exists(file_path):
                ydl.download([link])
            return file_path

    def download_video():
        ydl_opts = {
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
            "outtmpl": f"downloads/{title}.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": cookies_file,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            file_path = f"downloads/{info['id']}.{info['ext']}"
            if not os.path.exists(file_path):
                ydl.download([link])
            return file_path

    def song_video_dl():
        formats = f"{format_id}+140"
        fpath = f"downloads/{title}"
        ydl_optssx = {
            "format": formats,
            "outtmpl": fpath,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "prefer_ffmpeg": True,
            "merge_output_format": "mp4",
            "cookiefile": cookies_file,
        }
        with yt_dlp.YoutubeDL(ydl_optssx) as ydl:
            ydl.download([link])

    def song_audio_dl():
        fpath = f"downloads/{title}.%(ext)s"
        ydl_optssx = {
            "format": format_id,
            "outtmpl": fpath,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "prefer_ffmpeg": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "cookiefile": cookies_file,
        }
        with yt_dlp.YoutubeDL(ydl_optssx) as ydl:
            ydl.download([link])

    # Determine which download function to run
    if songvideo:
        await loop.run_in_executor(None, song_video_dl)
        fpath = f"downloads/{title}.mp4"
        return fpath
    elif songaudio:
        await loop.run_in_executor(None, song_audio_dl)
        fpath = f"downloads/{title}.mp3"
        return fpath
    elif video:
        # Check if a direct video download is allowed
        if await is_on_off(1):
            return await loop.run_in_executor(None, download_video)
        else:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--cookies", cookies_file,
                "-g", "-f", "best[height<=?720][width<=?1280]",
                f"{link}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                downloaded_file = stdout.decode().split("\n")[0]
                return downloaded_file
            else:
                return stderr.decode()
    else:
        return await loop.run_in_executor(None, download_audio)
                                        
