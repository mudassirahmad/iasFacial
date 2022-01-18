from flask import Flask, config,Response
from flask import request
from bson.objectid import ObjectId
from pymongo import MongoClient
from textSentiment import textSentiment
from videoFrameRead import videoFrameRead
import config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = config.client
url ='https://res.cloudinary.com/dx6obccn6/video/upload/v1641873829/testing_ktftma.ogg'


@app.route('/sentiment', methods=['POST'])
def get_data():
    
    
    if request.method == "POST":
        request_data = request.get_json()
        
        #jobID = request_data['jobID']
        #userID = request_data['userID']
        jobID='61c15a12909d9e00232ff5e7'
        userID='619bfe7717cbcc00236ed8d1'
        url= request_data['url']
        # name=request_data['name']
        
        print(jobID,"userid",userID,"link", url)
        print("link:",url)
        textsenti=textSentiment()   
        videoEmotion=videoFrameRead()
        link=url
        
        Data1=textsenti.get_token(link)
        print(Data1)
        print("facial starts")
        Data2=videoEmotion.facialEmtions(link)
        print("facial done")
        
        db=client.IAS
        records=db.interviewresults
        data_update={
            'recorded': False,
            'mcq':True,
            'recordedResult': [{"Text":Data1, "Video":Data2}]
        }
        
        if(records.find({"jobID" : ObjectId("{}".format(jobID)), "userID": ObjectId("{}".format(userID))})):
            records.update_one({"jobID" : ObjectId("{}".format(jobID)), "userID": ObjectId("{}".format(userID))}, {'$set': data_update})
            
            print("In update")
            return Response("True", status=201, mimetype='application/json')
        else:
            return Response("User Not Found", status=400, mimetype='application/json')
        
if __name__==("__main__"):
    app.run()