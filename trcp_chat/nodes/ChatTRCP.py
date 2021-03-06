#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
"""
    Chat program

    ROSPEEX あるいは jsk ROS Voice Recognition 
    から入力された文章を使い、DoCoMoAPIで会話する


    The project is hosted on GitHub where your could fork the project or report
    issues. Visit https://github.com/roboworks/

    :copyright: (c) 2015,2016 by Hiroyuki Okada, All rights reserved.
    :license: MIT License (MIT), http://www.opensource.org/licenses/MIT
"""
__author__ = 'Hiroyuki Okada'
__version__ = '0.2'
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

# trcp
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

        self.req.projectKey = rospy.get_param("~req_projectKey", 'OSU')
        self.req.appName = rospy.get_param("~req_appName" ,'')
        self.req.appKey = rospy.get_param("~req_appKey" ,'hoge_app01')
        self.req.clientVer = rospy.get_param("~req_clientVer",  '1.0.0')
        self.req.dialogMode = rospy.get_param("~req_dialogMode",'off')
        self.req.language = rospy.get_param("~req_language", 'ja')
        self.req.userId = rospy.get_param("~req_userId", '12 123456 123456 0')
        self.req.lat = rospy.get_param("~req_lat" , '139.766084')
        self.req.lon = rospy.get_param("~req_lon" , '35.681382')


        """ 雑談対話APIの準備 """
        self.req_chat = DoCoMoChatReq()
        self.req_chat.utt = ""

        self.req_chat.context =  rospy.get_param("~context", "aaabbbccc111222333")
        self.req_chat.nickname = rospy.get_param("~nickname", "ひろゆき")
        self.req_chat.nickname_y = rospy.get_param("~nickname_y", "ヒロユキ")
        self.req_chat.sex = rospy.get_param("~sex", "男")
        self.req_chat.bloodtype = rospy.get_param("~bloodtype", "AB")
        self.req_chat.birthdateY = rospy.get_param("~birthdateY", "1960")
        self.req_chat.birthdateM = rospy.get_param("~birthdateM", "7")
        self.req_chat.birthdateD = rospy.get_param("~birthdateD", "11")
        self.req_chat.age = rospy.get_param("~age", "56")
        self.req_chat.constellations = rospy.get_param("~constellations", "蟹")
        self.req_chat.place = rospy.get_param("~place", "東京")
        self.req_chat.mode = rospy.get_param("~mode", "dialog")
        self.req_chat.t = rospy.get_param("~t", "20")


        """ サービスの起動 """
        rospy.wait_for_service('docomo_sentenceunderstanding')
        self.understanding = rospy.ServiceProxy('docomo_sentenceunderstanding',DoCoMoUnderstanding)

        rospy.wait_for_service('docomo_qa')        
        self.qa = rospy.ServiceProxy('docomo_qa',DoCoMoQa)

        rospy.wait_for_service('docomo_chat')        
        self.chat = rospy.ServiceProxy('docomo_chat',DoCoMoChat)

        self.resp_understanding = DoCoMoUnderstandingRes()
        
        self.nowmode = "CHAT"
        rospy.spin()


    def trcpSay(self, text):
        self.rospeex.say(text, 'ja', 'nict')


    def jsk_voice(self,data):
#        print len(data.texts)
#        for elem in data.texts:
#            print elem
        rospy.loginfo("jsk_voice:%s", data.texts[0])
        self.execTrcpChat(data.texts[0])


    def sr_response(self, message):
        # Rospeexを使うと、文字列の最後に「。」が付くので削除する
        src = message
        sr_dst=src.replace('。', '')
        rospy.loginfo("rospeex:%s", sr_dst)
        self.execTrcpChat(sr_dst)


    """ DoCoMo 知識検索の実行 """
    def execDoCoMoQA(self, message):
        rospy.loginfo("DoCoMo Q&A")
        self.req_qa = DoCoMoQaReq()
        self.req_qa.text = message

        res_qa = self.qa(self.req_qa)
        if res_qa.success:
            # for answer in res_qa.response.answer:
            #     print answer.rank
            #     print answer.answerText
            #     print answer.linkText
            #     print answer.linkUrl
            """
            質問回答のレスポンスコードは、下記のいずれかを返却。
            S020000: 内部のDBからリストアップした回答
            S020001: 知識Q&A APIが計算した回答
            S020010: 外部サイトから抽出した回答候補
            S020011: 外部サイトへのリンクを回答
            E010000: 回答不能(パラメータ不備)
            E020000: 回答不能(結果0件)
            E099999: 回答不能(処理エラー)
            ※Sで始まる場合は正常回答、
            Eで始まる場合は回答が得られていないことを示す。
            """
            rospy.loginfo("DoCoMo Q&A response code:%s",res_qa.response.code)
            if res_qa.response.code == 'S020000':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay(res_qa.response.textForSpeech)
            elif res_qa.response.code == 'S020001':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay(res_qa.response.textForSpeech)
            elif res_qa.response.code == 'S020010':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay(res_qa.response.textForSpeech)
            elif res_qa.response.code == 'S020011':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay(res_qa.response.textForSpeech)
            elif res_qa.response.code == 'E010000':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay("ごめんなさい、答えが見つかりませんでした")
            elif res_qa.response.code == 'E020000':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay("ごめんなさい、答えが見つかりませんでした")
            elif res_qa.response.code == 'E099999':
                rospy.loginfo("DoCoMo Q&A response:%s",res_qa.response.textForDisplay)
                self.trcpSay("ごめんなさい、答えが見つかりませんでした")
            else:
                pass
        else:
            rospy.loginfo("DoCoMo Q&A response:%s","system error")
            return False

        return True


    def execTrcpChat(self, message):
        rospy.loginfo("chat:%s", message)
        #message が特定のキーワードであれば、それに対応した処理を行う
        """ 時間 ->現在時刻を答える"""
        time = re.compile('(?P<time>何時)').search(message)
        if time is not None:
            rospy.loginfo("What Time is it now? :%s", message)        
            d = datetime.datetime.today()
            text = u'%d時%d分です。'%(d.hour, d.minute)

            self.trcpSay(text)
            return True

        # 特定のキーワード処理はここまで
        print self.nowmode
        try:
            """ もし現在の会話モードが「しりとり」なら
                文章理解APIをスキップする

                それ以外なら、文章理解APIで文章を解析する
            """
            if self.nowmode == "CHAIN":
                self.resp_understanding.success = True
                self.resp_understanding.response.commandId = "BC00101"
                self.resp_understanding.response.utteranceText = message
            else:
                self.req.utteranceText = message
                self.resp_understanding = self.understanding(self.req)

            if  self.resp_understanding.success:
                commandId = self.resp_understanding.response.commandId
                rospy.loginfo("<< %s", commandId)

                if commandId == "BC00101":
                    """雑談"""
                    rospy.loginfo("DoCoMo Chat")
                    self.req_chat.utt = message
                    self.res_chat = self.chat(self.req_chat)
                    rospy.loginfo("DoCoMo Chat response:%s",self.res_chat.response)

                    """雑談対話からのレスポンスを設定する"""
                    self.req_chat.mode = self.res_chat.response.mode.encode('utf-8')
                    self.req_chat.context = self.res_chat.response.context.encode('utf-8')

                    if self.nowmode == "CHAIN":
                        if self.res_chat.response.mode == "srtr":
                            print self.nowmode
                            self.nowmode = "CHAIN"                    
                            self.trcpSay(self.res_chat.response.utt)
                        else:
                            print self.nowmode
                            self.nowmode = "CHAT"
                            self.trcpSay(self.res_chat.response.utt)
                    elif self.nowmode == "CHAT":                       
                        if self.res_chat.response.mode == "srtr":
                            print self.nowmode
                            self.nowmode = "CHAIN"                    
                            self.trcpSay(self.res_chat.response.utt)
                        else:
                            print self.nowmode
                            self.nowmode = "CHAT"
                            rospy.loginfo("TRCP Chat response:%s",self.res_chat.response.yomi)
                            self.trcpSay(self.res_chat.response.yomi)





                elif commandId  == "BK00101":
                    """知識検索"""
                    rospy.loginfo(":Q&A")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)

                elif commandId  == "BT00101":
                    """乗換案内"""
                    rospy.loginfo(":Transfer")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)

                elif commandId  == "BT00201":
                    """地図"""
                    rospy.loginfo(":Map")                    
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)

                elif commandId == "BT00301":
                    """天気"""
                    rospy.loginfo(":Weather")                    
                    """お天気検索"""
                    """http://weather.livedoor.com/weather_hacks/webservice"""
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)

                elif commandId == "BT00401":
                    """グルメ検索"""
                    rospy.loginfo(":Restaurant")
                    """ グルなびWebサービス"""
                    """http://api.gnavi.co.jp/api/"""
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)

                    
                elif commandId == "BT00501":
                    """ブラウザ"""
                    rospy.loginfo(":Webpage")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT00601":
                    """観光案内"""
                    rospy.loginfo(":Sightseeing")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT00701":
                    """カメラ"""
                    rospy.loginfo(":Camera")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT00801":
                    """ギャラリー"""
                    rospy.loginfo(":Gallery")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT00901":
                    """通信"""
                    rospy.loginfo(":Coomunincation")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01001":
                    """メール"""
                    rospy.loginfo(":Mail")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01101":
                    """メモ登録"""
                    rospy.loginfo(":Memo input")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01102":
                    """メモ参照"""
                    rospy.loginfo(":Memo output")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01201":
                    """アラーム"""
                    rospy.loginfo(":Alarm")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01301":
                    """スケジュール登録"""
                    rospy.loginfo(":Schedule input")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01302":
                    """スケジュール参照"""
                    rospy.loginfo(":Schedule input")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01501":
                    """端末設定"""
                    rospy.loginfo(":Setting")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT01601":
                    """SNS投稿"""
                    rospy.loginfo(":SNS")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BT90101":
                    """キャンセル"""
                    rospy.loginfo(":Cancel")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BM00101":
                    """地図乗換"""
                    rospy.loginfo(":Map transfer")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                elif commandId == "BM00201":
                    """通話メール"""
                    rospy.loginfo(":Short mail")
                    self.execDoCoMoQA(self.resp_understanding.response.utteranceText)
                    
                else:
                    """発話理解APIで判定不能"""
                    """Undeterminable"""     
                    rospy.loginfo("Undeterminable:%s",self.resp_understanding.response.commandId)
                    self.trcpSay("ごめんなさい、良く聞き取れませんでした。")

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
