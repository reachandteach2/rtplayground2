# rtplayground2
This is code written in CircuitPython to make it easy to do experiments with Adafruit's Circuit Playground Express without having to write a program.

WHY DOES THIS PROJECT EXIST?
Sometimes you just want to throw together something quickly that requires the power of a processor but you don't want to find a laptop with your development environment on it and don't really want to write any code. You just want to directly jump to tinkering. I don't pretend to say that this replaces anything close to all the reasons you need to write code, but it does provide enough functionality that if you have a Circuit Playground Express and some sort of electronics kit (like a Tronex or Snap Circuit kit) and maybe a servo and a handful of K'nex or popsicle sticks, cardboard, and glue, you can do some really fun things.

WHAT ARE THE FILES IN THIS PROJECT:

boot.py -- makes it possible for python to release the file system when the Circuit Playground Switch so that pgm.txt can be updated (based on a switch setting)

pgm.txt -- default program loaded when the Circuit Playground Express is powered up or reset

code.py -- the RTPlayground2.py code

All 3 of these files need to be transfered to the Circuit Playground Express (which should already be loaded with updated versions of CircuitPython and library modules adafruit_motor, simpleio.mpy, and neopixel.mpy)

WHAT DOES THIS DO?

After downloading this code into a Circuit Playground which has CircuitPython loaded on it, you can select 5 built-in functions:
Pgm 0: Neopixel display (with servo and motor output) output on A0, servo output on A2
Pgm 1: Sound/IR remote activated output on A0, servo output on A2
Pgm 2: Light activated servo/motor output on A0, servo output on A2
Pgm 3: Variable voltage control servo/motor output on A0, servo output on A2, analog input on A1 (0 to 3.3V)
Pgm 4: Color card activated servo/motor output on A0, servo output on A2

To select the software function:
Move slide switch to the right (towards pad A1)
Click reset button once, one of the green LEDs on the left side should be lit
Repeatedly click the Left button (Button A) to change which LED is lit (and the software function selected) in the order 0, 1, 2, 3, 4
Move slide switch to the left (towards pad A6) to start the software function

The speed/delay of functions 0, 1, and 2 can be set by pressing the Right button (Button B) while the software function is running (not while selecting the software function)
