from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.video import Video
from app.db.models.transcript import TranscriptChunk
from app.ingestion.youtube import extract_video_id, canonical_url
from app.ingestion.metadata import fetch_metadata
from app.ingestion.transcript import fetch_transcript
from app.ingestion.cleaning import clean_transcript
from app.ingestion.chunking import create_chunks
from app.ingestion.embeddings import embed_texts

def ingest_video(db: Session, submitted_url: str) -> tuple[Video, bool]:
    """Return (video, reused_existing). Existing completed ingestion is reused."""
    video_id = extract_video_id(submitted_url)
    existing = db.scalar(select(Video).where(Video.youtube_id == video_id))
    if existing and existing.ingestion_status == "completed":
        return existing, True

    video = existing
    if video is None:
        video = Video(youtube_id=video_id, url=canonical_url(video_id), title="Processing", ingestion_status="processing")
        db.add(video)
        db.commit()
        db.refresh(video)
    else:
        video.ingestion_status = "processing"
        video.ingestion_error = None
        db.query(TranscriptChunk).filter(TranscriptChunk.video_id == video.id).delete()
        db.commit()

    try:
        metadata = fetch_metadata(video.url)
        raw_transcript = fetch_transcript(video_id)
        cleaned = clean_transcript(raw_transcript)
        chunks = create_chunks(cleaned, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            raise ValueError("Transcript did not produce any chunks.")
        vectors = embed_texts([chunk["text"] for chunk in chunks])

        video.title = metadata["title"]
        video.channel_name = metadata["channel_name"]
        video.duration_seconds = metadata["duration_seconds"]
        video.url = canonical_url(video_id)
        db.add_all([
            TranscriptChunk(
                video_id=video.id,
                chunk_index=i,
                text=chunk["text"],
                start_seconds=chunk["start_seconds"],
                end_seconds=chunk["end_seconds"],
                embedding=vectors[i],
            )
            for i, chunk in enumerate(chunks)
        ])
        video.ingestion_status = "completed"
        video.ingestion_error = None
        db.commit()
        db.refresh(video)
        return video, False
    except Exception as exc:
        db.rollback()
        # Re-fetch row after rollback so failure status can be committed.
        failed_video = db.scalar(select(Video).where(Video.youtube_id == video_id))
        if failed_video:
            failed_video.ingestion_status = "failed"
            failed_video.ingestion_error = str(exc)[:2000]
            db.commit()
        raise
