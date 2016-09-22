#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Microsoft translator API

    An example::

 
    The project is hosted on GitHub where your could fork the project or report
    issues. Visit https://github.com/****************

    :copyright: © 2015 by Hiroyuki Okada & Tamagawa University
    :license: BSD, see LICENSE for more details.
"""
import hsrb_interface
import rospy
import sys
from hsrb_interface import geometry

# 移動のタイムアウト[s]
_MOVE_TIMEOUT=60.0

# ロボット機能を使うための準備
robot = hsrb_interface.Robot()
omni_base = robot.get('omni_base')
whole_body = robot.get('whole_body')
gripper = robot.get('gripper')
tts = robot.get('default', robot.Items.TEXT_TO_SPEECH)

# handを0.1[m]上に移動させる姿勢
hand_up = geometry.pose(x=0.1)

# handを0.5[m]手前に移動させる姿勢
hand_back = geometry.pose(z=-0.5)

def hello(msg):
    """
    こんにちわ。
    
    :param string msg: 出力するメッセージ
    """
    print msg

def add(a, b):
    """
    足し算ぐらいできます。
    
    :param int a: 足される値。
    :param int b: 足す値。
    :rtype: int
    :return: 足し算した数値。
    :todo: sample.py/def add - 例外出たときどうするんだろ。誰か直しといて。
    """
    return a + b

if __name__=='__main__':

    # まずは一言
   # rospy.sleep(5.0)
   # tts.say('こんにちはHSRだよ。これから部屋の中を移動するよ。')
   # rospy.sleep(5.0)
   print 10
   pos = whole_body.joint_positions
   print pos
   whole_body.move_to_joint_positions({'arm_lift_joint': 0.2})

   whole_body.move_to_joint_positions({'head_pan_joint': 0.4, 'head_tilt_joint': -0.2})
   omni_base.go(0.0, 0.0, 1.0, 50.0, relative=True)
   print 20
   omni_base.go(0.5, 0.0, 0.0, 50.0, relative=True)
