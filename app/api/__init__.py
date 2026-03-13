from app.api.auth import router as router_auth
from app.api.tasks import router as router_tasks
from app.api.topics import router as router_topics
from app.api.users import router as router_users

routers = [
    router_auth,
    router_users,
    router_topics,
    router_tasks,
]
