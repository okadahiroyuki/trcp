#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
"""
    Chat program

    ROSPEEXから
    入力された文章を使い、DoCoMoAPIで会話する

    The project is hosted on GitHub where your could fork the project or report
    issues. Visit https://github.com/roboworks/

    :copyright: (c) 2015 by Hiroyuki Okada, All rights reserved.
    :license: MIT License (MIT), http://www.opensource.org/licenses/MIT
"""
__author__ = 'Hiroyuki Okada'
__version__ = '0.1'
import sys
import string
import time
import datetime
import re
sys.path.append(".")
import urllib2
import urllib
import json
import rospy
from std_msgs.msg import String

# rospeex
from rospeex_if import ROSpeexInterface

# jsk
from jsk_gui_msgs.msg import VoiceMessage
from jsk_gui_msgs.msg import Tablet

from trcp_chat.srv import *
from trcp_chat.msg import *

_chat_={
    "utt":"",
    "context":"aaabbbccc111222333",
    "nickname":"あかね",
    "nickname_y":"アカネ",
    "sex":"女",
    "bloodtype":"O",
    "birthdateY":1990,
    "birthdateM":2,
    "birthdateD":5,
    "age":25,
    "constellations":"水瓶",
    "place":"大阪",
    "mode":"dialog",
    "t":"20"
}

_nowmode = "CHAT"

class ChatTRCP(object):
    """ ChatTRCP class """
    def __init__(self):
        """ Initializer """

    def run(self):
        """ run ros node """
        # initialize ros node
        rospy.init_node('ChatTRCP')
        rospy.loginfo("start DoCoMo Chat TRCP node")

        """ for ROSpeexInterface """
        self.rospeex = ROSpeexInterface()
        self.rospeex.init()
        self.rospeex.register_sr_response( self.sr_response )
        self.rospeex.set_spi_config(language='ja', engine='nict')

        """日本語（英語もある）でNICT(Googleもある)"""
        """launchファイ決めてもいいけど、動的に変更する？"""
        """とりあえず、現状は決め打ち"""
        self.lang = 'ja'
        self.input_engine = 'nict'        
        self.rospeex.set_spi_config(language='ja',engine='nict')

        """ for jsk voice understanding """
        rospy.Subscriber("/Tablet/voice", VoiceMessage, self.jsk_voice)

        """ 発話理解APIの準備 """
        self.req = DoCoMoUnderstandingReq()
        self.req.projectKey = 'OSU'    
        self.req.appName = ''
        self.req.appKey = 'hoge_app01'
        self.req.clientVer = '1.0.0'
        self.req.dialogMode = 'off'
        self.req.language = 'ja'
        self.req.userId = '12 123456 123456 0'
        self.req.lat = '139.766084'
        self.req.lon = '35.681382'

        """ 雑談対話APIの準備 """
        self.req_chat = DoCoMoChatReq()
        self.req_chat.utt = ""

        self.req_chat.context = _chat_["context"]
        self.req_chat.nickname = _chat_["nickname"]
        self.req_chat.nickname_y = _chat_["nickname_y"]
        self.req_chat.sex = _chat_["sex"]
        self.req_chat.bloodtype = _chat_["bloodtype"]
        self.req_chat.birthdateY = _chat_["birthdateY"]
        self.req_chat.birthdateM = _chat_["birthdateM"]
        self.req_chat.birthdateD = _chat_["birthdateD"]
        self.req_chat.age = _chat_["age"]
        self.req_chat.constellations = _chat_["constellations"]
        self.req_chat.place = _chat_["place"]
        self.req_chat.mode = _chat_["mode"]
        self.req_chat.t = _chat_["t"]


        rospy.wait_for_service('docomo_sentenceunderstanding')
        self.understanding = rospy.ServiceProxy('docomo_sentenceunderstanding',DoCoMoUnderstanding)

        rospy.wait_for_service('docomo_qa')        
        self.qa = rospy.ServiceProxy('docomo_qa',DoCoMoQa)

        rospy.wait_for_service('docomo_chat')        
        self.chat = rospy.ServiceProxy('docomo_chat',DoCoMoChat)

        self.resp_understanding = DoCoMoUnderstandingRes()
        
        _nowmode = "CHAT"

        rospy.spin()

    def jsk_voice(self,data):
#        print len(data.texts)
#        for elem in data.texts:
#            print elem
        rospy.loginfo("jsk_voice:%s", data.texts[0])
        self.chat(data.texts[0])

    def sr_response(self, message):
        # Rospeexを使うと、文字列の最後に「。」が付くので削除する
        src = message
        sr_dst=src.replace('。', '')
        rospy.loginfo("rospeex:%s", sr_dst)
        chat(sr_dst)




    def chat(self, message):
        rospy.loginfo("chat:%s", message)

        #message が特定のキーワードであれば、それに対応した処理を行う
        """ 時間 ->現在時刻を答える"""
        time = re.compile('(?P<time>何時)').search(message)
        if time is not None:
            rospy.loginfo("What Time is it now? :%s", message)        
            d = datetime.datetime.today()
            text = u'%d時%d分です。'%(d.hour, d.minute)
            # rospeex reply
            self.rospeex.say(text, 'ja', 'nict')
            return True

        # 特定のキーワード処理はここまで

        print _nowmode
        try:
            """ もし現在の会話モードが「しりとり」なら
                文章理解APIをスキップする

                それ以外なら、文章理解APIで文章を解析する
            """
            if _nowmode == "CHAIN":
                self.resp_understanding.success = True
                self.resp_understanding.response.commandId = "BC00101"
                self.resp_understanding.response.utteranceText = message
            else:
                self.req.utteranceText = message
                self.resp_understanding = self.understanding(self.req)

            if  self.resp_understanding.success:
                commandId = self.resp_understanding.response.commandId
                rospy.loginfo("<<< %s", commandId)
                if commandId == "BC00101":
                    """雑談"""
                    rospy.loginfo("TRCP:Chat")
                    self.res_chat = self.chat(self.req_chat)
                    rospy.loginfo("TRCP Chat response:%s",self.res_chat.response)

                elif commandId  == "BK00101":
                    """知識検索"""
                    rospy.loginfo("TRCP:Q&A")
                    self.req_qa = DoCoMoQaReq()
                    self.req_qa.text = self.resp_understanding.response.utteranceText
                    print self.resp_understanding.response.utteranceText
                    res_qa = self.qa(self.req_qa)
                    rospy.loginfo("TRCP Q&A response:%s",res_qa.response.code)
                    self.rospeex.say(res_qa.response.textForSpeech , 'ja', 'nict')



            else:
                """発話理解APIがエラーのとき"""
                rospy.loginfo("DoCoMo 発話理解API failed")
                pass

        except:
            """対話プログラムのどこかでエラーのとき"""
            rospy.loginfo("error")
            pass

        return True




            
if __name__ == '__main__':
    try:
        node = ChatTRCP()
        node.run()
    except rospy.ROSInterruptException:
        pass
