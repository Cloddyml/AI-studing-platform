import uvicorn
from fastapi import FastAPI

from app.api import routers

app = FastAPI()

for router in routers:
    app.include_router(router)


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
