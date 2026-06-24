import asyncio
import yt_dlp
from pathlib import Path
from app.services.progress_manager import progress_manager

class YouTubeDownloader:
    """
    Service Layer wrapping yt-dlp.
    Handles streaming download hooks and manages temp files.
    """
    def __init__(self, task_id: str, workspace_path: Path):
        self.task_id = task_id
        self.workspace_path = workspace_path

    async def download_stream(self, url: str, format_selection: str, quality: str = None) -> Path:
        loop = asyncio.get_event_loop()

        if format_selection == "mp3":
            ydl_format = "bestaudio/best"
        else:
            height_limit_map = {
                "240p": 240,
                "360p": 360,
                "480p": 480,
                "720p": 720,
                "1080p": 1080
            }

            height_limit = height_limit_map.get(quality, 720)

            # Use already-merged formats when possible
            ydl_format = f"best[height<={height_limit}]/best"

        outtmpl = str(self.workspace_path / "%(title)s.%(ext)s")

        ydl_opts = {
            "format": ydl_format,
            "outtmpl": outtmpl,
            
            # Render Secret File
            "cookiefile": "/etc/secrets/cookies.txt",
            
            "ffmpeg_location": "ffmpeg",
            "progress_hooks": [self._yt_dlp_progress_hook],
            
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "windowsfilenames": True,
            
            "noplaylist": True,
            "retries": 10,
            "fragment_retries": 10
        }

        def run_downloader():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info is None:
                    raise RuntimeError("yt-dlp returned no media information.")
                    
                filename = ydl.prepare_filename(info)
                return Path(filename)

        return await loop.run_in_executor(None, run_downloader)

    def _yt_dlp_progress_hook(self, d: dict):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)

            if total_bytes > 0:
                pct = int((downloaded / total_bytes) * 100)
                normalized_pct = int(10 + (pct * 0.6))
                
                progress_manager.set_progress(
                    self.task_id,
                    normalized_pct,
                    "Sucking ones and zeros from the internet..."
                )
            else:
                progress_manager.set_progress(
                    self.task_id,
                    35,
                    "Downloading media payload streams..."
                )

        elif d["status"] == "finished":
            progress_manager.set_progress(
                self.task_id,
                70,
                "Acquisition pipeline resolved. Preparing transcoding headers..."
            )