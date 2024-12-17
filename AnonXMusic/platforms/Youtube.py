import asyncio
import os
import yt_dlp
from typing import Union

async def download(
    self,
    link: str,
    mystic,
    video: Union[bool, str] = None,
    videoid: Union[bool, str] = None,
    songaudio: Union[bool, str] = None,
    songvideo: Union[bool, str] = None,
    format_id: Union[bool, str] = None,
    title: Union[bool, str] = None,
    cookies_file: str = "cookies.txt"  # Add cookies file path parameter
) -> str:
    if videoid:
        link = self.base + link
    loop = asyncio.get_running_loop()

    def audio_dl():
        ydl_optssx = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookies": cookies_file  # Use cookies file
        }
        x = yt_dlp.YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

    def video_dl():
        ydl_optssx = {
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookies": cookies_file  # Use cookies file
        }
        x = yt_dlp.YoutubeDL(ydl_optssx)
        info = x.extract_info(link, False)
        xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
        if os.path.exists(xyz):
            return xyz
        x.download([link])
        return xyz

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
            "cookies": cookies_file  # Use cookies file
        }
        x = yt_dlp.YoutubeDL(ydl_optssx)
        x.download([link])

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
            "cookies": cookies_file  # Use cookies file
        }
        x = yt_dlp.YoutubeDL(ydl_optssx)
        x.download([link])

    if songvideo:
        await loop.run_in_executor(None, song_video_dl)
        fpath = f"downloads/{title}.mp4"
        return fpath
    elif songaudio:
        await loop.run_in_executor(None, song_audio_dl)
        fpath = f"downloads/{title}.mp3"
        return fpath
    elif video:
        if await is_on_off(1):
            direct = True
            downloaded_file = await loop.run_in_executor(None, video_dl)
        else:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "-g",
                "-f",
                "best[height<=?720][width<=?1280]",
                f"{link}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, 'YTDL_COOKIES': cookies_file}  # Pass cookies if needed
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                downloaded_file = stdout.decode().split("\n")[0]
                direct = None
            else:
                return
    else:
        direct = True
        downloaded_file = await loop.run_in_executor(None, audio_dl)
    return downloaded_file, direct
        
