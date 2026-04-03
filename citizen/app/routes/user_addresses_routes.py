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
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    address: str
    landmark: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

    is_default: Optional[bool] = False


class UserAddressUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    address: Optional[str] = None
    landmark: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

    is_default: Optional[bool] = None

# CREATE



# CREATE
@router.post("/create")
async def create_address(payload: UserAddressCreate):
    address = UserAddress(**payload.model_dump())
    return await create_user_address(address)


# LIST
@router.get("/list/{user_id}")
async def list_addresses(user_id: str):
    return {"addresses": await get_all_addresses(user_id)}

    
# GET BY ID
@router.get("/{id}")
async def get_address(id: str):
    address = await get_address_by_id(id)
    if not address:
        raise HTTPException(404, "Address not found")
    return address


# UPDATE
@router.put("/update/{id}")
async def update_address(id: str, payload: UserAddressUpdate):
    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(400, "No fields to update")

    updated = await update_user_address(id, updates)

    if not updated:
        raise HTTPException(404, "Address not found")

    return {"status": "success", "data": updated}


# DELETE
@router.delete("/delete/{id}")
async def delete_address(id: str):
    result = await delete_user_address(id)

    if not result:
        raise HTTPException(404, "Address not found")

    return {"status": "success", "deleted_id": id}