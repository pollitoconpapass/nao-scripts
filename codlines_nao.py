import os
import time
import random
from naoqi import ALProxy 

IP=os.getenv("IP_ADDRESS")
PROXY=int(os.getenv("PORT"))

tts = ALProxy("ALTextToSpeech", IP, PROXY)
postura = ALProxy("ALRobotPosture", IP, PROXY)
motion = ALProxy("ALMotion", IP, PROXY)

a = random.uniform(0,1)
b = random.uniform(0,1)

names = ["LShoulderRoll","RShoulderPitch"]
times = [[1],[1]]

#motion.moveInit()
start = time.time()
postura.goToPosture("StandInit", 0.7)
end = time.time()
tiempo_execution = end-start
print(tiempo_execution)
start = time.time()
motion.angleInterpolation(names,[a,0.0],times,True)
motion.angleInterpolation(names,[a,b],times,True)
tts.say("Hola")
end = time.time()

tiempo_execution = end-start
print(tiempo_execution)
