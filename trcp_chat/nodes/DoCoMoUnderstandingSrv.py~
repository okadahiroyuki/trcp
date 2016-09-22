#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-
"""
    DoCoMoUnderstandingSrv.py

    Service Server for DoCoMo SentenceUnderstanding API

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

from okada.msg import DoCoMoUnderstandingReq
from okada.msg import DoCoMoUnderstandingRes
from okada.msg import DoCoMoUnderstandingSlotStatus
from okada.msg import DoCoMoUnderstandingEtractedWords

from okada.srv import DoCoMoUnderstanding
from okada.srv import DoCoMoUnderstandingResponse

json_data={
    "projectKey": "OSU",
    "appInfo": {
        "appName": "hoge_app",
        "appKey": "hoge_app01"
    },
    "clientVer": "1.0.0",
    "dialogMode": "off",
    "language": "ja",
    "userId": "12 123456 123456 0",
    "location": {
        "lat": "139.766084",
        "lon": "35.681382"
    },
    "userUtterance": {
        "utteranceText": "",
    }
}

class DoCoMoSentenceUnderstandingSrv(object):
    """ DoCoMoSentenceUnderstandingSrv class """
    def __init__(self):
        """ Initializer """

    def run(self):
        """ run ros node """
        # initialize ros node
        rospy.init_node('DocomoSentenceUnderstandingSrv')
        rospy.loginfo("start DoCoMoSentenceUnderstandingSrv node")
        service_server = rospy.Service('docomo_sentenceunderstanding',DoCoMoUnderstanding,self.SentenceUnderstanding_handler)
        rospy.loginfo("start DoCoMoSentenceUnderstanding service server")
        self.APIKEY = rospy.get_param("~APIKEY", "4e4e61744672324d792f533965647867467767654978717445316a3337696430386b453371715246456238")
        self.url = rospy.get_param("~sentence_url","https://api.apigw.smt.docomo.ne.jp/sentenceUnderstanding/v1/task?" )
        
        rospy.spin()        

    def SentenceUnderstanding_handler(self, query):
        """ query sentence understanding """
        """ DoCoMoSentenceUnderstandingReq.msg """
        rospy.loginfo("DoCoMoSentenceUnderstandingSrv Query:%s", query)
        req = query.request
        if req.utteranceText == '':
            return DoCoMoUnderstandingResponse(success=False)
            
        if not req.projectKey:
            json_data['projectKey'] = "OSU"
        else:
            json_data['projectKey'] = req.projectKey
        if not req.appName:
            json_data['appName'] = ""
        else:
            json_data['appName'] = req.appName
        if not req.appKey:
            json_data['appKey'] = "hoge_app01"
        else:
            json_data['appKey'] = req.appKey
        json_data['clientVer'] = "1.0.0"
        json_data['dialogMode'] = "off"            
        if not req.language:
            json_data['language']="ja"
        else:
            json_data['language']=req.language
        if not req.userId:
            json_data['userId']="12 123456 123456 0"
        else:
            json_data['userId']=req.userId
        if not req.lat:
            json_data['lat']="139.766084"
        else:
            json_data['lat']=req.lat
        if not req.lon:
            json_data['lon']="35.681382"
        else:
            json_data['lon']=req.lon
        (json_data['userUtterance'])['utteranceText'] = req.utteranceText

        # Request body
        body={}
        body['APIKEY'] = self.APIKEY
        url_value = urllib.urlencode(body)
        req = urllib2.Request(self.url+url_value)
        req.add_header('Content-Type', 'application/json')
        try:
            response = urllib2.urlopen(req,json.dumps(json_data))
        except Exception as e:
            print e
            return DoCoMoUnderstandingResponse(success=False)
        the_page=json.load(response)

        # Response body
        """   """
        res=DoCoMoUnderstandingRes()

        res.projectKey = the_page['projectKey']
        res.appName = (the_page['appInfo'])['appName']
        res.appKey = (the_page['appInfo'])['appKey']
        res.clientVer =  the_page['clientVer']
        res.dialogMode =  the_page['dialogMode']            
        res.language =  the_page['language']
        res.userId =  the_page['userId']
        res.utteranceText = (the_page['userUtterance'])['utteranceText']
        res.utteranceRevised = (the_page['userUtterance'])['utteranceRevised']
        for wd in (the_page['userUtterance'])['utteranceWord']:
            res.utteranceWord.append(wd)
        for tsk in the_page['taskIdList']:
            res.taskIdList.append(tsk)
        res.commandId = ((the_page['dialogStatus'])['command'])['commandId']
        res.commandName = ((the_page['dialogStatus'])['command'])['commandName']
        res.serverSendTime =  the_page['serverSendTime']                


        """  """
        rospy.loginfo("DoCoMoSentenceUnderstanding:%s",res.utteranceText)
        rospy.loginfo("DoCoMoSentenceUnderstanding:%s",res.commandName)
        if res.commandId == "BC00101":
            """雑談"""
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BK00101":
            """知識検索"""
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00101":
            """乗換案内"""
            #stationTo, stationFrom
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00201":
            """地図"""
            #searchArea,hereArround,facilityName
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00301":
            """天気"""
            #searchArea,hereArround,daten
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00401":
            """グルメ検索"""
            #gourmetGenre,searchArea,hereArround
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            
                
        elif res.commandId == "BT00501":
            """ブラウザ"""
            #browser,website
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00601":
            """観光案内"""
            #searchArea,hereArround,sightseeing
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            
                
        elif res.commandId == "BT00701":
            """カメラ"""
            #
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00801":
            """ギャラリー"""
            #
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT00901":
            """通話"""
            #phoneTo
            setContent(self, the_page, res)
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)            

        elif res.commandId == "BT01001":
            """メール"""
            #mailTo,mailBody
            setContent(self,the_page, res)
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BT01101":
            """メモ登録"""
            #memoBody
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BT01102":
            """メモ参照"""
            #memoBody
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BT01201":
            """アラーム"""
            #time
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BT01301":
            """スケジュール登録"""
            #date,time,scheduleBody
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BT01302":
            """スケジュール参照"""
            #date,time
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BT01501":
            """端末設定"""
            #setting
        elif res.commandId == "BT01601":
            """SNS投稿"""
            #snsSource,snsBody
        elif res.commandId == "BT90101":
            """キャンセル"""
            #
        elif res.commandId == "BM00101":
            """地図乗換"""
            #searchArea
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "BM00201":
            """通話メール"""
            #phoneTo
            setContent(self, the_page, res)
            setSlotStatus(self,the_page,res)
            setExtractedWords(self,the_page,res)

        elif res.commandId == "EBC00101":
            """ Chatting """
            pass
        elif res.commandId == "EBT02501":
            """ Information """
            pass          
        elif res.commandId == "EBT01101":
            """Weather"""
            setSlotStatus(self,the_page,res)
        elif res.commandId == "EBT01401":
            """ Travel"""
            setSlotStatus(self,the_page,res)        
        elif res.commandId == "EBT00101":
            """Transportation"""
            setSlotStatus(self,the_page,res)
        elif res.commandId == "EBT00601":
            """News"""
            setSlotStatus(self,the_page,res)
        elif res.commandId == "EBT00301":
            """Call"""
            setSlotStatus(self,the_page,res)
        elif res.commandId == "EBT01201":
            """Restaurant"""
            setSlotStatus(self,the_page,res)
            
            """error"""
        elif res.commandId == "SE00101":
            """判定不能"""
            pass
        elif res.commandId == "SE00201":
            """サーバエラー１"""
            return DoCoMoUnderstandingResponse(success=False, response=res)
        elif res.commandId == "SE00202":
            """サーバエラー２"""
            return DoCoMoUnderstandingResponse(success=False, response=res)
        elif res.commandId == "SE00301":
            """ライブラリエラー"""
            return DoCoMoUnderstandingResponse(success=False, response=res)
        else:
            res.commandId = "SE00101"
            """判定不能"""
            """Undeterminable"""     

        return DoCoMoUnderstandingResponse(success=True, response=res)

def setContent(self, the_page, res):
    res.contentSource=(the_page['content'])['contentSource']
    res.contentType=(the_page['content'])['contentType']
    res.contentValue=(the_page['content'])['contentValue']
    return True

def setSlotStatus(self,the_page,res):
    self.slotStatus = (the_page['dialogStatus'])['slotStatus']
    for slot in self.slotStatus:
        st = DoCoMoUnderstandingSlotStatus()                    
        st.slotName  = slot['slotName']
        st.slotValue = slot['slotValue']
        try:
            st.ValueType = slot['valueType']
        except:
            pass
            res.slotStatus.append(st)
    return True    

def setExtractedWords(self,the_page,res):
    self.extractedWords = the_page['extractedWords']
    for words in self.extractedWords:
        wd = DoCoMoUnderstandingEtractedWords()            
        wd.wordsValue = words['wordsValue']                
        for wt in words['wordsType']:
            wd.wordsType.append(wt)
            res.extractedWords.append(wd)
    return True    

if __name__ == '__main__':
    try:
        node = DoCoMoSentenceUnderstandingSrv()
        node.run()
    except rospy.ROSInterruptException:
        pass
