from app.api.auth import router as router_auth
from app.api.users import router as router_user

routers = [
    router_auth,
    router_user,
]
