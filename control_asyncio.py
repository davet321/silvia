#!/usr/bin/env python3

import RPi.GPIO as GPIO
from DesignSpark.Pmod.HAT import createPmod
import time
import os
from bokeh.plotting import figure, show, output_file
from bokeh.models import CustomJS, Slider
# from bokeh.io import show as showio
from bokeh.layouts import column
import asyncio
from datetime import datetime


def create_config():
    default_tset = '94'
    default_kP = '12'
    default_kI = '0.1'
    default_kD = '200'
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


def fof(a, b, c, d, x, xz, yz, T):
    # First order filter. (as+b)/(cs+d)
    y = ((2*a + T*b)*x + (-2*a+T*b)*xz + (2*c-T*d)*yz) / (2*c + T*d)
    return y

def secs_since_midnight():
    now = datetime.now()
    seconds_since_midnight = (now - now.replace(hour=0,
                                                minute=0,
                                                second=0,
                                                microsecond=0)).total_seconds()
    return seconds_since_midnight


async def control():
    create_config()
    # Initialise variables that get carried over
    dtt = 0.5
    dt = dtt
    errz = 0
    yI = 0
    temp_rawz = therm.readCelcius()
    tempz = temp_rawz
    # Start time
    t0 = tz = time.time()

    while True:
        tset, kP, kI, kD = read_config()
        t = time.time()
        dt = t - tz
        temp_raw = therm.readCelcius()
        temp = fof(0, 1, 2, 1, temp_raw, temp_rawz, tempz, dt)
        temp_rawz = temp_raw
        err = tset - temp

        # err -> PID -> y
        yP = err
        yI += err * dt
        yD = (err - errz) / dt
        y = (kP * yP) + (kI * yI) + (kD * yD)

        # Anti windup
        if y >= 100 and yI >= 0:
            yI -= (err * dt)
        elif y <= 0 and yI <= 0:
            yI -= (err * dt)

        if abs(err) > 5:
            yI = 0

        y = max(0, min(100, y))

        # Wait until the target time step has passed
        await asyncio.sleep(dtt)

        pwm.ChangeDutyCycle(y)
        print('time:', round(t - t0, 2), ' temp:', round(temp, 2),
              ' err:', round(err, 2), ' pwm:', round(y, 2))
        print('P:', round(kP * yP, 2),
              ' I:', round(kI * yI, 2),
              'D:', round(kD * yD, 2))
        print(' ')
        tz = t
        errz = err
        tempz = temp


async def plotting():
    # Initialise lists
    time_plot = [secs_since_midnight()]
    temp_plot = [therm.readCelcius()]
    tset_plot = [100]

    output_file('tmp/temp.html')

    # Start timer at 10 so we get a plot on first iteration
    plot_timer = 10

    while True:
        await asyncio.sleep(1)
        tset, kP, kI, kD = read_config()
        # Append lists with current values
        time_plot.append(secs_since_midnight())
        temp_plot.append(therm.readCelcius())
        tset_plot.append(tset)

        if len(time_plot) >= 600:
            time_plot.pop(0)
            temp_plot.pop(0)
            tset_plot.pop(0)

        t0 = time.time()

        if plot_timer >= 10:
            p = figure(title='Thermocouple Temperature (deg C)',
                       x_axis_label='time', y_axis_label='Temp.')
            p.line(time_plot, temp_plot, line_width=2, color='red')
            p.line(time_plot, tset_plot, line_dash='4 4', line_width=1, color='green')
            show(p)
            plot_timer = 0
        else:
            plot_timer += 1


if __name__ == '__main__':
    # Set up GPIO output and PWM
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.OUT)
    # Set 20Hz frequency and initialise with 0% duty cycle (off)
    pwm = GPIO.PWM(12, 20)
    pwm.start(0)
    # Initialise thermocouple amplifier
    therm = createPmod('TC1', 'JBA')
    time.sleep(0.1)
    try:
        loop = asyncio.get_event_loop()
        cors = asyncio.wait([control(), plotting()])
        loop.run_until_complete(cors)
    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        GPIO.cleanup()
        therm.cleanup()
