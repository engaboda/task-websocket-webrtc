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
