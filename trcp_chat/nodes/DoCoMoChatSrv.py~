#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
"""
    DoCoMoChatSrv.py


    The project is hosted on GitHub where your could fork the project or report
    issues. Visit https://github.com/roboworks/

    :copyright: (c) 2015 by Hiroyuki Okada, All rights reserved.
    :license: MIT License (MIT), http://www.opensource.org/licenses/MIT
"""
import sys
import time
sys.path.append(".")

import rospy
from std_msgs.msg import String
from okada.msg import DoCoMoChatRes
from okada.msg import DoCoMoChatReq
from okada.srv import DoCoMoChat
from okada.srv import DoCoMoChatResponse
import urllib2
import urllib
import json

class DoCoMoChatSrv(object):
    """ DoCoMoChatSrv class """
    def __init__(self):
        """ Initializer """

    def run(self):
        """ run ros node """
        # initialize ros node
        rospy.init_node('DocomoChatSrv')
        rospy.loginfo("start DoCoMoChatSrv node")

        service_server = rospy.Service('docomo_chat', DoCoMoChat, self.Chat_handler)
        rospy.loginfo("start DoCoMoChat service server")

        self.url = rospy.get_param("~chat_url", "https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue")
        self.APIKEY = rospy.get_param("~APIKEY", "4e4e61744672324d792f533965647867467767654978717445316a3337696430386b453371715246456238")

        self.api_url = self.url + '?APIKEY=%s'%(self.APIKEY)

        
        rospy.spin()

    def Chat_handler(self,  query):
        rospy.loginfo("DoCoMoChatSrv Querry :%s", query)
        req = query.request
        if req.utt == '':
            return DoCoMoChatResponse(success=False)        

        req_data ={}
        req_data['utt'] = req.utt
        req_data['context'] = req.context
        req_data['nickname'] = req.nickname
        req_data['nickname_y'] = req.nickname_y
        req_data['sex'] = req.sex
        req_data['bloodtype'] = req.bloodtype
        req_data['birthdateY'] = req.birthdateY
        req_data['birthdateM'] = req.birthdateM
        req_data['birthdateD'] = req.birthdateD
        req_data['age'] = req.age
        req_data['constellations'] = req.constellations
        req_data['place'] = req.place
        req_data['mode'] = req.mode
        req_data['t'] = req.t

        req = urllib2.Request(self.api_url, json.dumps(req_data))
        req.add_header('Content-Type', 'application/json')
        try:
            res = urllib2.urlopen(req)
        except Exception as e:
            print e
            return DoCoMoChatResponse(success=False)

        resp_json = json.load(res)
        res = DoCoMoChatRes()

        res.utt = resp_json['utt'].encode('utf-8')
        res.yomi = resp_json['yomi'].encode('utf-8')
        res.mode = resp_json['mode'].encode('utf-8')
        res.da = int(resp_json['da'])
        res.context = resp_json['context'].encode('utf-8')

        rospy.loginfo("DoCoMoChatSrv Querry :%s", res.utt)
        return DoCoMoChatResponse(success=True, response=res)

        
if __name__ == '__main__':
    try:
        node = DoCoMoChatSrv()
        node.run()
    except rospy.ROSInterruptException:
        pass
