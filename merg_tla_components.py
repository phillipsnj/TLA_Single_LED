from machine import Pin, PWM
from time import sleep
import json

class tla_servo:
    def __init__(self, servo_pin, servo_position, *args, **kwargs):
        #self.servo_pin = servo_pin
        self.servo_position = servo_position
        self.servoPin = PWM(Pin(servo_pin))
        self.servoPin.freq(50)
        self.position(self.servo_position)
        
    def position(self, degrees):
        if degrees == 0:
            self.servoPin.duty_u16(0)
        else:
            if degrees > 135: degrees=135
            if degrees < 45: degrees=45
            maxDuty=7000
            minDuty=3000
            newDuty=minDuty+(maxDuty-minDuty)*(degrees/180)
            # servoPin.duty_u16(int(newDuty))
            self.servoPin.duty_u16(degrees*50)
            self.servo_position = degrees
            
class tla_led:
    def __init__(self, led_pin, *args, **kwargs):
        self.led = PWM(Pin(led_pin))
        self.led.freq(50)
        
    def position(self, value):
        self.value = value
        if self.value > 10: self.value = 10
        if self.value <0 : self.value = 0
        self.value = (64000*self.value*self.value/100)
        self.led.duty_u16(int(self.value))

class tla_turnout(tla_servo):
    def __init__(self, servo_pin, position, status_pin, status):
        super().__init__(servo_pin, position)
        self.turnout_position = position
        self.turnout_indicator = Pin(status_pin, Pin.OUT)
        self.status = status # ON or OFF
        if self.status == 'ON':
            self.turnout_indicator.value(1)
        else:
            self.turnout_indicator.value(0)
                
    def move_turnout(self, start, end):
        half_point = 0
        output = 0
        print("Move Servo - Start : "+str(start)+" end : "+str(end))
        #servo_count = 0
        if start < end:
            movement =1
            half_point = int(end - (end - start)/2)
            output = 0
            #self.turnout_indicator.value(0)
        else:
            movement=-1
            half_point = int(start - (start - end)/2)
            output = 1
            #self.turnout_indicator.value(1)
        #uart.write(str.encode("STS=UnKnown\n"))
        print(f"Half Point : {half_point} : {output}")
        for degree in range(start,end,movement):
            self.position(degree)
            if degree == half_point:
                print("Indicator")
                self.turnout_indicator.value(output)
            #if degree == switchPos:
            #    led_external.toggle()
            #if servo_count == 20:
            #    uart.write(str.encode("POS~"+str(degree)+"\n"))
            #    servo_count = 0
            #data['channel_data'][data['channel']]['position']=degree
            sleep(0.1)
            #servo_count +=1
        sleep(0.02)
