#!/usr/bin/python
# BeagleBone LED web server
# http://aquaticus.info/beaglebone-web-led
# BeagleBone/Angstrom Linux

import cherrypy
import os.path

from mmap import mmap
import struct

MMAP_OFFSET = 0x44c00000                # base address of registers
MMAP_SIZE   = 0x48ffffff-MMAP_OFFSET    # size of the register memory space

CM_PER_BASE = 0x44e00000 - MMAP_OFFSET
CM_PER_EPWMSS1_CLKCTRL = CM_PER_BASE + 0xcc
CM_PER_EPWMSS0_CLKCTRL = CM_PER_BASE + 0xd4
CM_PER_EPWMSS2_CLKCTRL = CM_PER_BASE + 0xd8

with open("/dev/mem", "r+b") as f:
    mem = mmap(f.fileno(), MMAP_SIZE, offset=MMAP_OFFSET)

def setReg(address, new_value):
    """ Sets 32 bits at given address to given value. """
    mem[address:address+4] = struct.pack("<L", new_value)

def writeDevice(device, value):
    with open(device,"w") as f:
        f.write("%d\n" % int(value))

def pwmSetDutyPercent(dutyPercent):
    """ Sets PWM duty cycle """
    writeDevice("/sys/class/pwm/ehrpwm.1:0/duty_percent", dutyPercent)

def pwmSetFrequency(frequencyHz):
    """Sets PWM duty cycle."""
    writeDevice("/sys/class/pwm/ehrpwm.1:0/period_freq", frequencyHz)

def pwmRun(start):
    """ Starts or Stops PWM. """
    device = "/sys/class/pwm/ehrpwm.1:0/run"
    with open(device,"r") as f:
		s = int(f.read()) #first read current state
		f.close()
		#it is an error if you try run/stop PWM if it's in required state
		if( s != start ):
			writeDevice(device, start)

setReg(CM_PER_EPWMSS1_CLKCTRL, 0x2) #activate PWM clock
writeDevice("/sys/kernel/debug/omap_mux/gpmc_a2", 6) #set mux mode for PWM pin (EHRPWM1:0 it's pin 14 on P9)

freq=10000 #set to maximum LED driver can handle

pwmRun(0) #stop PWM
pwmSetDutyPercent(0) #set to 0 before setting frequency
pwmSetFrequency(freq) #10kHz 
pwmRun(1) #start PWM (duty is 0, so LED is off)

print "PWM Running %d Hz." % freq

class ServerLed(object):
    '''Power ratio in percents. From 0 to 100%'''
    led_power=20 #Initial 20% of power
    '''Switch state 1 (on) or 0 (off)'''
    led_switch=1 #Initial LED on
    
    def index(self, power='', switch=''):
        if power:
            self.led_power = ( int(power) / 20 ) * 20
            print "New power %d%%" % self.led_power
            
        if switch:
            self.led_switch = int(switch)
            print "New switch state %d" % self.led_switch
        
        #read HTML template from file
        html = open('led.html','r').read()

        #replace level bar graph
        level_icon = "level%d.png" % self.led_power
        html = html.replace('level100.png', level_icon)

        #compute duty cycle based on current power ratio and switch status
        if self.led_switch:
            duty = self.led_power
        else:
            duty = 0 #disable

        pwmSetDutyPercent( duty ) #set PWM duty cycle
        
        #replace bulb icon if LED is disabled (off)
        if not self.led_switch:
            html = html.replace('bulb_on.png', 'bulb_off.png')

        return html

    index.exposed = True

#configuration
conf = {
        'global' : { 
            'server.socket_host': '0.0.0.0', #0.0.0.0 or specific IP
            'server.socket_port': 8080 #server port
        },

        '/images': { #images served as static files
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('images')
        },

        '/favicon.ico': {  #favorite icon
            'tools.staticfile.on': True,  
            'tools.staticfile.filename': os.path.abspath("images/bulb.ico")
        }
    }

cherrypy.quickstart(ServerLed(), config=conf)
