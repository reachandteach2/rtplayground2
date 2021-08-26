# rtplayground2.py by derrick @ reachandteach.com
# Creative Commons License Attribution-ShareAlike CC BY-SA
import time
import array
import board
import math
import pwmio
import analogio
import digitalio
from adafruit_motor import servo
import neopixel
import audiobusio
import simpleio

# get default/starting program command (0 - 9)
fp= open('pgm.txt','r')
try:
    cmd= int(fp.read())
except:
    cmd= 0
if (cmd<0 or cmd>9) :
    cmd= 0
fp.close()


#neopixels
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=True)

#red led
red_led = digitalio.DigitalInOut(board.LED)
red_led.switch_to_output()
red_led.value= False

#analog out for ext control/motor
motor= analogio.AnalogOut(board.A0)
motor.value= 0


#buttons and switches
button_a = digitalio.DigitalInOut(board.BUTTON_A)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.DOWN

button_b = digitalio.DigitalInOut(board.BUTTON_B)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.DOWN

switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# create a PWMOut object
pwm = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm)

# ext in
extIn = analogio.AnalogIn(board.A1)

# ir detector
irRX = digitalio.DigitalInOut(board.IR_RX)
irRX.direction = digitalio.Direction.INPUT

# mic
mic = audiobusio.PDMIn(
    board.MICROPHONE_CLOCK,
    board.MICROPHONE_DATA,
    sample_rate=16000,
    bit_depth=16
)
samples = array.array('H', [0] * 32)
lastmagnitude = 0

#light detector
light = analogio.AnalogIn(board.LIGHT)

#init stuff
buttona = False
buttonb = False
buttonPress = 0
operationMode= switch.value # operation mode vs configuration mode
enterOperationMode = True # 1st time operation mode, initialize
cycle= True # cycle toggles between false and true
firstCycle= True

# test if buttons are pressed
def pollButton() :
    global buttona, buttonb, parm, operationMode
    retButton= 0
    if (not buttona and button_a.value) :
        retButton= retButton+1
        buttona= True
        time.sleep(0.2)
    else:
        buttona= False

    if (not buttonb and button_b.value):
        retButton= retButton+2
        buttonb= True
        time.sleep(0.2)
    else:
        buttonb= False
    if (operationMode and retButton == 2):
        parm = (parm+1) % 3
    return retButton

def sleepTimer(delay) :
    global buttonPress
    if delay>0.3 :
        for i in range(delay*10):
            buttonPress= pollButton()
            time.sleep(0.1)
    else:
        buttonPress= pollButton()
        time.sleep(delay)

def displayCmdMode(cmd):
    for i in range(10):
        if cmd==i :
          pixels[i]= (0,64,0)
        else :
          pixels[i]= (0,0,0)

# neopixel color wheel
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def servo_angle(angle) :
    my_servo.angle = angle
    sleepTimer (0.2)
    my_servo.angle = None

def rainbow_cycle(cycle,nsecs):
    global buttonPress
    pixels.brightness = 0.1
    for j in range(25):
        for i in range(10):
            rc_index = (i * 256 // 10) + j*10
            pixels[i] = wheel(rc_index & 255)
        if buttonPress == 2:
            buttonPress = 0
            pixels.fill((0,0,0))
            time.sleep(0.1)
            break
        else:
            sleepTimer(nsecs/25)

# Mic functions
def mean(values):
    return sum(values) / len(values)

def readMic(mic):
    global lastmagnitude
    mic.record(samples, len(samples))
    magnitude = mean(samples)
    if lastmagnitude==0:
        lastmagnitude= magnitude
    magdiff= magnitude - lastmagnitude
    lastmagnitude= magnitude
    time.sleep(0.02)
    return magdiff

# cmd functions start here
def opt_rainbow(cycle,parm):
    global red_led
    if cycle :
        servo_angle(90)
        motor.value=65535
    else :
        servo_angle(0)
        motor.value= 0
    red_led.value= cycle
    rainbow_cycle(cycle,3+parm*2)

def opt_irsound(cycle,parm):
    global irRX, firstCycle, mic
    if not irRX.value or readMic(mic)>600:
        servo_angle(90)
        motor.value= 65535
        rainbow_cycle(cycle,3+parm*2)
        servo_angle(0)
        motor.value= 0
        pixels.fill((0,0,0))
        firstCycle= False
    if firstCycle:
        sleepTimer(0.1)
    else:
        sleepTimer(0.05)

def opt_lightcontrol(cycle,parm) :
    global firstCycle, lastmagnitude
    magnitude= light.value
    if (magnitude<40000 and lastmagnitude>40000) or firstCycle: # light OFF
        firstCycle= False
        lastmagnitude= magnitude
        servo_angle(0)
        motor.value= 0
        pixels.fill((0,0,0))
        pixels[1]=((0,0,128))
        sleepTimer(0.1)
    elif (magnitude >=40000 and lastmagnitude<40000) or firstCycle: # light ON
        firstCycle= False
        lastmagnitude= magnitude
        servo_angle(90)
        motor.value= 65535
        pixels.fill((128,0,0))
        sleepTimer(0.4+parm*2)
    else:
        sleepTimer(0.1)

def opt_extcontrol(cycle,parm) :
    global lastmagnitude
    m1 = extIn.value
    time.sleep(0.01)
    magnitude= extIn.value
    if (abs(magnitude-m1)<1500):
        s=int(simpleio.map_range(magnitude,0,65535,0,90)+.5)
        motor.value= magnitude
        lastmagnitude= magnitude
    else:
        s=int(simpleio.map_range(lastmagnitude,0,65535,0,90)+.5)
        motor.value= lastmagnitude
    #servo_angle(s)
    my_servo.angle=s
    for i in range(10):
        if (i <= int(s/10+0.5)):
            pixels[i]=((0,0,128))
        else:
            pixels[i]=((0,0,0))
    sleepTimer(0.05)

def opt_readcolor(cycle,parm) :
    global firstCycle, colorRed
    ambient= light.value
    if colorRed and ambient>30000: #go
        pixels.fill((0,128,0))
        colorRed= False
        servo_angle(90)
        motor.value= 65535
    elif not colorRed and ambient>30000: #stop
        pixels.fill((128,0,0))
        colorRed= True
        servo_angle(0)
        motor.value= 0
    time.sleep(0.2)


# on start...
options =   {0: opt_rainbow,
             1: opt_irsound,
             2: opt_lightcontrol,
             3: opt_extcontrol,
             4: opt_readcolor,
}


while True:
    buttonPress= pollButton()
    if operationMode:
        if enterOperationMode: #initialize operation mode on entry
            pixels.fill((0,0,0))
            parm= 0
            enterOperationMode= False
            cycle= True
            firstCycle= True
            red_led.value= False
            lastmagnitude= 0
            if cmd==4:
                colorRed= True
                pixels.fill((128,0,0))

        options[cmd](cycle,parm)
        cycle= not cycle


    else: #config command
        if buttonPress == 1 :
            cmd= (cmd+1)%5
        displayCmdMode(cmd)
        enterOperationMode= switch.value # go into operation mode when switch in left position
        operationMode= switch.value
        if operationMode: #try writing new cmd mode to flash
            try:
                fp= open('pgm.txt','w')
                fp.write(str(cmd))
                fp.close()
            except:
                pass