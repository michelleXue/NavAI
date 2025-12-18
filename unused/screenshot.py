import pyautogui as pag

screenshot = pag.screenshot(region=(1397, 358, 1008, 562))
screenshot.save(f"screenshots/coffeetable{315}degrees.png")