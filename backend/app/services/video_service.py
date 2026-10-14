from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models.video import Video
from app.db.models.transcript import TranscriptChunk
from app.ingestion.pipeline import ingest_video
from app.ingestion.youtube import extract_video_id

def get_video_status(db: Session, submitted_url: str) -> dict:
    video_id = extract_video_id(submitted_url)
    video = db.scalar(select(Video).where(Video.youtube_id == video_id))
    if not video:
        return {"youtube_id": video_id, "ingestion_status": "not_found"}
    chunk_count = db.scalar(
        select(__import__("sqlalchemy").func.count(TranscriptChunk.id))
        .where(TranscriptChunk.video_id == video.id)
    )
    return {
        "id": video.id,
        "youtube_id": video.youtube_id,
        "title": video.title,
        "channel_name": video.channel_name,
        "duration_seconds": video.duration_seconds,
        "ingestion_status": video.ingestion_status,
        "ingestion_error": video.ingestion_error,
        "chunk_count": chunk_count or 0,
    }

def submit_video(db: Session, url: str) -> tuple[Video, bool]:
    return ingest_video(db, url)
