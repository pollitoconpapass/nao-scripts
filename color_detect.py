# -*- coding: utf-8 -*-
import os
import cv2
import time
import numpy as np
import vision_definitions
from naoqi import ALProxy


IP = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))

CAMERA_INDEX   = 0
RESOLUTION     = vision_definitions.kVGA
COLOR_SPACE    = vision_definitions.kBGRColorSpace
FPS            = 15

UMBRAL_AREA = 500

LOWER_COLOR = np.array([0, 50, 50])
UPPER_COLOR = np.array([10, 255, 255])
COLOR_NAME = "rojo"

def main():
    vdev = ALProxy("ALVideoDevice", IP, PORT)
    tts  = ALProxy("ALTextToSpeech", IP, PORT)
    motion = ALProxy("ALMotion", IP, PORT)

    prev_life = None
    life = None
    try:
        life = ALProxy("ALAutonomousLife", IP, PORT)
        prev_life = life.getState()
        life.setState("disabled")
    except:
        pass

    try:
        motion.wakeUp()
    except:
        pass

    client_name = "colorDetect_%d" % int(time.time())
    handle = vdev.subscribeCamera(client_name, CAMERA_INDEX, RESOLUTION, COLOR_SPACE, FPS)

    tts.say("Buscando color %s" % COLOR_NAME)
    encontrado = False

    try:
        while True:
            img = vdev.getImageRemote(handle)
            if img is None:
                time.sleep(0.01)
                continue

            w = img[0]
            h = img[1]
            data = img[6]

            frame = np.fromstring(data, dtype=np.uint8)
            if frame.size != w * h * 3:
                continue
            frame = frame.reshape((h, w, 3))

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
            area = cv2.countNonZero(mask)

            if not encontrado and area > UMBRAL_AREA:
                encontrado = True
                tts.say("Lo encontré!!")
                print("¡Color %s detectado! (area=%d)" % (COLOR_NAME, area))

    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
    finally:
        try:
            vdev.unsubscribe(handle)
        except:
            pass
        try:
            motion.rest()
        except:
            pass
        if life is not None and prev_life is not None:
            try:
                life.setState(prev_life)
            except:
                pass

if __name__ == "__main__":
    main()
