# -*- coding: utf-8 -*-
import os
import requests
from naoqi import ALProxy

IP   = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "dolphin-mistral"

SYSTEM_PROMPT = (
    "Eres un robot NAO amigable y gracioso. Hablas en ingles de manera "
    "natural y concisa. Tus respuestas deben ser cortas (máximo 3 oraciones). "
    "Actúas como un compañero adorable."
)

def chat(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["message"]["content"]

def main():
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    motion = ALProxy("ALMotion", IP, PORT)
    tts.setLanguage("English")

    motion.wakeUp()

    tts.say("Hola! Soy tu robot. Escribe algo y te responderé. Presiona Enter con mensaje vacío para salir.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    try:
        while True:
            user_input = raw_input("\nTú: ").decode("utf-8")
            if not user_input.strip():
                break

            messages.append({"role": "user", "content": user_input})

            try:
                respuesta = chat(messages)
            except Exception as e:
                respuesta = "Lo siento, no pude conectar con mi cerebro. Error: %s" % str(e)

            print("NAO: %s" % respuesta)
            tts.say(respuesta.encode("utf-8"))
            messages.append({"role": "assistant", "content": respuesta})

    except KeyboardInterrupt:
        pass

    tts.say("Hasta luego!")
    motion.rest()

if __name__ == "__main__":
    main()
