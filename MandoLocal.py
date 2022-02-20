import socket
import threading
import math

from inputs import get_gamepad

ip = "localhost"
sensibilidadJoystick = 0.8

dictTeclado = {'a': 'left', 's': 'down', 'd': 'right', 'w': 'up', 97: 'a', 98: 'b', 100: 'l1', 101: 'r1'}
dictMando = {'BTN_SOUTH': 'a', 'BTN_NORTH': 'y', 'BTN_WEST': 'x',
             'BTN_EAST': 'b', 'BTN_TL': 'l1', 'BTN_TR': 'r1'}

dictMandoJoystick = {
'ABS_HAT0X-': 'left', 'ABS_HAT0X+': 'right', 'ABS_HAT0Y+': 'down','ABS_HAT0Y-': 'up',
'ABS_X-' : 'left', 'ABS_X+': 'right', 'ABS_Y+': 'up','ABS_Y-': 'down'
}

joysticksMando = {'ABS_HAT0X','ABS_HAT0Y','ABS_X','ABS_Y'}


pulsada = False
pulsadoMando = -1


def on_press(key):
    global pulsada, dictTeclado
    if not pulsada:
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

# TODO añadir soporte para mantener el joystick/cruceta
def mando():
    global dictMando, pulsadoMando, dictMandoJoystick, sensibilidadJoystick,joysticksMando
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



class Mando(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'mando'

    def run(self):
        mando()


hiloMando = Mando('mando').start()

# with keyboard.Listener(
#         on_press=on_press,
#         on_release=on_release) as listener:
#     listener.join()