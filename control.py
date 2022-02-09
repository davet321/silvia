#!/usr/bin/env python3

import RPi.GPIO as GPIO
from DesignSpark.Pmod.HAT import createPmod
import time
import os
from bokeh.plotting import figure, show, output_file


def create_config():
    default_tset = '95'
    default_kP = '12'
    default_kI = '0.1'
    default_kD = '195'
    if not os.path.isfile('control.conf'):
        with open('control.conf', 'w') as f:
            f.write('%s,%s,%s,%s' % (default_tset,
                                     default_kP,
                                     default_kI,
                                     default_kD))


def read_config():
    with open('control.conf', 'r') as f:
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


if __name__ == '__main__':
    # Set the target time step
    dtt = 0.5
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
        create_config()
        # Initialise variables that get carried over
        dt = dtt
        errz = 0
        yI = 0
        temp_rawz = therm.readCelcius()
        tempz = temp_rawz
        plot_timer = 0
        # Initialise lists for Bokeh plot
        time_plot = [0]
        temp_plot = [temp_rawz]
        temp_raw_plot = [temp_rawz]
        tset_plot = [0]
        output_file('tmp/temp.html')
        # Start time
        t0 = tz = time.time()
        while True:
            tset, kP, kI, kD = read_config()
            t = time.time()
            dt = t - tz
            plot_timer += dt
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
            while time.time() - t <= dtt:
                time.sleep(0.01)

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

            # Prepare lists for plotting
            time_plot.append(t - t0)
            temp_plot.append(temp)
            temp_raw_plot.append(temp_raw)
            tset_plot.append(tset)
            # Trim the start of the list if they're too long (>1 hour)
            if max(time_plot) - min(time_plot) >= 3600:
                time_plot.pop(0)
                temp_plot.pop(0)
                temp_raw_plot.pop(0)
                tset_plot.pop(0)

            if plot_timer > 10:
                p = figure(title='Thermocouple Temperature (deg C)',
                           x_axis_label='time', y_axis_label='Temp.')
                p.line(time_plot, temp_plot, line_width=2)
                p.line(time_plot, temp_raw_plot, line_width=2, line_color='red')
                p.line(time_plot, tset_plot, line_dash='4 4', line_width=1, color='green')
                show(p)
                plot_timer = 0

    except KeyboardInterrupt:
        pass
    finally:
        pwm.stop()
        GPIO.cleanup()
        therm.cleanup()
