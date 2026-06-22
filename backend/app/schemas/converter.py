from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal

class ConversionRequest(BaseModel):
    """
    Strict Pydantic payload validator protecting server entryways
    against malicious, malformed, or corrupt client requests.
    """

    url: str = Field(
        ...,
        description="The target video or streaming URL to resolve and transcode",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    )

    format: Literal["mp3", "mp4"] = Field(
        ...,
        description="Target wrapper format container"
    )

    quality: Optional[Literal["240p", "360p", "480p", "720p", "1080p"]] = Field(
        default=None,
        description="Target resolution height constraints, mandatory if MP4 is specified"
    )

    audio_quality: Optional[Literal["128k", "192k", "256k", "320k"]] = Field(
        default="320k",
        description="Target MP3 bitrate in kbps (e.g., '128k', '192k', '256k', '320k')"
    )

    @model_validator(mode="after")
    def validate_format_parameters(self) -> 'ConversionRequest':
        """
        Ensures format-specific quality parameters are present.
        """
        if self.format == "mp4" and not self.quality:
            raise ValueError("Resolution height parameter ('quality') is mandatory if MP4 format is selected.")
        if self.format == "mp3" and not self.audio_quality:
            raise ValueError("Audio bitrate parameter ('audio_quality') is mandatory if MP3 format is selected.")
        return self