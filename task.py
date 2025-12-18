from navai.user_action_decider.draw_grid import grid
from navai.user_action_decider.area_sensitivity import *
from navai.user_action_decider.object_detection import *
from navai.user_action_decider.utils import *
from navai.user_action_decider.json_action import *
from end_check.end_condition import *
import json

def taskOriented(goal, region):

    times = []
    endtimes = []
    detecttimes = []
    senstimes = []
    actiontimes = []
    screenshottimes = []

    ending = False

    counter = 0

    prevA = 0
    currA = 0

    # 0 actions
    # 1 screenshots
    # 2 areas
    # 3 sensitivities
    # 4 json
    context = [[None for _ in range(20)] for _ in range(5)]

    while not ending:

        start_time = time.time()
        ssstart = time.time()
        # screenshot
        screenshot(counter, region)

        # draw grid
        grid("temp/screenshot_original", "temp/grid_images")

        # compress screenshot
        compress_images_in_folder("temp/grid_images", "temp/screenshot_compressed")

        context[1][counter] = f"temp/screenshot_compressed/screenshot{counter}.png"
        
        ssend = time.time()
        screenshottimes.append(ssend - ssstart)

        # Check if finished
        compress_images_in_folder("temp/screenshot_original", "temp/screenshot_compressed")
        endstart = time.time()
        ending = finished(goal, f"temp/screenshot_compressed/screenshot{counter}.png", context[3])
        endend = time.time()
        endtimes.append(endend - endstart)
        print(f"Finished: {ending}")
        if ending:
            break

        # detect objects and save to json
        startdet = time.time()
        target = detect_objects(f"temp/screenshot_compressed/screenshot{counter}.png", goal)
        enddet = time.time()
        detecttimes.append(enddet - startdet)

        # parse json
        jsonPath = f"screenshotjson/screenshot{counter}.json"

        with open(jsonPath, "r", encoding="utf-8") as file:
            data = json.load(file)
            json_string = json.dumps(data)

        context[4][counter] = json_string

        # Get sensitivity
        sensstart = time.time()
        if counter == 0:
            s = 1
            currA = getArea(f"temp/screenshot_compressed/screenshot{counter}.png", goal)
        if counter > 0:        
            prevA = currA
            currA = getArea(f"temp/screenshot_compressed/screenshot{counter}.png", goal)
            s = sens(currA, prevA, 5) 
        sensend = time.time()
        senstimes.append(sensend - sensstart)


        context[2][counter] = currA
        context[3][counter] = s

        # determine action
        print(target)
        print(s)
        actionstart = time.time()
        context[0][counter] = determine_action(json_string, target, f"temp/screenshot_compressed/screenshot{counter}.png", s, context, counter, region)       
        actionend = time.time()
        actiontimes.append(actionend - actionstart)
        counter += 1

        end_time = time.time()
        times.append(end_time - start_time)

    print("Done")
    print(f"{counter} steps taken")
    avg = 0
    endavg = 0
    ssavg = 0
    sensavg = 0
    detectavg = 0
    actionavg = 0

    for i in range (len(times)):
        print(f"Step {i+1}: {times[i]}, end {endtimes[i]}, sens {senstimes[i]}, detect {detecttimes[i]}, action {actiontimes[i]}")
        avg += times[i]
        endavg += endtimes[i]
        ssavg += screenshottimes[i]
        sensavg += senstimes[i]
        detectavg += detecttimes[i]
        actionavg += actiontimes[i]

    print(f"Average time cost: {avg/counter}")
    print(f"Average end check time cost: {endavg/counter}")
    print(f"Screenshot time cost: {ssavg/counter}")
    print(f"Average detection time cost: {detectavg/counter}")
    print(f"Average sensitivity time cost: {sensavg/counter}")
    print(f"Average action time cost: {actionavg/counter}")
