import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
import paho.mqtt.client as mqtt
from time import sleep
import urllib.request
import numpy as np


client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
    client.subscribe("sensors/#")
    client.subscribe("telegram/#")

def on_message(client, userdata, message):
    topic = message.topic
    data = message.payload.decode()
    timestamp = time.time()
    
    if topic.startswith("sensors/motion"):
        handle_motion();
    elif topic.startswith("sensors/audio"):
        save_audio_file(topic, data, timestamp)
    elif topic == "telegram/command":
        handle_telegram_command(client, data)

    print("Received message")

def save_audio_file(topic, data, timestamp):
    filename = topic.split("/")[-1] + str(timestamp)
    filepath = "./audio/" + filename
    with open(filepath, "wb") as audio_file:
        audio_file.write(data)

def handle_telegram_command(client, command):
    if command == "/unlock":
        client.publish("arduino/command", "unlock")
    elif command == "/lock":
        client.publish("arduino/command", "lock")

def handle_motion():
    url = 'http://172.20.10.6/cam-hi.jpg'
    labels = []
    for i in range(10): #10 frames
        img_resp=urllib.request.urlopen(url)
        imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
        im = cv2.imdecode(imgnp,-1)
        bbox, label, conf = cv.detect_common_objects(im, model="yolov3")
        output_image = draw_bbox(im, bbox, label, conf)
        
        for item in label:
            if item in labels:
                pass
            else:
                labels.append(item)
                
        cv2.imshow("At your door", output_image)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyWindow("At your door")
            break
    
    print(labels)
    if "person" in labels:
        client.publish("detection/camera", "Person detected")

client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever() #starts running loop in background to communicate with MQTT broker
