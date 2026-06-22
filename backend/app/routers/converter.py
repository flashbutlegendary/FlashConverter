from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse, JSONResponse
import uuid
import traceback

from app.schemas.converter import ConversionRequest
from app.services.downloader import YouTubeDownloader
from app.services.transcoder import FFmpegTranscoder
from app.services.progress_manager import progress_manager
from app.utilities.file_system import create_task_workspace, remove_task_workspace

router = APIRouter(
    prefix="/converter",
    tags=["Media Conversion Control Core"]
)


@router.post("/convert", status_code=status.HTTP_200_OK)
async def execute_conversion_pipeline(
    request: ConversionRequest,
    background_tasks: BackgroundTasks
):

    task_id = str(uuid.uuid4())

    progress_manager.set_progress(
        task_id,
        0,
        "Initializing pipeline workspaces..."
    )

    if request.format == "mp4" and not request.quality:
        progress_manager.set_progress(
            task_id,
            100,
            "Failed: Quality config missing"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolution parameter ('quality') is mandatory for MP4 exports."
        )

    workspace_path = create_task_workspace(task_id)

    try:

        progress_manager.set_progress(
            task_id,
            10,
            "Negotiating with video server..."
        )

        downloader = YouTubeDownloader(
            task_id,
            workspace_path
        )

        downloaded_file = await downloader.download_stream(
            request.url,
            request.format,
            request.quality
        )

        if not downloaded_file.exists():
            raise FileNotFoundError(
                "Downloaded source file could not be located."
            )

        progress_manager.set_progress(
            task_id,
            75,
            "Untangling audio/video spaghetti..."
        )

        transcoder = FFmpegTranscoder(
            task_id,
            workspace_path
        )

        final_output_file = await transcoder.transcode(
            input_file=downloaded_file,
            target_format=request.format,
            quality=request.quality,
            audio_quality=request.audio_quality
        )

        if not final_output_file.exists():
            raise FileNotFoundError(
                "Transcoder output file verification failed."
            )

        progress_manager.set_progress(
            task_id,
            100,
            "Conversion completed successfully."
        )

        background_tasks.add_task(
            remove_task_workspace,
            workspace_path
        )

        media_type = (
            "audio/mpeg"
            if request.format == "mp3"
            else "video/mp4"
        )

        return FileResponse(
            path=final_output_file,
            media_type=media_type,
            filename=final_output_file.name
        )

    except Exception as e:

        background_tasks.add_task(
            remove_task_workspace,
            workspace_path
        )

        progress_manager.set_progress(
            task_id,
            100,
            f"Critical failure: {repr(e)}"
        )

        print("\n==============================")
        print("[CRITICAL TASK FAILURE]")
        print(f"Task ID: {task_id}")
        print(traceback.format_exc())
        print("==============================\n")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Conversion failed.",
                "detail": repr(e),
                "suggestion": "Verify the URL and try again."
            }
        )


@router.get("/status/{task_id}", status_code=status.HTTP_200_OK)
async def get_pipeline_progress(task_id: str):

    task_state = progress_manager.get_progress(task_id)

    if not task_state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found."
        )

    return task_state