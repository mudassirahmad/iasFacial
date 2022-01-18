m=""
with open('C:/Users/Mudassir/Desktop/Emotion_recognition/video.mp4', 'rb') as f:
    m=f.read()

with open('recieved.mp4','wb') as q:
    q.write(m)