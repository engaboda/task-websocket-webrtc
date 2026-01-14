## After cloning the repository, execute following commands
1. python3.12 -m venv .venv
2. pip install -r requirements.txt


## Generating Migrations
1. python -m alembic revision --autogenerate -m "user_bid_project_db_models_initail"
2. python -m alembic upgrade head


## when freshly migrating to DB
1. `python -m alembic upgrade head`

## Apis App Provide
1. {{url}}/{{prefix}}/products/{{product_id}}/new-bid
2. {{url}}/{{prefix}}/products/{{product_id}}/highest-bids
3. {{url}}/{{prefix}}/products/{{product_id}}/bids
4. {{url}}/{{prefix}}/products
5. {{url}}/{{prefix}}/products/{{product_id}}/new-room
```New Room Response
{
    "id": 6,
    "room_name": "Room-Product-1-Owner-aboda",
    # with permission [can sub, can pub, can pub data]
    "token": ""
}
```
6. {{url}}/{{prefix}}/rooms/{{room_id}}/join-room
```Joining Room Response
{
    "room_name": "Room-Product-1-Owner-aboda",
    # with permission [can sub]
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidXNlci1haG1lZCIsInZpZGVvIjp7InJvb21BZG1pbiI6ZmFsc2UsInJvb21Kb2luIjp0cnVlLCJyb29tIjoiUm9vbS1Qcm9kdWN0LTEtT3duZXItYWJvZGEiLCJjYW5QdWJsaXNoIjpmYWxzZSwiY2FuU3Vic2NyaWJlIjp0cnVlLCJjYW5QdWJsaXNoRGF0YSI6ZmFsc2V9LCJzdWIiOiJ1c2VyLWFobWVkIiwiaXNzIjoiQVBJN3ZLNGp4ejlUU0JYIiwibmJmIjoxNzY4NDAxNTU0LCJleHAiOjE3Njg0MjMxNTR9.lXBHwT0hdbZVgSp0rxH_b2tVXTXSX8HOoxv0nGBiZnk"
}
```

## websocket App Provide
1. ws://localhost:8000/ws/notifications/products/{{product_id}}/bids


## to deploy it using docker swarm
1. docker build -t rwaj .
2. docker swarm init
3. docker node ls
4. docker stack deploy -c docker-compose.yml rwaj
5. docker services logs rwaj_backend -f

## to clean the containers
1. docker stack rm rwaj
