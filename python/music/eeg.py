import serial
import time

try:
    port1 = serial.Serial('/dev/ttyACM0', # depends on the COM, we’ll check
                         baudrate=9600)
    port2 = serial.Serial('/dev/ttyACM1', # depends on the COM, we’ll check
                         baudrate=9600)
    #then to send the actual pulse
    port1.write(b'TRG\n')
    port2.write(b'TRG\n')
    port1.close()
    port2.close()

except Exception as e:
    print(f"Error: {e}")


