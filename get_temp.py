#!/usr/bin/env python3
from DesignSpark.Pmod.HAT import createPmod
from time import sleep

therm = createPmod('TC1','JBA')
sleep(0.2)
print(therm.readCelcius())
