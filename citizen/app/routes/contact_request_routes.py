from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.contact_request_domain import ContactRequest
from app.services.contact_request_service import (
    create_contact_request,
    get_all_contact_requests,
    get_contact_request_by_id,
    update_contact_request,
    delete_contact_request
)

router = APIRouter()

# -------------------------
# ENUM VALIDATION
# -------------------------
ALLOWED_STATUS = {"new", "in_progress", "resolved"}


# -------------------------
# CREATE SCHEMA
# -------------------------
class ContactRequestCreate(BaseModel):
    full_name: str
    phone_number: str
    email_address: str
    subject: str
    message: str
    status: str = "new"


# -------------------------
# UPDATE SCHEMA
# -------------------------
class ContactRequestUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None


# -------------------------
# CREATE CONTACT
# -------------------------
@router.post("/create")
async def create_contact_request_endpoint(payload: ContactRequestCreate):

    if payload.status not in ALLOWED_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {ALLOWED_STATUS}"
        )

    contact = ContactRequest(**payload.model_dump())

    data = await create_contact_request(contact)

    return {
        "status": "success",
        "data": data
    }


# -------------------------
# GET ALL CONTACTS
# -------------------------
@router.get("/list")
async def list_contact_requests():

    data = await get_all_contact_requests()

    return {
        "status": "success",
        "data": data
    }


# -------------------------
# GET BY ID
# -------------------------
@router.get("/{id}")
async def get_contact_request_endpoint(id: str):

    data = await get_contact_request_by_id(id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Contact request not found"
        )

    return {
        "status": "success",
        "data": data
    }


# -------------------------
# UPDATE CONTACT (INCLUDING STATUS)
# -------------------------
@router.put("/{id}")
async def update_contact_request_endpoint(
    id: str,
    payload: ContactRequestUpdate
):

    updates = payload.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )

    # validate status if present
    if "status" in updates and updates["status"] not in ALLOWED_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {ALLOWED_STATUS}"
        )

    data = await update_contact_request(id, updates)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Contact request not found"
        )

    return {
        "status": "success",
        "data": data
    }


# -------------------------
# DELETE CONTACT
# -------------------------
@router.delete("/{id}")
async def delete_contact_request_endpoint(id: str):

    result = await delete_contact_request(id)

    if not result:
        raise HTTPException(    
            status_code=404,
            detail="Contact request not found"
        )

    return {
        "status": "success",
        "deleted_id": id
    }