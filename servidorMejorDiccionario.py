import math
import socket
import threading
import queue
from time import sleep

from pynput.keyboard import Key, Controller
from inputs import get_gamepad

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('25.85.111.106', 65525)
s.bind(server_address)

queue = queue.Queue()
keyboard = Controller()

# TODO añadir mantener
botonATecla = {
    'a': Key.enter,
    'b': Key.shift,
    'left': 'a',
    'down': 's',
    'right': 'd',
    'up': 'w',
    'l1': 'q',
    'r1': 'e'
}

sensibilidadJoystick = 0.8

dictMando = {'BTN_SOUTH': 'a', 'BTN_NORTH': 'y', 'BTN_WEST': 'x',
             'BTN_EAST': 'b', 'BTN_TL': 'l1', 'BTN_TR': 'r1'}

dictMandoJoystick = {
    'ABS_HAT0X-': 'left', 'ABS_HAT0X+': 'right', 'ABS_HAT0Y+': 'down', 'ABS_HAT0Y-': 'up',
    'ABS_X-': 'left', 'ABS_X+': 'right', 'ABS_Y+': 'up', 'ABS_Y-': 'down'
}

joysticksMando = {'ABS_HAT0X', 'ABS_HAT0Y', 'ABS_X', 'ABS_Y'}

pulsada = False
pulsadoMando = -1


def mando():
    global dictMando, pulsadoMando, dictMandoJoystick, sensibilidadJoystick, joysticksMando
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
                        joystickPulsado.append(evento.code)
                    if estado < -sensibilidadJoystick:
                        str = evento.code + "-"
                        pulsar = dictMandoJoystick[str]
                        enviarCaracter(pulsar)
                        joystickPulsado.append(evento.code)
                else:
                    if math.fabs(evento.state) < sensibilidadJoystick:
                        joystickPulsado.remove(evento.code)


def enviarCaracter(char):
    print(char)
    queue.put(botonATecla[char])


class Mando(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'mando'

    def run(self):
        mando()


def leer():
    while True:
        data, address = s.recvfrom(4096)
        tecla = data.decode('utf-8')
        global queue
        try:
            queue.put(botonATecla[tecla])
        except:
            print(tecla)


def escribir():
    while True:
        try:
            tecla = queue.get()
            try:
                global keyboard
                keyboard.press(tecla)
                sleep(0.10)
                keyboard.release(tecla)
            except:
                pass
        except queue.Empty:
            pass


class lectura(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'lectura'

    def run(self):
        leer()


class escritura(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'escritura'

    def run(self):
        escribir()


hilo1 = lectura('lectura').start()
hilo2 = escritura('escritura').start()
hiloMando = Mando('mando').start()
