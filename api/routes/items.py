"""
Item routes for the API.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

from api.services.item_service import item_service

router = APIRouter(
    prefix="/items",
    tags=["items"]
)


class ItemCreate(BaseModel):
    """Schema for creating an item."""
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None


class ItemResponse(BaseModel):
    """Schema for item response."""
    id: int
    name: str
    description: Optional[str]
    price: float
    tax: Optional[float]
    total_price: float


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item."""
    created_item = item_service.create_item(
        name=item.name,
        description=item.description,
        price=item.price,
        tax=item.tax
    )
    return created_item


@router.get("/", response_model=List[ItemResponse])
async def get_all_items():
    """Get all items."""
    items = item_service.get_all_items()
    return items


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get an item by ID."""
    item = item_service.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update an item."""
    updated_item = item_service.update_item(
        item_id=item_id,
        name=item_update.name,
        description=item_update.description,
        price=item_update.price,
        tax=item_update.tax
    )
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete an item."""
    deleted = item_service.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return None

