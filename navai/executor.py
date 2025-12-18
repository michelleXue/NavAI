"""Goal execution and dispatch for NavAI."""

from typing import Tuple

from .action import actionOriented
from .analysis import analysisOriented
from .categorization import categorizeQuery
from task import taskOriented
from .models import ResponseCategory

Region = Tuple[int, int, int, int]


class ExecutionError(Exception):
    """Raised when goal execution fails."""
    pass


def execute_goal(goal: str, region: Region) -> str:
    """
    Categorize and execute a goal.

    Returns:
        Category name as string for logging.

    Raises:
        ExecutionError: If category is unknown.
    """
    category = categorizeQuery(goal)

    match category:
        case ResponseCategory.ACTION_ORIENTED:
            actionOriented(goal, region)
        case ResponseCategory.GENERAL_INQUIRY:
            analysisOriented(goal, region)
        case ResponseCategory.TASK_ORIENTED:
            taskOriented(goal, region)
        case _:
            raise ExecutionError(f"Unknown category: {category}")

    return category.name if hasattr(category, 'name') else str(category)
