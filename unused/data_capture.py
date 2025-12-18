import pyautogui as pag
import time
import pydirectinput as pdi

time.sleep(2)

# for table
# pdi.keyDown('s')
# time.sleep(6)
# pdi.keyUp('s')

# for lamp
# MANUALLY TURN AROUND FIRST
pdi.keyDown('a')
time.sleep(2)
pdi.keyUp('a')
pdi.keyDown('w')
time.sleep(2)
pdi.keyUp('w')

print("check distance")
time.sleep(2)
screenshot = pag.screenshot(region=(1397, 358, 1008, 562))
screenshot.save(f"screenshots/lamp{1}.png")

for i in range(4):
    pdi.keyDown('w')
    time.sleep(0.75)
    pdi.keyUp('w')
    print("check distance")
    screenshot = pag.screenshot(region=(1397, 358, 1008, 562))

    screenshot.save(f"screenshots/lamp{i+2}.png")
    time.sleep(3)
    


