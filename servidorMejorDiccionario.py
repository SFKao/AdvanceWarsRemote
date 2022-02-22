import socket
import threading
import queue
from time import sleep

from pynput.keyboard import Key, Controller

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sLocal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
local_address = ('localhost', 65525)
server_address = ('25.85.111.106', 65525)
s.bind(server_address)
sLocal.bind(local_address)

queue = queue.Queue()
keyboard = Controller()

# TODO añadir mantener
dictTeclado = {
    'a': Key.enter,
    'b': Key.shift,
    'left': 'a',
    'down': 's',
    'right': 'd',
    'up': 'w',
    'l1': 'q',
    'r1': 'e'
}


def leer():
    while True:
        data, address = s.recvfrom(4096)
        tecla = data.decode('utf-8')
        global queue
        queue.put(tecla)
        print(tecla)
#TODO añadir que ponga lo que hay que pulsar directamente y que escriba lo contrario
#TODO añadir un hilo que lea del mando y asi ahorrar comunicacion local.

def leerLocal():
    while True:
        data, address = sLocal.recvfrom(4096)
        tecla = data.decode('utf-8')
        global queue
        queue.put(tecla)
        print(tecla)


def escribir():
    while True:
        try:
            tecla = queue.get()
            try:
                tecla = dictTeclado[tecla]
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

class lecturaLocal(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'lectura'

    def run(self):
        leerLocal()


class escritura(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = 'escritura'

    def run(self):
        escribir()


hilo1 = lectura('lectura').start()
hilo2 = escritura('escritura').start()
hiloLocal = lecturaLocal('local').start()






























