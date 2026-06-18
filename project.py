# -*- coding: utf-8 -*-
import os
import time
import json
import random
import requests
import subprocess
from naoqi import ALProxy

# BOT QUE HABLA ESPAÑOL
IP   = os.getenv("IP_ADDRESS")
PORT = int(os.getenv("PORT"))
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "dolphin-mistral"

GOOGLE_KEY = os.getenv("GOOGLE_KEY")
GOOGLE_URL = "https://www.google.com/speech-api/v2/recognize"

DEVNULL = open(os.devnull, "w")

SYSTEM_PROMPT = (
    "Eres el Doctor Ricardo, un asistente medico amigable y cercano. "
    "Hablas de forma natural y conversacional, como un medico de confianza. "
    "El usuario es un paciente que viene a consulta. Preguntale sobre sus sintomas, "
    "cuanto tiempo lleva asi, que ha hecho al respecto. Haz preguntas de seguimiento "
    "una por una, no todas de golpe. Cuando tengas suficiente informacion, ofrece "
    "un posible diagnostico y recomendaciones. Tus respuestas deben ser claras pero "
    "con un tono calido y humano. Maximo 4 oraciones por respuesta. "
    "Responde solo con el mensaje que le daras al usuario, no incluyas ningun otro "
    "razonamiento o informacion adicional."
)

FEEDBACK_PHRASES = [
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

WALK_SPEED = 0.25
WALK_TIMEOUT = 30

SENSORS = [
    "FrontTactilTouched",
    "MiddleTactilTouched",
    "RearTactilTouched",
]

def esperar_caricia(motion, memory):
    print("Caminando... toca la cabeza para detenerme.")
    motion.moveInit()
    motion.moveToward(WALK_SPEED, 0, 0)

    prev_state = {s: 0.0 for s in SENSORS}
    start = time.time()
    pat_detected = False

    while time.time() - start < WALK_TIMEOUT:
        for sensor in SENSORS:
            try:
                val = memory.getData(sensor)
            except ValueError:
                val = 0.0

            if prev_state[sensor] == 0.0 and val >= 1.0:
                pat_detected = True
                break

            prev_state[sensor] = val

        if pat_detected:
            break

        time.sleep(0.2)

    motion.stopMove()
    return pat_detected

def esperar_feedback(tts, memory, motion, timeout=15):
    SENSORS = [
        "FrontTactilTouched",
        "MiddleTactilTouched",
        "RearTactilTouched",
    ]
    ZONES = ["frontal", "media", "trasera"]
    prev_state = {s: 0.0 for s in SENSORS}
    pat_detected = False
    start = time.time()
    while time.time() - start < timeout:
        for sensor, zone in zip(SENSORS, ZONES):
            try:
                val = memory.getData(sensor)
            except ValueError:
                val = 0.0
            if prev_state[sensor] == 0.0 and val >= 1.0:
                pat_detected = True
                phrase = random.choice(FEEDBACK_PHRASES)
                print("Tocado! (%s) -> %s" % (zone, phrase))
                tts.say(phrase)
                names = ["LShoulderPitch", "RShoulderPitch"]
                angles = [[0.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
                times = [[0.3, 0.7, 1.0], [0.3, 0.7, 1.0]]
                motion.angleInterpolation(names, angles, times, True)
            prev_state[sensor] = val
        time.sleep(0.3)
    return pat_detected

def saludar(motion):
    names = ["RShoulderRoll", "RElbowYaw", "RElbowRoll", "RShoulderPitch"]
    angle_lists = [
        [-0.5, -0.2, -0.5, -0.2],
        [ 1.0,  1.0,  1.0,  1.0],
        [ 0.5,  0.5,  0.5,  0.5],
        [ 0.5,  0.5,  0.2,  0.5],
    ]
    times = [
        [0.3, 0.7, 1.0, 1.4],
    ] * 4
    motion.angleInterpolation(names, angle_lists, times, True)

def choque_mano(motion, memory, tts):
    tts.say("Choca esos cinco!")
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw", "RWristYaw"]
    target_angles = [0.3, -0.1, 0.5, 0.8, 0.0]
    motion.angleInterpolation(names, target_angles, [1.0], True)
    SENSORS = [
        "HandRightBackTouched",
        "HandRightLeftTouched",
        "HandRightRightTouched",
    ]
    prev_state = {s: 0.0 for s in SENSORS}
    start = time.time()
    bumped = False
    while time.time() - start < 10:
        for sensor in SENSORS:
            try:
                val = memory.getData(sensor)
            except ValueError:
                val = 0.0
            if prev_state[sensor] == 0.0 and val >= 1.0:
                bumped = True
                break
            prev_state[sensor] = val
        if bumped:
            break
        time.sleep(0.2)
    if bumped:
        tts.say("Bien!")
    retract = [0.5, 0.0, 0.0, 0.0, 0.0]
    motion.angleInterpolation(names, retract, [0.5], True)

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
    memory = ALProxy("ALMemory", IP, PORT)
    life = ALProxy("ALAutonomousLife", IP, PORT)

    prev_life = life.getState()
    life.setState("disabled")

    motion.wakeUp()
    tts.setLanguage("Spanish")

    tts.say("Caminando, toca mi cabeza para detenerme.")

    encontrado = esperar_caricia(motion, memory)

    if not encontrado:
        tts.say("No detecte ningun toque. Intente de nuevo.")
        motion.rest()
        life.setState(prev_life)
        return

    tts.say("Hola! Soy el Doctor Ricardo, tu asistente medico.")
    saludar(motion)

    track = ALProxy("ALTracker", IP, PORT)
    track.setMode("Head")
    track.registerTarget("Face", 0.1)
    track.track("Face")

    time.sleep(1)

    tts.say("Cuentame, que te trae por aqui? Que te duele?")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    try:
        while True:
            print("(Escuchando... hable ahora)")
            user_input = grabar_y_transcribir()
            print(user_input)

            if user_input is None:
                tts.say("Perdon, no te escuche bien. Podrias repetirlo?")
                continue

            if user_input == "[error]":
                tts.say("Tuve un problema de conexion. Intenta de nuevo.")
                continue

            print("Tu: %s" % user_input)

            if "adios" in user_input or "chao" in user_input or "terminar" in user_input:
                tts.say("Fue un placer ayudarte. Cuidese mucho, hasta luego!")
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

        tts.say("Te gusto la consulta? Si fue asi, dame una caricia en la cabeza!")
        esperar_feedback(tts, memory, motion)
        choque_mano(motion, memory, tts)

    except KeyboardInterrupt:
        tts.say("Hasta luego!")
    finally:
        try:
            track.stopTracker()
            track.unregisterAllTargets()
        except Exception:
            pass
        motion.rest()
        life.setState(prev_life)

if __name__ == "__main__":
    main()
