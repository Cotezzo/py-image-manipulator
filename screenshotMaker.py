from mss import mss
from PIL import Image
import numpy as np
from win32api import GetSystemMetrics

def getRawScreen():
    sc_w = GetSystemMetrics(0)
    sc_h = GetSystemMetrics(1)
    mon = {'top': 0, 'left': 0, 'width': sc_w, 'height': sc_h}
    frame = mss().grab(mon)
    return Image.frombytes('RGB', frame.size, frame.bgra, "raw", "BGRX")

def arrayScreenshot():
    #screen = getRawScreen()
    #R, G, B = screen.split()
    #screen = Image.merge("RGB", [B, G, R])
    #return np.array(screen)
    R, G, B = getRawScreen().split()
    return np.array(Image.merge("RGB", [B, G, R]))

def arrayScreenshotStorto():
    return np.array(getRawScreen())