#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
import sys
import rospy
from std_msgs.msg import String
from jsk_gui_msgs.msg import VoiceMessage
from jsk_gui_msgs.msg import Tablet

def callback(data):
    print len(data.texts)
    for elem in data.texts:
        print elem
    print "#####"
    print data.texts[0]
    
def listener():

    # in ROS, nodes are unique named. If two nodes with the same
    # node are launched, the previous one is kicked off. The 
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaenously.
    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("/Tablet/voice", VoiceMessage, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

        
if __name__ == '__main__':
    listener()
