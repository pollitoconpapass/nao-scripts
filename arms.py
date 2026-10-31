import os
import time
import math
from naoqi import ALProxy

IP = os.getenv("IP_ADDRESS")
PORT = 9559

# Elevacion del brazo desde la posicion colgando (0 = colgando, 90 = horizontal al frente)
ANGULO_GRADOS = 45
DURACION = 2.0   # segundos, lento para probar con seguridad

def main():
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)
    life = ALProxy("ALAutonomousLife", IP, PORT)

    # Evita que Autonomous Life interfiera
    if life.getState() != "disabled":
        life.setState("disabled")
    time.sleep(1.0)

    motion.setFallManagerEnabled(True)
    motion.setSmartStiffnessEnabled(True)

    motion.wakeUp()
    time.sleep(2.0)

    posture.goToPosture("StandInit", 0.4)
    time.sleep(2.0) 


    # Convierte elevacion a ShoulderPitch: colgando = ~90 deg (1.57 rad), horizontal = 0
    pitch = math.radians(90 - ANGULO_GRADOS)
    print("ShoulderPitch objetivo: %.3f rad" % pitch)

    names = ["LShoulderPitch", "RShoulderPitch"]

    # Subir
    motion.angleInterpolation(names, [[pitch], [pitch]], [[DURACION], [DURACION]], True)
    time.sleep(1.5)

    # Bajar
    motion.angleInterpolation(names, [[math.radians(80)], [math.radians(80)]],
                              [[DURACION], [DURACION]], True)
    time.sleep(0.5)

    posture.goToPosture("StandInit", 0.6)
    time.sleep(1.0)
    motion.rest()
    print("Prueba terminada")

if __name__ == "__main__":
    main()