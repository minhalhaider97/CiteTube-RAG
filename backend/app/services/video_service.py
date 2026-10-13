from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Video


def get_or_create_video(
    db: Session,
    youtube_video_id: str,
    canonical_url: str,
    title: str,
    channel_name: str | None = None,
    duration_seconds: int | None = None,
) -> tuple[Video, bool]:
    """
    Returns:
        (video, created)

    created=True means a new video record was inserted.
    created=False means the video already existed.
    """

    video = db.scalar(
        select(Video).where(
            Video.youtube_video_id == youtube_video_id
        )
    )

    if video is not None:
        return video, False

    video = Video(
        youtube_video_id=youtube_video_id,
        canonical_url=canonical_url,
        title=title,
        channel_name=channel_name,
        duration_seconds=duration_seconds,
        status="pending",
    )

    db.add(video)
    db.commit()
    db.refresh(video)

    return video, True


def mark_video_completed(db: Session, video: Video) -> None:
    video.status = "completed"
    video.processed_at = datetime.now(timezone.utc)
    video.error_message = None

    db.commit()
    db.refresh(video)


def mark_video_failed(
    db: Session,
    video: Video,
    error_message: str,
) -> None:
    video.status = "failed"
    video.error_message = error_message

    db.commit()
    db.refresh(video)