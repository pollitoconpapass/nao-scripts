# -*- coding: utf-8 -*-
import os
import json
import requests
import subprocess
from naoqi import ALProxy


IP   = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "dolphin-mistral"

GOOGLE_KEY = os.getenv("GOOGLE_KEY")
GOOGLE_URL = "https://www.google.com/speech-api/v2/recognize"

DEVNULL = open(os.devnull, "w")

SYSTEM_PROMPT = (
    "Eres un robot NAO amigable y gracioso. Hablas en español de manera "
    "natural y concisa. Tus respuestas deben ser cortas (maximo 3 oraciones). "
    "Actuas como un companiero adorable."
)

def grabar_y_transcribir():
    tmp = "/tmp/nao_voz.raw"

    subprocess.check_call([
        "ffmpeg", "-y",
        "-f", "avfoundation",
        "-i", ":0",
        "-t", "5",
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        "-f", "s16le",
        tmp,
    ], stdout=DEVNULL, stderr=DEVNULL)

    with open(tmp, "rb") as f:
        raw_data = f.read()

    try:
        r = requests.post(
            GOOGLE_URL,
            params={"output": "json", "lang": "es-ES", "key": GOOGLE_KEY},
            data=raw_data,
            headers={"Content-Type": "audio/l16; rate=16000; channels=1"},
            timeout=10,
        )
        r.raise_for_status()
        for line in r.text.strip().split("\n"):
            if not line:
                continue
            try:
                results = json.loads(line)
            except ValueError:
                continue
            if results and "result" in results and results["result"]:
                return results["result"][0]["alternative"][0]["transcript"].lower()
        return None
    except Exception as e:
        print("Google error:", str(e))
        return "[error]"

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
    tts.setLanguage("Spanish")
    motion.wakeUp()

    tts.say("Hola! Habla cuando quieras. Para terminar di adios o chao.")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    try:
        while True:
            print("(Escuchando... hable ahora)")
            user_input = grabar_y_transcribir()
            print(user_input)

            if user_input is None:
                print("(no entendi, repito)")
                continue

            if user_input == "[error]":
                tts.say("Tuve un error de conexion.")
                continue

            print("Tu: %s" % user_input)

            if "adios" in user_input or "chao" in user_input or "terminar" in user_input:
                tts.say("Hasta luego! Fue un placer hablar contigo.")
                break

            messages.append({"role": "user", "content": user_input})

            try:
                respuesta = chat(messages)
            except Exception as e:
                respuesta = "Lo siento, no pude conectar con mi cerebro."
                print("Error: %s" % str(e))

            print("NAO: %s" % respuesta)
            tts.say(respuesta.encode("utf-8"))
            messages.append({"role": "assistant", "content": respuesta})

    except KeyboardInterrupt:
        tts.say("Hasta luego!")
    finally:
        motion.rest()

if __name__ == "__main__":
    main()
