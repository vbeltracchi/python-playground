# Traffic Light Simulator
# This module draws a small traffic light using tLig, and switches
# The lights once, in a red-amber-green fashion.
# Very simple solution, can be heavily optimised.
#
# Vittorio Beltracchi - 2015

import time
from Tkinter import *

tLig = Tk()
sig = Canvas(tLig, width=105, height=300)
sig.pack()

# functions


def red(a):
    for i in range(a):
        red = sig.create_oval(5, 5, 100, 100, fill="red")
        tLig.update()
        time.sleep(0.05)


def redb(a):
    for i in range(a):
        red = sig.create_oval(5, 5, 100, 100, fill="black")
        tLig.update()
        time.sleep(0.05)


def amber(a):
    for i in range(a):
        amber = sig.create_oval(5, 105, 100, 200, fill="orange")
        tLig.update()
        time.sleep(0.05)


def amberb(a):
    for i in range(a):
        amber = sig.create_oval(5, 105, 100, 200, fill="black")
        tLig.update()
        time.sleep(0.05)


def green(a):
    for i in range(a):
        green = sig.create_oval(5, 205, 100, 300, fill="green")
        tLig.update()
        time.sleep(0.05)


def greenb(a):
    for i in range(a):
        green = sig.create_oval(5, 205, 100, 300, fill="black")
        tLig.update()
        time.sleep(0.05)


def lights():
    red = sig.create_oval(5, 5, 100, 100, fill="black")
    amber = sig.create_oval(5, 105, 100, 200, fill="black")
    green = sig.create_oval(5, 205, 100, 300, fill="black")

# end of functions
# calling the functions

lights()
red(30)
redb(1)
amber(10)
amberb(1)
green(30)
greenb(1)

tLig.mainloop()
