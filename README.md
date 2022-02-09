# Ranciliol Silvia Temperature Controller
Temperature controller for a Rancilio Silvia with Bokeh web interface
For use with a Raspberry Pi Zero W

**Hardware:**
* Rancilio Silvia
* Raspberry Pi Zero W
* Thermocouple: https://uk.rs-online.com/web/p/thermocouples/6212287/
* Thermocouple module: https://uk.rs-online.com/web/p/sensor-development-tools/1346476/
* Solid state relay: https://uk.rs-online.com/web/p/solid-state-relays/9225201/


**Usage:**
```
bokeh serve --allow-websocket-origin=192.168.50.101:5006 configuration.py &
python3 control_asyncio.py
```
Where the IP address of the Raspberry Pi is _192.168.50.101_

Go to _192.168.50.101/temp.html_ to see a plot of temperature against time. This is not live and needs refreshed in your browser to update. The html file updates periodically according _plot_timer_ in _control_asyncio.py_

Go to _192.168.50.101:5006/configuration_ to change the temperature set point and PID gains
