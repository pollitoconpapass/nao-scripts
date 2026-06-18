import os
import time
from naoqi import ALProxy

IP = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))

def move_joints(motion, names, angles, times, absolute=True):
    motion.angleInterpolation(names, angles, times, absolute)

def main():
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)

    motion.wakeUp()
    posture.goToPosture("StandInit", 1.0)
    time.sleep(0.5)

    LH = "LShoulderPitch"
    LR = "LShoulderRoll"
    LY = "LElbowYaw"
    LB = "LElbowRoll"
    RH = "RShoulderPitch"
    RR = "RShoulderRoll"
    RY = "RElbowYaw"
    RB = "RElbowRoll"
    HP = "LHipPitch"
    HR = "LHipRoll"
    Head = "HeadPitch"

    print("Disco time in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Let's dance!")

    # --- Move 1: Disco point up + look up ---
    move_joints(motion, [LH, RH, LR, RR, Head], [
        [1.2], [0.3],
        [-0.1], [0.3],
        [-0.3],
    ], [[0.8], [0.8], [0.8], [0.8], [0.8]])
    tts.say("Disco!")

    # --- Move 2: Switch point direction ---
    move_joints(motion, [LH, RH, LR, RR], [
        [0.3], [1.2],
        [0.3], [-0.1],
    ], [[0.6], [0.6], [0.6], [0.6]])
    tts.say("Fieeesta!")

    # --- Move 3: The hustle - arms wave side to side ---
    for i in range(2):
        move_joints(motion, [LR, RR, LB, RB], [
            [-0.5], [0.5],
            [-0.8], [0.8],
        ], [[0.4], [0.4], [0.4], [0.4]])
        move_joints(motion, [LR, RR, LB, RB], [
            [0.2], [-0.2],
            [-1.2], [1.2],
        ], [[0.4], [0.4], [0.4], [0.4]])

    # --- Move 4: Get down (bend knees) ---
    move_joints(motion, [HP, LR, RR, LB, RB], [
        [-0.4], [0.1], [-0.1],
        [-0.5], [0.5],
    ], [[0.6], [0.6], [0.6], [0.6], [0.6]])
    tts.say("Yeah!")
    move_joints(motion, [HP, LB, RB], [
        [0.0], [-1.2], [1.2],
    ], [[0.5], [0.5], [0.5]])

    # --- Move 5: Hip sway with arms ---
    for i in range(2):
        move_joints(motion, [HR, LR, RR], [
            [-0.25], [-0.6], [0.6],
        ], [[0.5], [0.5], [0.5]])
        move_joints(motion, [HR, LR, RR], [
            [0.25], [0.2], [-0.2],
        ], [[0.5], [0.5], [0.5]])

    # --- Move 6: Arm roll / spaghetti arms ---
    move_joints(motion, [LY, RY], [
        [0.0], [0.0],
    ], [[0.5], [0.5]])
    tts.say("Oeoeeooeo!")

    # --- Move 7: Side lunge point ---
    move_joints(motion, [LH, RH, LR, RR, LY, RY], [
        [0.3], [0.3],
        [-0.8], [-0.2],
        [-1.5], [1.5],
    ], [[0.8], [0.8], [0.8], [0.8], [0.8], [0.8]])
    tts.say("Mas!")
    move_joints(motion, [LR, RR, LY, RY], [
        [-0.2], [0.8],
        [1.5], [-1.5],
    ], [[0.8], [0.8], [0.8], [0.8]])

    # --- Move 8: Head bob + arms up ---
    move_joints(motion, [Head, LH, RH, LR, RR], [
        [0.2], [1.2], [1.2],
        [-0.3], [0.3],
    ], [[0.5], [0.5], [0.5], [0.5], [0.5]])
    time.sleep(0.3)
    move_joints(motion, [Head], [
        [-0.3],
    ], [[0.4]])
    time.sleep(0.3)

    # --- Move 9: Finale - Saturday night fever arms ---
    move_joints(motion, [LH, RH, LR, RR, LY, RY], [
        [0.8], [0.8],
        [-0.9], [0.9],
        [-2.0], [2.0],
    ], [[0.8], [0.8], [0.8], [0.8], [0.8], [0.8]])
    tts.say("Gracias y buenas noches!")

    time.sleep(1.0)

    posture.goToPosture("StandInit", 1.0)
    time.sleep(0.5)
    motion.rest()
    print("Disco dance finished!")


if __name__ == "__main__":
    main()