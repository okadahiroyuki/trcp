#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
"""
    DoCoMoScenario.py

    Service Server for DoCoMo Scenario API

    The project is hosted on GitHub where your could fork the project or report
    issues. Visit https://github.com/roboworks/

    :copyright: (c) 2015 by Hiroyuki Okada, All rights reserved.
    :license: MIT License (MIT), http://www.opensource.org/licenses/MIT
"""
__author__ = 'Hiroyuki Okada'
__version__ = '0.1'
import sys
import time
sys.path.append(".")
import urllib2
import urllib
import json
import rospy
from std_msgs.msg import String

from okada.msg import DoCoMoScenarioReq
from okada.msg import DoCoMoScenarioRes

from okada.srv import DoCoMoScenario
from okada.srv import DoCoMoScenarioResponse


class DoCoMoScenarioSrv(object):
    """ DoCoMoScenarioSrv class """
    def __init__(self):
        """ Initializer """

    def run(self):
        """ run ros node """
        # initialize ros node
        rospy.init_node('DocomoScenarioSrv')
        rospy.loginfo("start DoCoMoScnarioSrv node")
        service_server = rospy.Service('docomo_scenario', DoCoMoScenario, self.Scenario_handler)
        rospy.loginfo("start DoCoMoScenario service server")

        self.APIKEY = rospy.get_param("~APIKEY", "4e4e61744672324d792f533965647867467767654978717445316a3337696430386b453371715246456238")
        # get scenario APP ID
        self.APP_URL = rospy.get_param("~scenario_url","https://api.apigw.smt.docomo.ne.jp/scenarioDialogue/v1/registration")
        self.api_url = self.APP_URL + '?APIKEY=%s'%(self.APIKEY)

        self.req_data = {'botId': 'APIBot'}
        self.request = urllib2.Request(self.api_url, json.dumps(self.req_data))
        self.request.add_header('Content-Type', 'application/json')
        try:
            self.response = urllib2.urlopen(self.request)
        except Exception as e:
            print e
            return DoCoMoScenarioResponse(success=False)
        self.resp_json = json.load(self.response)
#        self.app_id = self.resp_json['app_id'].encode('utf-8')
#        rospy.loginfo("DoCoMoScenario:%s", self.app_id)
       
        self.urlS = rospy.get_param("~scenario_url", "https://api.apigw.smt.docomo.ne.jp/scenarioDialogue/v1/dialogue")
        
        self.api_urlS = self.urlS + '?APIKEY=%s'%(self.APIKEY)
        self.appId, self.botId = '5pB2Nv_6FQtIh8OIjVCfztSZNIlpzZZV','APIBot'

        self.initTalkingFlag, self.initTopicId = 'true', 'APITOPIC'
        
        rospy.spin()        


    def Scenario_handler(self, query):
        rospy.loginfo("DoCoMoScenario Query:%s", query)
        req = query.request
        self.req_data = {} 
        self.req_data['voiceText'] = req.voiceText
#        self.req_data['appId'] = self.appId
        self.req_data['botId'] = 'APIBot'
#        self.req_data['initTalkingFlag'] = req.initTalkingFlag
#        self.req_data['initTopicId'] = 'APITOPIC'
        self.req_data['appRecvTime'] = '2015-10-30 21:21:16'
        self.req_data['appSendTime'] = '2015-10-30 21:21:16'
        self.request = urllib2.Request(self.api_urlS, json.dumps(self.req_data))
        self.request.add_header('Content-Type', 'application/json')
        try:
            self.response = urllib2.urlopen(self.request)
        except Exception as e:
            print e
            return DoCoMoScenarioResponse(success=False)

        self.the_page = json.loads(self.response.read())
        res = DoCoMoScenarioRes()
        self.sys = self.the_page['systemText']
        res.expression =  self.sys['expression'].encode('utf-8')
        res.utterance =  self.sys['utterance'].encode('utf-8')        
        res.serverSendTime = self.the_page['serverSendTime']
        return DoCoMoScenarioResponse(success=True, response=res)

        
if __name__ == '__main__':
    try:
        node = DoCoMoScenarioSrv()
        node.run()
    except rospy.ROSInterruptException:
        pass
