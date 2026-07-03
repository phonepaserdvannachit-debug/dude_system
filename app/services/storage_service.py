import uuid
from app.core.supabase import supabase


def upload_file(file, bucket: str) -> str:
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"

    file_bytes = file.file.read()

    # IMPORTANT FIX: wrap bytes correctly
    supabase.storage.from_(bucket).upload(
        path=filename,
        file=file_bytes,
        file_options={
            "content-type": file.content_type,
            "upsert": "true"
        }
    )

    return supabase.storage.from_(bucket).get_public_url(filename)