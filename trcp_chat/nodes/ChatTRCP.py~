#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
"""
    Chat program

    ROSPEEXから入力された文章を使い、DoCoMoAPIで会話する

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

from rospeex_if import ROSpeexInterface

from okada.srv import *
from okada.msg import *


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
        
        self.nowmode = "CHAT"
        rospy.spin()

    """ DoCoMo 雑談対話の実行 """
    def execChat(self, message):
        # Rospeexを使うと、文字列の最後に「。」が付くので削除する
        src = message
        dst=src.replace('。', '')
        self.req_chat.utt = dst

        self.res_chat = self.chat(self.req_chat)
        rospy.loginfo("TRCP Chat response:%s",self.res_chat.response)
        self.rospeex.say(self.res_chat.response.yomi , 'ja', 'nict')

        return True

    """ DoCoMo 知識検索の実行 """
    def execQA(self, message):
        rospy.loginfo("TRCP:Q&A")
        self.req_qa = DoCoMoQaReq()
        self.req_qa.text = message
        res_qa = self.qa(self.req_qa)
        rospy.loginfo("TRCP Q&A response:%s",res_qa.response.code)
        self.rospeex.say(res_qa.response.textForSpeech , 'ja', 'nict')

        return True

    def sr_response(self, message):
        rospy.loginfo("sr_responsee:%s", message)
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

        """ 自己紹介 ->挨拶する"""
        hello = re.compile('(?P<introduce>)自己紹介').search(message)
        if hello is not None:
            rospy.loginfo("Self introduce :%s", message)        
            text = "皆さんこんにちわ。私の名前はイレイサーです。僕は家庭でみんなの手伝いをするために作られたホームサービスロボットなんだ。"
            # rospeex reply
            self.rospeex.say(text, 'ja', 'nict')
            return True

        # 特定のキーワード処理はここまで
            
        try:
            """ もし現在の会話モードが「しりとり」なら
                文章理解APIをスキップする
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
                rospy.loginfo("<<< %s", commandId)
                if commandId == "BC00101":
                    rospy.loginfo("BBBB")
                    """雑談"""
                    rospy.loginfo("TRCP:Chat")

                    
                    # Rospeexを使うと、文字列の最後に「。」が付くので削除する
                    src = self.resp_understanding.response.utteranceText
                    dst=src.replace('。', '')
                    self.req_chat.utt = dst

                    self.res_chat = self.chat(self.req_chat)
                    rospy.loginfo("TRCP Chat response:%s",self.res_chat.response)

                    """雑談対話からのレスポンスを設定する"""
                    self.req_chat.mode = self.res_chat.response.mode.encode('utf-8')
                    self.req_chat.context = self.res_chat.response.context.encode('utf-8')

                    if self.nowmode == "CHAIN":
                        if self.res_chat.response.mode == "srtr":
                            self.nowmode = "CHAIN"                    
                            self.rospeex.say(self.res_chat.response.utt , 'ja', 'nict')
                        else:
                            self.nowmode = "CHAT"
                            self.rospeex.say(self.res_chat.response.utt , 'ja', 'nict')
                    elif self.nowmode == "CHAT":                       
                        if self.res_chat.response.mode == "srtr":
                            self.nowmode = "CHAIN"                    
                            self.rospeex.say(self.res_chat.response.utt , 'ja', 'nict')
                        else:
                            self.nowmode = "CHAT"
                            self.rospeex.say(self.res_chat.response.yomi , 'ja', 'nict')


                elif commandId  == "BK00101":
                    """知識検索"""
                    rospy.loginfo("TRCP:Q&A")
                    self.req_qa = DoCoMoQaReq()
                    self.req_qa.text = self.resp_understanding.response.utteranceText
                    print self.resp_understanding.response.utteranceText
                    res_qa = self.qa(self.req_qa)
                    rospy.loginfo("TRCP Q&A response:%s",res_qa.response.code)
                    self.rospeex.say(res_qa.response.textForSpeech , 'ja', 'nict')

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
                    if res_qa.success:
                        print res_qa.response.textForDisplay
                        rospy.loginfo("TRCP:%s",res_qa.response.textForSpeech)
                        # for answer in res_qa.response.answer:
                        #     print answer.rank
                        #     print answer.answerText
                        #     print answer.linkText
                        #     print answer.linkUrl
                        if res_qa.response.code == 'S020000':
                            pass
                        elif res_qa.response.code == 'S020001':
                            pass
                        elif res_qa.response.code == 'S020010':
                            pass
                        elif res_qa.response.code == 'S020011':
                            pass                            
                        elif res_qa.response.code == 'E010000':
                            pass
                        elif res_qa.response.code == 'E020000':
                            pass
                        elif res_qa.response.code == 'E099999':
                            pass
                        else:
                            pass
                    else:
                        pass


                elif commandId  == "BT00101":
                    """乗換案内"""
                    rospy.loginfo(":Transfer")
                    self.execQA(message)                                        
                elif commandId  == "BT00201":
                    """地図"""
                    rospy.loginfo(":Map")                    
                    self.execQA(message)                    

                elif commandId == "BT00301":
                    """天気"""
                    rospy.loginfo(":Weather")                    
                    """お天気検索"""
                    """http://weather.livedoor.com/weather_hacks/webservice"""
#                    self.execQA(message)
                    self.execChat(message)                                        

                elif commandId == "BT00401":
                    """グルメ検索"""
                    rospy.loginfo(":Restaurant")
                    """ グルなびWebサービス"""
                    """http://api.gnavi.co.jp/api/"""
                    self.execQA(message)                    

                    
                elif commandId == "BT00501":
                    """ブラウザ"""
                    rospy.loginfo(":Webpage")
                    self.execQA(message)                                                            
                elif commandId == "BT00601":
                    """観光案内"""
                    rospy.loginfo(":Sightseeing")
                    self.execQA(message)                                                            
                elif commandId == "BT00701":
                    """カメラ"""
                    rospy.loginfo(":Camera")
                    self.execQA(message)                                                            
                elif commandId == "BT00801":
                    """ギャラリー"""
                    rospy.loginfo(":Gallery")
                    self.execQA(message)                                                            
                elif commandId == "BT00901":
                    """通信"""
                    rospy.loginfo(":Coomunincation")
                    self.execQA(message)                                                            
                elif commandId == "BT01001":
                    """メール"""
                    rospy.loginfo(":Mail")
                    self.execQA(message)                                                            
                elif commandId == "BT01101":
                    """メモ登録"""
                    rospy.loginfo(":Memo input")
                    self.execQA(message)                                                            
                elif commandId == "BT01102":
                    """メモ参照"""
                    rospy.loginfo(":Memo output")
                    self.execQA(message)                                                            
                elif commandId == "BT01201":
                    """アラーム"""
                    rospy.loginfo(":Alarm")
                    self.execQA(message)                                                            
                elif commandId == "BT01301":
                    """スケジュール登録"""
                    rospy.loginfo(":Schedule input")
                    self.execQA(message)
                    
                elif commandId == "BT01302":
                    """スケジュール参照"""
                    rospy.loginfo(":Schedule input")
                    self.execQA(message)                                                            
                elif commandId == "BT01501":
                    """端末設定"""
                    rospy.loginfo(":Setting")
                    self.execQA(message)                                                            
                elif commandId == "BT01601":
                    """SNS投稿"""
                    rospy.loginfo(":SNS")
                    self.execQA(message)                                                            
                elif commandId == "BT90101":
                    """キャンセル"""
                    rospy.loginfo(":Cancel")
                    self.execQA(message)                                                            
                elif commandId == "BM00101":
                    """地図乗換"""
                    rospy.loginfo(":Map transfer")
                    self.execQA(message)                                                            
                elif commandId == "BM00201":
                    """通話メール"""
                    rospy.loginfo(":Short mail")
                    self.execQA(message)                                                            
                    
                else:
                    """発話理解APIで判定不能"""
                    """Undeterminable"""     
                    rospy.loginfo("Undeterminable:%s",self.resp_understanding.response.commandId)
                    self.rospeex.say("ごめんなさい、良く聞き取れませんでした。" , 'ja', 'nict')


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
