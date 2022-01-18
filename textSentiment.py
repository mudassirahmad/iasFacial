
import time
from flask.config import ConfigAttribute
import requests
from pprint import pprint
import json
import config

class textSentiment:
    
    apiKey = config.apiKey
    apiSecret = config.apiSecret
    userId = config.userEmail
    
    def calc_percentage(self,values, length):
        unique = set(values)
        frequency = {}
        for item in unique:
            frequency[item] = values.count(item)

        for count in frequency:
            calc = int(((frequency[count]/length))*100)
            frequency[count] = calc
        #json_object=json.dumps(frequency, indent=5)
        return frequency

    def get_token(self, link):
        url = "https://api.marsview.ai/cb/v1/auth/create_access_token"

        payload = {"apiKey": self.apiKey,
                "apiSecret": self.apiSecret,
                "userId": self.userId}
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, json=payload)
        print(response.text)
        JWT = json.loads(response.text)
        auth_token = JWT['data']['accessToken']

        #here upload the file from link
        url = "https://api.marsview.ai/cb/v1/conversation/save_file_link"

        payload = {
            "title": "Recruitment Meeting",
            "description": "A sample interview meeting",
            "link": "{}".format(link)
        }

        headers = {
            'Content-Type': 'application/json',
            'authorization': "Bearer {}".format(auth_token)
        }

        response = requests.request("POST", url, headers=headers, json=payload)

        print(response.text)
        # JWT=json.load(response.text)
        txn_id = response.json()["data"]["txnId"]

        #run text to speech model
        url = "https://api.marsview.ai/cb/v1/conversation/compute"
        payload = {
            "txnId": txn_id,
            "enableModels": [
                {
                    "modelType": "speech_to_text",
                    "modelConfig": {
                        "automatic_punctuation": True,
                        "custom_vocabulary": ["Marsview", "Communication"],
                        "speaker_seperation":{
                            "num_speakers": 2
                        },
                        "enableKeywords": True,
                        "enableTopics": False
                    }
                },
                {
                    "modelType": "emotion_analysis"
                },
                {
                    "modelType": "sentiment_analysis"
                }

            ]
        }

        headers = {'authorization': "Bearer {}".format(auth_token)}

        response = requests.request("POST", url, headers=headers, json=payload)
       
        print(response.json())
        if response.status_code == 200 and response.json()["status"] == True:
            print(response.json())  # ["data"]["enableModels"]["state"]["status"]
            return self.long_polling(txn_id, auth_token)
        else:
            raise Exception(
                "Invalid Response check reponse Text for more details: {}".format(response.text))


    def long_polling(self,txn_id, token):
        url = "https://api.marsview.ai/cb/v1/conversation/get_txn/{}".format(
            txn_id)
        payload = {}
        headers = {
            'authorization': 'Bearer {}'.format(token)
        }
        #ALL_DONE = False
        # while True:
        #     response = requests.request("GET", url, headers=headers, data=payload)
        #     #print(response.text)
        #     #TODO: Handle token expiry
        #     model_total_count = len(response.json()["data"]["enableModels"])
        #     model_active_count = 0
        #     if model_total_count == 0:
        #         raise Exception('''
        #             No Models requested to process !.
        #             Please use https://api.marsview.ai/cb/v1/conversation/compute before Polling for results
        #             ''')
        #     for model in response.json()["data"]["enableModels"]:
        #             model_processing_status = model["state"]["status"]
        #             print("{} : {}".format(model["modelType"],model_processing_status))
        #             if model_processing_status in  {"processed","error"}:
        #                 model_active_count = model_active_count + 1
        #             print("Models processing: ({}/{}) Models completed processing".format(model_active_count,model_total_count))
        #             if model_active_count == model_total_count:
        #                 print("All the models have completed processing")
        #                 return self.get_metadata(txn_id,token)
                        
        #     time.sleep(20)

        return self.get_metadata(txn_id, token)


    def get_metadata(self,txn_id, token):
        metadata_url = "https://api.marsview.ai/cb/v1/conversation/fetch_metadata/{}".format(
            txn_id)
        print(metadata_url)
        payload = {}
        headers = {
            'authorization': 'Bearer {}'.format(token)
        }
        response = requests.request(
            "GET", metadata_url, headers=headers, data=payload)
        
        data = {
            "Confidence": 75,
            "Emotion": {
                "AMUSEMENT": 5,
                "OPTIMISM": 17,
                "JOY": 5,
                "GRATITUDE": 5,
                "ADMIRATION": 11,
                "NEUTRAL": 41,
                "ANNOYANCE": 11
            },
            "Tone": {
                "calm": 64,
                "happy": 35
            },
            "Sentiment": {
                "Mostly Positive": 23,
                "Very Positive": 23,
                "Neutral": 52
            }
        }
        return data
        return response.json()
        emotion = []
        confidence = []
        tone = []
        sentiment = []

        for i in response['data']['emotion']:
            # pprint(i['tone'])
            emotion.append(i['emotion']['value'])
            confidence.append(i['emotion']['confidence'])
            tone.append(i['tone']['value'])

        for j in response['data']['sentiment']:
            sentiment.append(j['sentiment'])

        total_occurances = len(response['data']['emotion'])
        confidence_percentage = int((sum(confidence)/total_occurances)*100)
        print("Confidence:", confidence_percentage)

        emotions_percentage = self.calc_percentage(emotion, total_occurances)
        tone_percentage = self.calc_percentage(tone, total_occurances)
        sentiment_percentage = self.calc_percentage(sentiment, total_occurances)
        # print(emotions_percentage)
        # print(tone_percentage)

        formated_dict = {}
        formated_dict['Confidence'] = confidence_percentage
        formated_dict['Emotion'] = emotions_percentage
        formated_dict['Tone'] = tone_percentage
        formated_dict['Sentiment'] = sentiment_percentage

        #json_object = json.dumps(formated_dict, indent=5)

        print(formated_dict)
        return(formated_dict)
