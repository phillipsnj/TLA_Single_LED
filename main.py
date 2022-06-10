import os
import gc
from machine import Pin, PWM, UART
from time import sleep
import json
from merg_tla_components import tla_led, tla_servo

config_file = 'data.json'

with open(config_file) as f:
    data = json.load(f)
print(data)

gc.enable()

uart = UART(0, baudrate = 9600)
print("UART Info : ", uart)
sleep(1)

led_onboard = tla_led(25)
led_onboard.position(0)
led_external1 = tla_led(19)
led_external1.position(100)

# led_green = tla_led(6)
# led_green.position(2)
# led_amber = tla_led(7)
# led_amber.position(5)
# led_red = tla_led(8)
# led_red.position(100)

button = Pin(data['button_port'], Pin.IN, Pin.PULL_UP)
button_status = button.value()

test_servo = tla_servo(5, 46)

led_port = tla_led(data['led_port'])

def save_config():
    #print("Start Save")
    with open(config_file, 'w') as f:
        json.dump(data, f)
    #f.close()
    print("Saved")


def uart_send(text):
    led_onboard.position(100)
    uart.write(str.encode(text+"\n"))
    sleep(0.01)
    led_onboard.position(0)

def update_status(status):
    if status == "On":
        data['status'] = "ON"
        uart_send("STS~" + data['status'])
        led_port.position(data['brightness'])
        print(f"Status ON")
    else:
        data['status'] = "OFF"
        uart_send("STS~" + data['status'])
        led_port.position(0)
        print(f"Status OFF")


def INF(operator, value):
    uart_send("ONM")
    uart_send("OFM")
    uart_send("DES~" + data['description'])
    uart_send("VER~" + data['version'])
    uart_send("TAG~" + data['TAG'])
    uart_send("TYP~" + data['type'])
    uart_send("STS%" + data['status'])
    uart_send("BRT=" + str(data['brightness']))
    uart_send("ONM:CNM=ON")
    uart_send("OFM:CNM=OFF")
    uart_send("STS:CNM=Status")
    uart_send("STS:OPT=On")
    uart_send("STS:OPT=Off")

def STS(operator, value):
    if operator == "=":
        update_status(value)

def ONM(operator, value):
    update_status("On")

def OFM(operator, value):
    update_status("Off")

def BRT(operator, value):
    if operator == "+":
        if data['brightness'] < 10:
            data['brightness'] += 1
    else:
        if data['brightness'] > 0:
            data['brightness'] -= 1
    update_status("On")
    # data['status'] = "ON"
    uart_send("STS~" + data['status'])
    uart_send("BRT=" + str(data['brightness']))
    led_port.position(data['brightness'])

def process_input(info):
    led_onboard.position(100)
    TLA = info[0][:3]
    operator = info[0][3:4]
    value = info[0][4:]
    print("Processing : "+TLA+" : "+operator+" -> "+value)
    tla_actions ={
        "INF":INF,
        "STS":STS,
        "BRT":BRT,
        "ONM":ONM,
        "OFM":OFM
    }
    if TLA in tla_actions :
        tla_actions[TLA](operator, value)
    else:
        print(f"Unknown TLA : {TLA}")
    led_onboard.position(0)

gc.collect()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
buffer = ""

print("Move Servo")
test_servo.move_position_fine(45, 130)
sleep(1)
test_servo.move_position_fine(130, 45)
print("Moved Servo")

while True:
    if button_status != button.value():
        print("Button Pressed :"+str(button.value()))
        button_status = button.value()
        if button.value() == 0:
            update_status("Off")
        else:
            update_status("On")

    if uart.any() > 0 :
        input = uart.read(1)
        #info = input.split(',')
        print("RAW Input : "+str(input))
        if input == b'\r':
            info = buffer.split(',')
            process_input(info)
            buffer = ""
            #print("LINE FEED + "+str(info))
        elif input == b'\n':
            None
        else :
            buffer = buffer+input.decode()
    sleep(0.01)


#servo = tla_servo(16, 70)

#servo.position(50)
#sleep(2)
#servo.position(100)
#sleep(2)
#servo.position(0)

# turnout = tla_turnout(16,70, 18,"ON")
#
# turnout.move_turnout(50,100)
# sleep(2)
# turnout.move_turnout(100,50)
# sleep(2)


# for test in range (0,100,+5):
#     led_external1.position(test)
#     print(f"Position : {test}")
#     sleep(0.2)