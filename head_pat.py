# -*- coding: utf-8 -*-
import os
import time
import random
from naoqi import ALProxy

IP = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))

PHRASES = [
    "Que bonito!",
    "Me encanta!",
    "Eso me gusta!",
    "Gracias!",
    "Que suave!",
    "Sigue asi!",
    "Eres mi favorito!",
    "Carino!",
    "Woow!",
    "Perfecto!",
    "Me haces muy feliz!",
]

def main():
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    memory = ALProxy("ALMemory", IP, PORT)
    motion = ALProxy("ALMotion", IP, PORT)

    motion.wakeUp()
    tts.setLanguage("Spanish")

    print("Tocame la cabeza! (Ctrl+C para salir)")
    tts.say("Dame caricias en la cabeza!")

    SENSORS = [
        "FrontTactilTouched",
        "MiddleTactilTouched",
        "RearTactilTouched",
    ]
    ZONES = ["frontal", "media", "trasera"]

    prev_state = {s: 0.0 for s in SENSORS}

    try:
        while True:
            for sensor, zone in zip(SENSORS, ZONES):
                try:
                    val = memory.getData(sensor)
                except:
                    val = 0.0

                if prev_state[sensor] == 0.0 and val >= 1.0:
                    phrase = random.choice(PHRASES)
                    print("Tocado! (%s) -> %s" % (zone, phrase))
                    tts.say(phrase.encode("utf-8"))

                prev_state[sensor] = val

            time.sleep(0.3)

    except KeyboardInterrupt:
        print("")

    tts.say("Hasta luego!")
    motion.rest()
    print("Listo!")


if __name__ == "__main__":
    main()
