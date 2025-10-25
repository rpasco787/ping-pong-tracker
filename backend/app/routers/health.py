from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/healthz")
def healthz():
    return {"ok": True, "service": "pingpong-api"}
