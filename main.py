from navai.action import actionOriented
from navai.analysis import analysisOriented
from navai.categorization import categorizeQuery
from task import taskOriented
from navai.models import ResponseCategory

# NavAI

# Setup:
# Set screenshot bounds with bounds.py and place region variable
# Set goal in goal variable
# Place api key in api_key.txt

# goal = ""
# region = (x1, y1, width, height)
#goal = "Get to the yellow bus and avoid hitting other cars, go around them. You can stop when you are near it."
# goal = "Where am I?"
# goal = "Walk forward for three seconds, turn to the left for one second, and walk right for two seconds."
#goal = "Walk through the doorway on the left walk into the bedroom."
goal = "Move Right"
region = (969, 142, 942, 557)

category = categorizeQuery(goal)

#TODO: Look for table 1 in Page 3 of docd

match category:
    case ResponseCategory.ACTION_ORIENTED:
        actionOriented(goal,region)
    case ResponseCategory.GENERAL_INQUIRY:
        # exploratory goal oriented
        # TODO: Try to stop once we find the target
        analysisOriented(goal, region)
    case ResponseCategory.TASK_ORIENTED:
        # Direct goal navigator
        # Semantic Interpreter too inside
        taskOriented(goal, region)
    case _:
        print(f"Unknown response category: {category}")
