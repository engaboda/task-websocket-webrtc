import json
import logging

from livekit import api
from src.config import settings
from src.db.engine import RwajSession
from src.db.models import Product, User
from src.security import hash_password

logger = logging.getLogger(__name__)


async def create_product(name: str, price: float):
    async with RwajSession() as session:
        new_product = Product(name=name, price=price)
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product


async def create_user(username: str, email: str, password: str):
    async with RwajSession() as session:
        user = User(username=username, email=email, password=hash_password(password))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def publish_to_channel(message: str, product_id: int) -> None:
    logger.info(f"publishing to channel: {message} for product: {product_id}")
    try:
        settings.redis.redis_client.publish(
            f'product_bids_notifications:{product_id}',
            json.dumps({
                "type": "notification",
                "data": message
            })
        )
    except Exception as error:
        logger.exception(f'error: {error} while sending message: {message} to product: {product_id}')


async def create_livekit_room(room_name, username: str, product_id: int):
    lkapi = api.LiveKitAPI(
        url=settings.livekit.url,
        api_key=settings.livekit.api_key,
        api_secret=settings.livekit.secret_key,
    )
    # Create a room
    room = await lkapi.room.create_room(
        api.CreateRoomRequest(name=room_name)
    )

    logger.info(f'room: {room} created for user: {username} for product: {product_id}')

    # Generate access token for the user
    token = api.AccessToken().with_identity(username).with_name(username).with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_publish_data=True,
            can_subscribe=True,
        )
    ).to_jwt()

    await lkapi.aclose()
    return room.name, token


async def create_livekit_read_only_viewer(user_name: str, room_name: str):
    viewer_id = f"user-{user_name}"

    token = (
        api.AccessToken(api_key=settings.livekit.api_key, api_secret=settings.livekit.secret_key)
        .with_identity(viewer_id)
        .with_name(viewer_id)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_subscribe=True,
                can_publish=False,
                can_publish_data=False,
                room_admin=False,
            )
        )
        .to_jwt()
    )

    return token
