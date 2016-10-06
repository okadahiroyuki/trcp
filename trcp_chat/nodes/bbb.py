#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
import rospy
from rospeex_if import ROSpeexInterface

def sr_response(msg):
    print msg
 
def main():
    rospy.init_node('demo')
    interface = ROSpeexInterface()
    interface.init()
#    interface.set_sr_response()
    interface.register_sr_response( sr_response )
    interface.set_spi_config(language='ja', engine='nict')
    rospy.spin()
 
if __name__ == '__main__':
    main()
