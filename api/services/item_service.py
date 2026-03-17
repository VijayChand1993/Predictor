"""
Item service for business logic related to items.
"""
from typing import Optional, List, Dict


class ItemService:
    """Service class for handling item-related business logic."""
    
    def __init__(self):
        # In-memory storage for demo purposes
        self.items: Dict[int, dict] = {}
        self.next_id = 1
    
    def create_item(self, name: str, description: Optional[str], price: float, tax: Optional[float]) -> dict:
        """
        Create a new item.
        
        Args:
            name: Item name
            description: Item description
            price: Item price
            tax: Item tax
            
        Returns:
            Created item with calculated total price
        """
        total_price = price + (tax if tax else 0)
        item = {
            "id": self.next_id,
            "name": name,
            "description": description,
            "price": price,
            "tax": tax,
            "total_price": total_price
        }
        self.items[self.next_id] = item
        self.next_id += 1
        return item
    
    def get_item(self, item_id: int) -> Optional[dict]:
        """
        Get an item by ID.
        
        Args:
            item_id: The item ID
            
        Returns:
            Item if found, None otherwise
        """
        return self.items.get(item_id)
    
    def get_all_items(self) -> List[dict]:
        """
        Get all items.
        
        Returns:
            List of all items
        """
        return list(self.items.values())
    
    def update_item(self, item_id: int, name: Optional[str] = None, 
                   description: Optional[str] = None, price: Optional[float] = None,
                   tax: Optional[float] = None) -> Optional[dict]:
        """
        Update an existing item.
        
        Args:
            item_id: The item ID
            name: New name (optional)
            description: New description (optional)
            price: New price (optional)
            tax: New tax (optional)
            
        Returns:
            Updated item if found, None otherwise
        """
        item = self.items.get(item_id)
        if not item:
            return None
        
        if name is not None:
            item["name"] = name
        if description is not None:
            item["description"] = description
        if price is not None:
            item["price"] = price
        if tax is not None:
            item["tax"] = tax
        
        # Recalculate total price
        item["total_price"] = item["price"] + (item["tax"] if item["tax"] else 0)
        
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """
        Delete an item.
        
        Args:
            item_id: The item ID
            
        Returns:
            True if deleted, False if not found
        """
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False


# Singleton instance
item_service = ItemService()

