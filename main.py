import machine
from machine import Pin
import socket
import network
import time
import json
import os
import sys

from dht11 import DHT11

def file_exists(filename):
    try:
        with open(filename) as _:
            return True
    except:
        return False

led = Pin("LED", Pin.OUT)
button = Pin(0, Pin.IN, Pin.PULL_UP)
sensor_pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(sensor_pin)

for f in ['index.html', 'style.css', 'script.js']:
    if not file_exists(f):
        print(f'Brak pliku: "{f}"')
        sys.exit()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("<SSID>", "<hasło do wifi>")
 
# Wait for connect or fail
wait = 30
while wait > 0:
    led.high()
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('Czekanie na połączenie...')
    time.sleep(1)
    led.low()
 
# Handle connection error
print(wlan.status())
if wlan.status() != 3:
    raise RuntimeError('Połączenie nieudane')
else:
    print('Połączono')
    print('Pliki: ', *os.listdir())
    led.low()
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)

def get_sensor_data():
    sensor.measure()
    temperature = sensor.temperature
    humidity = sensor.humidity

    return {
        'temperature': temperature,
        'humidity': humidity,
    }
 
def webpage():
    if file_exists('index.html'):
        with open('index.html') as f:
            html = f.read()
    else:
        html = 'Brak index.html'
    return html
    

def serve(connection):
    while True:
        if button.value() == 1:
            print('Przerwanie')
            sys.exit()

        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        if request == '/sensor':
            data = get_sensor_data()
            client.send(bytes(json.dumps(data), 'utf-8'))
            client.close()

        elif file_exists(request[1:]):
            with open(request[1:]) as f:
                html = f.read()
            client.send(html)
            client.close()

        else:
            html=webpage()
            client.send(html)
            client.close()
 
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return(connection)

try:
    if ip is not None:
        connection=open_socket(ip)
        serve(connection)
except KeyboardInterrupt:
    machine.reset()