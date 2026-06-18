# -*- coding: utf-8 -*-
import os
import time
from naoqi import ALProxy

IP = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))

def main():
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)

    motion.wakeUp()

    posture.goToPosture("StandInit", 0.7)
    time.sleep(0.5)

    # Baymax fistbump: raise right arm, extend fist, bump
    joint_names = [
        "RShoulderPitch",  # + = forward, - = backward
        "RShoulderRoll",   # + = out to side
        "RElbowRoll",      # + = bent (hand up), - = straight
        "RElbowYaw",       # forearm rotation
        "RWristYaw"
    ]

    # 1) Raise fist (arm bent, fist up)
    angles_raise  = [[0.3], [0.2], [1.2], [0.0], [0.0]]
    times_raise   = [[1.5], [1.5], [1.5], [1.5], [1.5]]

    # 2) Extend fist forward
    angles_extend = [[0.6], [0.2], [0.3], [0.0], [0.0]]
    times_extend  = [[1.0], [1.0], [1.0], [1.0], [1.0]]

    # 3) The bump (small forward-backward motion)
    angles_bump_fwd = [[0.7], [0.2], [0.2], [0.0], [0.0]]
    angles_bump_bck = [[0.5], [0.2], [0.4], [0.0], [0.0]]
    times_bump      = [[0.3], [0.3], [0.3], [0.3], [0.3]]

    # 4) Return to rest
    angles_rest  = [[1.5], [0.1], [0.0], [0.0], [0.0]]
    times_rest   = [[1.0], [1.0], [1.0], [1.0], [1.0]]

    motion.angleInterpolation(joint_names, angles_raise,  times_raise,  True)
    motion.angleInterpolation(joint_names, angles_extend, times_extend, True)

    # Say tralalala during the bump motion
    # Bump motions while singing (post.say = non-blocking)
    tts.post.say("tralalalalalalalalalalalala")

    for _ in range(3):
        motion.angleInterpolation(joint_names, angles_bump_fwd, times_bump, True)
        motion.angleInterpolation(joint_names, angles_bump_bck, times_bump, True)

    motion.angleInterpolation(joint_names, angles_rest, times_rest, True)

    motion.rest()

if __name__ == "__main__":
    main()
