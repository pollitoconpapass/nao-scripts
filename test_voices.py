# -*- coding: utf-8 -*-
import os
import time
from naoqi import ALProxy


IP = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))

VOICE_PROFILES = [
    {
        "name": "Normal (default)",
        "language": "Spanish",
        "params": {},
    },
    {
        "name": "Agudo (high pitch)",
        "language": "Spanish",
        "params": {"pitchShift": 1.8},
    },
    {
        "name": "Grave (low pitch)",
        "language": "Spanish",
        "params": {"pitchShift": 0.6},
    },
    {
        "name": "Rapido (fast)",
        "language": "Spanish",
        "params": {"speed": 150},
    },
    {
        "name": "Lento (slow)",
        "language": "Spanish",
        "params": {"speed": 60},
    },
    {
        "name": "Susurro (low volume)",
        "language": "Spanish",
        "params": {"volume": 30},
    },
    {
        "name": "Fuerte (high volume)",
        "language": "Spanish",
        "params": {"volume": 100},
    },
    {
        "name": "English (default)",
        "language": "English",
        "params": {},
    },
    {
        "name": "English (fast & high)",
        "language": "English",
        "params": {"speed": 140, "pitchShift": 1.5},
    },
    {
        "name": "English (slow & low)",
        "language": "English",
        "params": {"speed": 60, "pitchShift": 0.7},
    },
]

TEXTS = {
    "Spanish": (
        "Hola! Soy el robot NAO. Esta es mi voz con los parametros actuales. "
        "Puedo cambiar mi tono, velocidad y volumen."
    ),
    "English": (
        "Hello! I am the NAO robot. This is my voice with the current settings. "
        "I can change my pitch, speed and volume."
    ),
}

def apply_params(tts, params):
    tts.setParameter("pitchShift", params.get("pitchShift", 1.0))
    tts.setParameter("speed", params.get("speed", 100))
    if "volume" in params:
        tts.setParameter("volume", params["volume"])

def main():
    tts = ALProxy("ALTextToSpeech", IP, PORT)

    print("=" * 60)
    print("PRUEBA DE VOCES - NAO VOICE TEST")
    print("=" * 60)
    print("")
    print("Probando %d perfiles de voz..." % len(VOICE_PROFILES))
    print("")

    input("Presiona Enter para comenzar...")

    for i, profile in enumerate(VOICE_PROFILES, 1):
        print("[%d/%d] %s" % (i, len(VOICE_PROFILES), profile["name"]))
        print("  Language: %s, Params: %s" % (profile["language"], profile["params"]))

        tts.setLanguage(profile["language"])
        apply_params(tts, profile["params"])

        text = TEXTS.get(profile["language"], TEXTS["Spanish"])
        tts.say(text.encode("utf-8"))

        time.sleep(0.5)
        print("")

    # Reset to defaults
    tts.setLanguage("Spanish")
    apply_params(tts, {"pitchShift": 1.0, "speed": 100, "volume": 80})
    print("Prueba completada! Volviendo a valores por defecto.")


if __name__ == "__main__":
    main()
