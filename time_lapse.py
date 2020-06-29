import cv2
import numpy as np
from datetime import datetime
from capture_msi import capture_ms_img
import os
from elp_usb_cam import ELP_Camera
import matplotlib.pylab as plt
from msi_proc import *

cam = ELP_Camera(1)
ms_img = capture_ms_img(cam, pause=.2)
show_rgb_comp(ms_img)
