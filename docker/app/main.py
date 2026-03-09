import os

from fastapi import FastAPI
import redis
import psycopg2

app = FastAPI(title="RedSnake")


def get_redis():
    return redis.from_url(os.environ["REDIS_URL"])


def get_pg_connection(db_url_env: str):
    return psycopg2.connect(os.environ[db_url_env])


@app.get("/")
async def root():
    return {"app": "redsnake", "status": "running"}


@app.get("/health")
async def health():
    checks = {}

    # Redis
    try:
        r = get_redis()
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = str(e)

    # PostgreSQL system DB
    try:
        conn = get_pg_connection("SYSTEM_DATABASE_URL")
        conn.close()
        checks["postgres_system"] = "ok"
    except Exception as e:
        checks["postgres_system"] = str(e)

    # PostgreSQL user DB
    try:
        conn = get_pg_connection("USER_DATABASE_URL")
        conn.close()
        checks["postgres_user"] = "ok"
    except Exception as e:
        checks["postgres_user"] = str(e)

    healthy = all(v == "ok" for v in checks.values())
    return {"healthy": healthy, "checks": checks}
