from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domain.user_address_domain import UserAddress
from app.services.user_address_service import (
    create_user_address,
    get_all_addresses,
    get_address_by_id,
    update_user_address,
    delete_user_address
)

router = APIRouter()

# Pydantic models
class UserAddressCreate(BaseModel):
    user_id: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None

class UserAddressUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None

# CREATE
@router.post("/create")
async def create_address(payload: UserAddressCreate, session: AsyncSession = Depends(get_session)):
    address = UserAddress(**payload.model_dump())
    return await create_user_address(address, session)

# LIST
@router.get("/list/{user_id}")
async def list_addresses(user_id: str, session: AsyncSession = Depends(get_session)):
    addresses = await get_all_addresses(user_id, session)
    return {"addresses": addresses}

# GET BY ID
@router.get("/{id}")
async def get_address(id: str, session: AsyncSession = Depends(get_session)):
    address = await get_address_by_id(id, session)
    if not address:
        raise HTTPException(404, "Address not found")
    return address

# UPDATE
@router.put("/{id}")
async def update_address(id: str, payload: UserAddressUpdate, session: AsyncSession = Depends(get_session)):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No fields to update")
    updated = await update_user_address(id, updates, session)
    if not updated:
        raise HTTPException(404, "Address not found")
    return {"status": "success", "data": updated}

# DELETE
@router.delete("/{id}")
async def delete_address(id: str, session: AsyncSession = Depends(get_session)):
    result = await delete_user_address(id, session)
    if not result:
        raise HTTPException(404, "Address not found")
    return {"status": "success", "deleted_id": id}