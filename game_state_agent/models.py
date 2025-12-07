"""Pydantic models for game state and LLM structured outputs."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UpdateType(str, Enum):
    """Type of game state update detected."""
    NOOP = "noop"
    LOCATION = "location"
    INVENTORY = "inventory"
    BOTH = "both"


class InventoryItem(BaseModel):
    """An item in the player's inventory."""
    name: str = Field(description="Name of the item")
    quantity: int = Field(default=1, description="Quantity of the item")


class StateUpdate(BaseModel):
    """Structured output from the LLM analyzing a screenshot.
    
    This model is used with OpenAI's structured outputs to ensure
    consistent parsing of the LLM's analysis.
    """
    update_type: UpdateType = Field(
        description="Type of update detected. Use 'noop' if no relevant game state information is visible."
    )
    new_location: Optional[str] = Field(
        default=None,
        description="The player's current location/area name if visible (e.g., 'Limgrave', 'Stormveil Castle', 'Roundtable Hold'). Only set if update_type is 'location' or 'both'."
    )
    inventory_items: Optional[list[InventoryItem]] = Field(
        default=None,
        description="List of items visible in the inventory screen. Only set if update_type is 'inventory' or 'both' and an inventory/equipment screen is clearly visible."
    )
    reasoning: str = Field(
        description="Brief explanation of what was detected in the screenshot and why this update type was chosen."
    )


class GameState(BaseModel):
    """Current state of the game being tracked."""
    player_location: str = Field(
        default="Unknown",
        description="Current area/region the player is in"
    )
    inventory: list[InventoryItem] = Field(
        default_factory=list,
        description="Items in the player's inventory"
    )
    
    def apply_update(self, update: StateUpdate) -> bool:
        """Apply a state update and return True if state changed."""
        if update.update_type == UpdateType.NOOP:
            return False
        
        changed = False
        
        if update.update_type in (UpdateType.LOCATION, UpdateType.BOTH):
            if update.new_location and update.new_location != self.player_location:
                self.player_location = update.new_location
                changed = True
        
        if update.update_type in (UpdateType.INVENTORY, UpdateType.BOTH):
            if update.inventory_items is not None:
                self.inventory = update.inventory_items
                changed = True
        
        return changed

