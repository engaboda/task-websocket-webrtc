import asyncio
import json
import logging
from typing import List
from fastapi import APIRouter, HTTPException

import redis.asyncio as aioredis

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.endpoints import WebSocketEndpoint

from src.config import settings
from src.db.engine import RwajSession
from src.db.models import Product, Bids, User, Room
from src.serializers import (
    ProductResponseListSerializer, HighestBidPriceSerializer, CreateBidSerializer,
    BidInformationSerializer, CreateRoomSerializer, RoomInformation, JoinRoomSerializer
)
from src.utils import publish_to_channel, create_livekit_room, create_livekit_read_only_viewer

logger = logging.getLogger(__name__)
rwaj_routers = APIRouter(prefix=settings.fastapi.MAIN_PREFIX)


@rwaj_routers.get('/health')
def health():
    return {"status": "ok"}


@rwaj_routers.get('/products', status_code=200, response_model=List[ProductResponseListSerializer])
async def products_list():
    async with RwajSession() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return products


@rwaj_routers.post('/products/{product_id}/new-bid', status_code=201, response_model=BidInformationSerializer)
async def new_bid(product_id: int, data: CreateBidSerializer):
    """
        Field with a user to input their name
        Button for a user to submit a new bid
    """
    async with RwajSession() as session:
        products = await session.execute(
            select(
                Product
            ).where(
                Product.id == product_id
            )
        )
        product = products.scalar()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        users = await session.execute(
            select(
                User
            ).where(
                User.username == data.username
            )
        )
        user = users.scalar()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        bid = Bids(
            **{
                "product_id": product_id,
                "user_id": user.id,
                "amount": data.price,
            }
        )
        session.add(bid)
        await session.commit()
        await session.refresh(bid)
        await publish_to_channel(f"New Bid add by user: {data.username}", product_id)

        return {
            "id": bid.id,
            'product_id': product_id,
            'username': data.username,
            'amount': data.price,
            "placed_at": bid.placed_at,
        }


@rwaj_routers.get('/products/{product_id}/bids', status_code=201, response_model=List[BidInformationSerializer])
async def bids(product_id: int):
    """
        Display a list of historical bids, showing who placed the bid and how much it was for
    """
    async with RwajSession() as session:
        result = await session.execute(
            select(Bids)
            .options(selectinload(Bids.user))
            .where(Bids.product_id == product_id)
            .distinct()
        )
        bids = result.scalars().all()

        if not bids:
            raise HTTPException(status_code=404, detail="No bids found for this product")

        return [
            {
                "id": bid.id,
                'product_id': product_id,
                'username': bid.user.username,
                'amount': bid.amount,
                "placed_at": bid.placed_at,
            }
            for bid in bids
        ]


@rwaj_routers.get('/products/{product_id}/highest-bids', status_code=200, response_model=HighestBidPriceSerializer)
async def highest_bids(product_id: int):
    """
        Display the current highest bidding price
    """
    async with RwajSession() as session:
        result = await session.execute(
            select(
                func.max(
                    Bids.amount
                )
            ).where(
                Bids.product_id == product_id
            )
        )
        highest_bid = result.scalar()  # scalar() returns the single value

        if highest_bid is None:
            highest_bid = None  # No bids exist for this product

        return {"highest_bid": highest_bid}


class NotificationEndpoint(WebSocketEndpoint):
    encoding = 'text'

    async def on_connect(self, websocket):
        self.product_id = int(websocket.path_params["product_id"])
        async with RwajSession() as session:
            result = await session.execute(
                select(
                    Product
                ).where(
                    Product.id == self.product_id
                )
            )
            self.product = result.scalar()

        if not self.product:
            logger.error(f'product_id: {self.product_id} not found while connecting to notification channel.')
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()

        # Connect to Redis
        self.redis = aioredis.from_url(settings.redis.url)
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe(f"product_bids_notifications:{self.product_id}")

        # Background listener for messages
        asyncio.create_task(self.listen_for_notifications(websocket))

    async def listen_for_notifications(self, websocket):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    await websocket.send_json(json.loads(data))
        except Exception as e:
            logger.error(f'error: {e} while listening for notifications')
        finally:
            logger.info("✅ Redis pubsub listener stopped.")

    async def on_receive(self, websocket, data):
        await websocket.send_text(f"{data}")

    async def on_disconnect(self, websocket, close_code):
        try:
            logger.info(f'disconnect code: {close_code} from websocket.')
            await self.pubsub.unsubscribe(f"product_bids_notifications:{self.product_id}")
            await self.pubsub.close()
            await self.redis.close()
        except AttributeError as error:
            logger.error(f'error: {error} while connecting to notification channel.')


rwaj_routers.add_websocket_route('/ws/notifications/products/{product_id}/bids', NotificationEndpoint)


@rwaj_routers.post('products/{product_id}/new-room', status_code=201, response_model=RoomInformation)
async def new_room(product_id: int, data: CreateRoomSerializer):
    async with RwajSession() as session:
        products = await session.execute(
            select(
                Product
            ).where(
                Product.id == product_id
            )
        )
        product = products.scalar()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        users = await session.execute(
            select(
                User
            ).where(
                User.username == data.username
            )
        )
        user = users.scalar()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        room_name = f'Room-Product-{product.id}-Owner-{user.username}'
        room = Room(
            **{
                "product_id": product_id,
                "user_id": user.id,
                "name": room_name,
            }
        )
        session.add(room)
        await session.commit()
        await session.refresh(room)

        room_name, token = await create_livekit_room(room_name, user.email, product_id)
        return {
            'id': room.id,
            'room_name': room_name,
        }


@rwaj_routers.post('/rooms/{room_id}/join-room', status_code=201, response_model=RoomInformation)
async def join_room(room_id: int, data: JoinRoomSerializer):
    async with RwajSession() as session:
        rooms = await session.execute(
            select(
                Room
            ).options(
                selectinload(Room.product),
                selectinload(Room.user),
            ).where(
                Room.id == room_id
            )
        )
        room = rooms.scalar()
        if not room:
            raise HTTPException(status_code=404, detail="Stream not found")

        room_name = f'Room-Product-{room.prduct.id}-Owner-{room.user.username}'
        token = await create_livekit_read_only_viewer(data.username, room_name)
        return room_name, token
