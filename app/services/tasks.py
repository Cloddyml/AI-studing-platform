from app.exceptions.excs import SolutionNotFoundException, TaskNotFoundException
from app.schemas.solutions import SolutionDTO
from app.schemas.tasks import TaskDetailDTO
from app.services.base import BaseService


class TasksService(BaseService):
    async def get_task_by_id(self, task_id: int) -> TaskDetailDTO:
        task = await self.db.tasks.get_published_by_id(task_id)
        if task is None:
            raise TaskNotFoundException
        return task

    async def get_task_solution(self, task_id: int, user_id: int) -> SolutionDTO:
        task = await self.db.tasks.get_published_by_id(task_id)
        if task is None:
            raise TaskNotFoundException
        solution = await self.db.solutions.get_user_solution(
            user_id=user_id, task_id=task_id
        )
        if solution is None:
            raise SolutionNotFoundException
        return solution
