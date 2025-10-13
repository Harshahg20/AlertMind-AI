from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime

from app.api.alerts import MOCK_CLIENTS
from app.services.patch_management import PatchManagementService

router = APIRouter()

svc = PatchManagementService()


@router.get("/advisories")
async def get_patch_advisories(client_id: str) -> Dict:
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return svc.get_advisories(client)


@router.post("/plan")
async def plan_patch_window(client_id: str, advisories: Dict) -> Dict:
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    items = advisories.get("advisories", [])
    return svc.plan_maintenance(client, items)


@router.get("/simulate-blast")
async def simulate_blast(client_id: str, product: str) -> Dict:
    client = next((c for c in MOCK_CLIENTS if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return svc.simulate_blast_radius(client, product)


