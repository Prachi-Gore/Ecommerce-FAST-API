python -m venv venv

venv\scripts\activate

pip install -r requirements.txt

alembic revision --autogenerate -m "create table"

alembic upgrade head

fastapi dev
