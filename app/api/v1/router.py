from fastapi import APIRouter

from app.api.v1.endpoints import auth, bill, health, payment, slip
from app.api.v1.endpoints import dashboard
from app.api.v1.endpoints import upload
from app.api.v1.endpoints import test
from app.api.v1.endpoints import contract
from app.api.v1.endpoints import catalog

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(bill.router)
api_router.include_router(payment.router)
api_router.include_router(slip.router)
api_router.include_router(dashboard.router)
api_router.include_router(upload.router)
api_router.include_router(contract.router)
api_router.include_router(catalog.router)
api_router.include_router(test.router)
