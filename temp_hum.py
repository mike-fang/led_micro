import subprocess 
from subprocess import PIPE

def get_th():
    p = subprocess.Popen(['/home/pi/rpi-examples/HTU21D/c/HTU21D_test'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    out = out.decode()
    temp, hum = out.split()
    temp = temp.split('C')[0]
    hum = hum.split('%')[0]
    return float(temp), float(hum)
