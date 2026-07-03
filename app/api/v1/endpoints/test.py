from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/test", tags=["Test"])


@router.get("/supabase")
def test_supabase():
    return {
        "url": settings.SUPABASE_URL is not None,
        "key": settings.SUPABASE_SERVICE_ROLE_KEY is not None,
        "profiles_bucket": settings.SUPABASE_BUCKET_PROFILES
    }