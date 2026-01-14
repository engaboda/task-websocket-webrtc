from datetime import datetime

from pydantic import BaseModel


class ProductResponseListSerializer(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        from_attributes = True


class HighestBidPriceSerializer(BaseModel):
    highest_bid: int

    class Config:
        from_attributes = True


class BidInformationSerializer(BaseModel):
    id: int
    product_id: int
    username: str
    amount: int
    placed_at: datetime

    class Config:
        from_attributes = True


class CreateBidSerializer(BaseModel):
    username: str
    price: int


class CreateRoomSerializer(BaseModel):
    username: str


JoinRoomSerializer = CreateRoomSerializer


class RoomInformation(BaseModel):
    id: int
    room_name: str
