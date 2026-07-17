from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VenueItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address: str


class GetVenuesResponse(BaseModel):
    venues: list[VenueItemResponse]


class PlayerUrlResponse(BaseModel):
    url: str
