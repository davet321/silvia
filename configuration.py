#!/usr/bin/env python3

import os
from bokeh.plotting import curdoc
from bokeh.layouts import column
from bokeh.models import Slider


def create_config():
    default_tset = '95'
    default_kP = '12'
    default_kI = '0.1'
    default_kD = '195'
    if not os.path.isfile('params.conf'):
        with open('params.conf', 'w') as f:
            f.write('%s,%s,%s,%s' % (default_tset,
                                     default_kP,
                                     default_kI,
                                     default_kD))


def read_config():
    with open('params.conf', 'r') as f:
        config = f.readline().split(',')
        tset = float(config[0])
        kP = float(config[1])
        kI = float(config[2])
        kD = float(config[3])
        return tset, kP, kI, kD


def update_tset(attr, old, new):
    tset, kP, kI, kD = read_config()
    tset = new
    with open('params.conf', 'w') as f:
        f.write('%s,%s,%s,%s' % (tset, kP, kI, kD))

def update_kP(attr, old, new):
    tset, kP, kI, kD = read_config()
    kP = new
    with open('params.conf', 'w') as f:
        f.write('%s,%s,%s,%s' % (tset, kP, kI, kD))


def update_kI(attr, old, new):
    tset, kP, kI, kD = read_config()
    kI = new
    with open('params.conf', 'w') as f:
        f.write('%s,%s,%s,%s' % (tset, kP, kI, kD))


def update_kD(attr, old, new):
    tset, kP, kI, kD = read_config()
    kD = new
    with open('params.conf', 'w') as f:
        f.write('%s,%s,%s,%s' % (tset, kP, kI, kD))


create_config()
tset, kP, kI, kD = read_config()

temp_slider = Slider(start=80, end=110, value=tset, step=1,
                     title='Temperature ('+u'\N{DEGREE SIGN}'+'C)')
kP_slider = Slider(start=5, end=25, value=kP, step=1,
                   title='Proportional Gain')
kI_slider = Slider(start=0, end=1, value=kI, step=.05,
                   title='Integral Gain')
kD_slider = Slider(start=50, end=300, value=kD, step=5,
                   title='Derivative Gain')

temp_slider.on_change('value', update_tset)
kP_slider.on_change('value', update_kP)
kI_slider.on_change('value', update_kI)
kD_slider.on_change('value', update_kD)

curdoc().add_root(column(temp_slider, kP_slider, kI_slider, kD_slider))
