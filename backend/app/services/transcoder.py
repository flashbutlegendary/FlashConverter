import asyncio
import subprocess
from pathlib import Path
from app.services.progress_manager import progress_manager

class FFmpegTranscoder:
    """
    FFmpeg Transcoding Service
    Uses subprocess.run() for maximum compatibility.
    Works both locally and on Render.
    """

    def __init__(self, task_id: str, workspace_path: Path):
        self.task_id = task_id
        self.workspace_path = workspace_path

    async def transcode(
        self,
        input_file: Path,
        target_format: str,
        quality: str = None,
        audio_quality: str = "320k"
    ) -> Path:
        output_name = f"{input_file.stem} - FlashConverter.{target_format}"
        output_path = self.workspace_path / output_name

        if target_format == "mp3":
            bitrate_map = {
                "128k": "128k",
                "192k": "192k",
                "256k": "256k",
                "320k": "320k"
            }

            selected_bitrate = bitrate_map.get(audio_quality, "320k")
            print(f"Selected bitrate: {selected_bitrate}")

            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_file),
                "-vn",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-b:a",
                selected_bitrate,
                str(output_path)
            ]
        else:
            quality_map = {
                "240p": 240,
                "360p": 360,
                "480p": 480,
                "720p": 720,
                "1080p": 1080
            }

            scale_height = quality_map.get(quality, 720)

            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_file),
                "-vf",
                f"scale=-2:{scale_height}",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                str(output_path)
            ]

        progress_manager.set_progress(
            self.task_id,
            80,
            "Converting caffeine into results..."
        )

        try:
            def run_ffmpeg():
                return subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )

            result = await asyncio.to_thread(run_ffmpeg)

            if result.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg pipeline failure:\n{result.stderr}"
                )

            if not output_path.exists():
                raise RuntimeError(
                    "FFmpeg completed but output file was not generated."
                )

            progress_manager.set_progress(
                self.task_id,
                95,
                "Tidying up digital workspace files..."
            )

            return output_path

        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg executable not found. "
                "Verify FFmpeg is installed and available in PATH."
            )