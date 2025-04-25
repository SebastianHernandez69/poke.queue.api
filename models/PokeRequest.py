from pydantic import BaseModel, Field
from typing import Optional

class PokeRequest(BaseModel):

    id: Optional[int] = Field(
        default=None,
        ge=1,
        description="The ID of the requested Pokémon"
    )

    pokemon_type: Optional[str] = Field(
        default=None,
        description="The type of the requested Pokémon",
        pattern="^[a-zA-Z0-9_]+$"
    )

    url: Optional[str] = Field(
        default=None,
        description="The URL of the requested",
        pattern="^https?://[^\s]+$"
    )
    
    status: Optional[str] = Field(
        default=None,
        description="The status of the requested",
        pattern="^(sent|completed|inprogress|failed)$"
    )