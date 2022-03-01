import socket
import threading
import math
from time import sleep

from pynput import keyboard
from inputs import get_gamepad

ip = "25.85.111.106"
sensibilidadJoystick = 0.8
teclaDesactivar = '.'
teclaAumentarTiempoRepeticion = "+"
teclaReducirTiempoRepeticion = "-"
tiempoRepetirBoton = 0.5

dictTeclado = {'a': 'left', 's': 'down', 'd': 'right', 'w': 'up', 97: 'a', 98: 'b', 100: 'l1', 101: 'r1'}
dictMando = {'BTN_SOUTH': 'a', 'BTN_NORTH': 'y', 'BTN_WEST': 'x',
             'BTN_EAST': 'b', 'BTN_TL': 'l1', 'BTN_TR': 'r1'}

dictMandoJoystick = {
    'ABS_HAT0X-': 'left', 'ABS_HAT0X+': 'right', 'ABS_HAT0Y+': 'down', 'ABS_HAT0Y-': 'up',
    'ABS_X-': 'left', 'ABS_X+': 'right', 'ABS_Y+': 'up', 'ABS_Y-': 'down'
}

joysticksMando = {'ABS_HAT0X', 'ABS_HAT0Y', 'ABS_X', 'ABS_Y'}

pulsada = False
pulsadoMando = -1
silenciado = False
repetirBoton = ""

# TODO añadir soporte para mantener el joystick/cruceta
def mando():
    global dictMando, pulsadoMando, dictMandoJoystick, sensibilidadJoystick, joysticksMando, repetirBoton
    joystickPulsado = []
    while True:
        eventos = get_gamepad()
        for evento in eventos:
            if evento.code in dictMando:
                if evento.state != 0:
                    pulsar = dictMando[evento.code]
                    enviarCaracter(pulsar)
            if evento.code in joysticksMando:
                if evento.code not in joystickPulsado:
                    estado = evento.state
                    if math.fabs(estado) > 1:
                        estado = estado / math.pow(2, 15)
                    if estado > sensibilidadJoystick:
                        str = evento.code + "+"
                        pulsar = dictMandoJoystick[str]
                        enviarCaracter(pulsar)
                        repetirBoton = pulsar
                        joystickPulsado.append(evento.code)
                    if estado < -sensibilidadJoystick:
                        str = evento.code + "-"
                        pulsar = dictMandoJoystick[str]
                        enviarCaracter(pulsar)
                        repetirBoton = pulsar
                        joystickPulsado.append(evento.code)
                else:
                    if math.fabs(evento.state) < sensibilidadJoystick:
                        repetirBoton = ""
                        joystickPulsado.remove(evento.code)


def repetir():
    while True:
        global repetirBoton, tiempoRepetirBoton
        if repetirBoton != "":
            repetirLocal = repetirBoton
            sleep(tiempoRepetirBoton)
            if repetirBoton == repetirLocal:
                enviarCaracter(repetirBoton)


class Mando(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'mando'

    def run(self):
        mando()


class Repetir(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'repetir'

    def run(self):
        repetir()


print("Teclas especiales: ")
print("\tSilenciar input: ", teclaDesactivar)
print("\tAumentar tiempo repetición: ", teclaAumentarTiempoRepeticion)
print("\tReducir tiempo repetición: ", teclaReducirTiempoRepeticion)
print("\tTiempo de repetición default: ", tiempoRepetirBoton)


def on_press(key):
    global pulsada, dictTeclado, silenciado, teclaDesactivar, teclaAumentarTiempoRepeticion, teclaReducirTiempoRepeticion, tiempoRepetirBoton
    try:
        if key.char == teclaDesactivar:
            if silenciado:
                silenciado = False
                print("Silencio desactivado!")
            else:
                silenciado = True
                print("Silencio activado!")
        else:
            if key.char == teclaAumentarTiempoRepeticion and silenciado is False:
                tiempoRepetirBoton = tiempoRepetirBoton + 0.1
                print("Tiempo repetir = ", tiempoRepetirBoton)
            else:
                if key.char == teclaReducirTiempoRepeticion and silenciado is False:
                    if tiempoRepetirBoton > 0.22:
                        tiempoRepetirBoton = tiempoRepetirBoton - 0.1
                    print("Tiempo repetir = ", tiempoRepetirBoton)
    except:
        pass
    if not pulsada and silenciado is False:
        try:
            tecla = key.char
            enviarCaracter(dictTeclado[tecla])
            pulsada = True
        except:
            try:
                enviarCaracter(dictTeclado[key.vk])
                pulsada = True
            except:
                pass


def on_release(key):
    global pulsada
    pulsada = False


def enviarCaracter(char):
    print(char)
    byte_message = bytes(char, 'utf-8')
    opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global ip
    opened_socket.sendto(byte_message, (ip, 65525))


hiloMando = Mando('mando').start()
hiloRepetir = Repetir('repetir').start()

with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
