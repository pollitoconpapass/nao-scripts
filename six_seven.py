import os
import time
import math
from naoqi import ALProxy

IP = os.getenv("IP_ADDRESS")
PORT = 9559

# --- Ajustes (grados de elevacion desde colgando: 0 = colgando, 90 = horizontal) ---
ELEV_ALTA = 45      # mano "arriba" (maximo de lo que probaste)
ELEV_BAJA = 20      # mano "abajo"
MEDIO_CICLO = 0.45  # segundos por subida/bajada (mas bajo = mas rapido)
CICLOS = 6          # cuantos six-seven seguidos
# --- Ajustes del movimiento "cruzar al hombro" ---
DURACION = 2.0      # segundos que tarda cada movimiento
PAUSA = 1.0         # delay entre movimientos

def cruzar_brazo_derecho(motion):
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw",
             "RElbowRoll", "RWristYaw"]

    # --- Tiempo 1: brazo derecho a la horizontal, mano abierta y extendida ---
    motion.setAngles(["RHand"], [1.0], 0.2)
    motion.angleInterpolation(names, [
        [0.0],      # ShoulderPitch: horizontal al frente
        [-0.1],     # ShoulderRoll: casi recto
        [0.0],      # ElbowYaw: neutro
        [0.05],     # ElbowRoll: brazo extendido
        [0.0],      # WristYaw: neutro
    ], [[DURACION]] * 5, True)
    time.sleep(PAUSA)

    # --- Tiempo 2: baja 20 grados y empieza a cruzar ---
    motion.angleInterpolation(names, [
        [math.radians(20)],   # ShoulderPitch: 20 deg por debajo de la horizontal
        [0.15],               # ShoulderRoll: empieza a cruzar hacia la izquierda
        [0.0],
        [0.8],                # ElbowRoll: codo doblado a medias
        [0.0],
    ], [[DURACION]] * 5, True)
    time.sleep(PAUSA)

    # --- Tiempo 3: mano lo mas cerca posible del hombro izquierdo ---
    motion.angleInterpolation(names, [
        [math.radians(20)],
        [0.30],               # ShoulderRoll: casi en su limite hacia adentro
        [0.0],
        [1.5],                # ElbowRoll: codo muy doblado (limite ~1.54)
        [0.0],
    ], [[DURACION]] * 5, True)
    time.sleep(PAUSA)

def pitch(elev):
    """Elevacion (grados) -> ShoulderPitch (rad)."""
    return math.radians(90 - elev)

def main():
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    motion = ALProxy("ALMotion", IP, PORT)
    posture = ALProxy("ALRobotPosture", IP, PORT)
    life = ALProxy("ALAutonomousLife", IP, PORT)

    if life.getState() != "disabled":
        life.setState("disabled")
    time.sleep(1.0)

    motion.setFallManagerEnabled(True)
    motion.setSmartStiffnessEnabled(True)

    motion.wakeUp()
    time.sleep(2.0)

    posture.goToPosture("StandInit", 0.4)
    time.sleep(2.0)

    # --- Pose inicial: antebrazos al frente, palmas arriba ---

    MUNECA_L = -1.5
    MUNECA_R = 1.5

    names = ["LShoulderPitch", "RShoulderPitch",
             "LShoulderRoll", "RShoulderRoll",
             "LElbowYaw", "RElbowYaw",
             "LElbowRoll", "RElbowRoll",
             "LWristYaw", "RWristYaw"]
    medio = pitch((ELEV_ALTA + ELEV_BAJA) / 2.0)
    angles = [[medio], [medio],
              [0.15], [-0.15],
              [-1.5], [1.5],
              [-1.0], [1.0],
              [MUNECA_L], [MUNECA_R]]
    motion.angleInterpolation(names, angles, [[2.0]] * 10, True)

    # Manos abiertas para que se vea la palma
    motion.setAngles(["LHand", "RHand"], [1.0, 1.0], 0.2)
    time.sleep(0.5)

    # --- Six seven: manos alternadas con keyframes ---
    alta = pitch(ELEV_ALTA)
    baja = pitch(ELEV_BAJA)

    L, R, tiempos = [], [], []
    t = 0.0
    for i in range(CICLOS):
        # Mano izquierda sube / derecha baja
        t += MEDIO_CICLO
        L.append(alta); R.append(baja); tiempos.append(t)
        # Mano izquierda baja / derecha sube
        t += MEDIO_CICLO
        L.append(baja); R.append(alta); tiempos.append(t)

    tts.post.say("Six... seven!")   # post = habla en paralelo al movimiento
    motion.angleInterpolation(
        ["LShoulderPitch", "RShoulderPitch"],
        [L, R],
        [tiempos, tiempos],
        True
    )

    # Dureme un rato...
    time.sleep(0.5)
    posture.goToPosture("StandInit", 0.6)
    time.sleep(2.0)  

    # Cruza el brazito
    cruzar_brazo_derecho(motion)
    posture.goToPosture("StandInit", 0.6)

    # --- Volver a reposo ---
    time.sleep(0.5)
    posture.goToPosture("StandInit", 0.6)
    time.sleep(1.0)
    motion.rest()
    print("Six seven terminado")

if __name__ == "__main__":
    main()