from flask import Flask, config
from flask import request
from bson.objectid import ObjectId
from pymongo import MongoClient
from textSentiment import textSentiment
from videoFrameRead import videoFrameRead
import config
import json

app = Flask(__name__)
client = config.client
link ='C:/Users/Mudassir/Desktop/Emotion_recognition/video.mp4'




@app.route('/sentiment', methods=['POST'])
def get_data():
    # url = 'http://127.0.0.1:5000/'
    # payload={
    #     "applicantId": applicantID,
    #     "jobId":jobId,
    #     "email":email
    # }
    # headers ={
    #     'Content-Type': 'applicantion/json'
    # }
    # response = requests.request("POST",url, headers=headers, json=payload)
    # print(response)

    if request.method == "POST":
        request_data = request.get_json()
        # jobId = request_data['jobID']
        # userId = request_data['userID']
        # link= request_data['link']
        jobId='6127ce25737dd9379811b4a3'
        userId='6113cc4b25bcf835a8ca69cc'
        textsenti=textSentiment()
        videoEmotion=videoFrameRead()
        
        Data1=textsenti.get_token(link)
        print("facial starts")
        Data2=videoEmotion.facialEmtions(link)
        print("facial sone")
        # print(type(Data))
        db=client.IAS
        records=db.interviewresults
        data_update={
            'recorded': False,
            'mcq':True,
            'recordedResult': [{"Text":Data1, "Video":Data2}]
        }
        
        if(records.find({"jobID" : ObjectId("{}".format(jobId)), "userID": ObjectId("{}".format(userId))})):
            records.update_one({"jobID" : ObjectId("{}".format(jobId)), "userID": ObjectId("{}".format(userId))}, {'$set': data_update})
            return("True")
        else:
            raise ValueError("Id's not found in database")
            return("False")
        
