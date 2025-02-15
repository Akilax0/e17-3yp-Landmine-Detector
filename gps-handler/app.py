from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
from flask_cors import CORS
import json
import time

app = Flask(__name__)
CORS(app)

app.config['MQTT_BROKER_URL'] = 'mqtt.eclipseprojects.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds

topic = '/3yp/ldr01/detections'

coordinatesTopic = '/3yp/ldr01/coordinates'

finishedTopic = '/3yp/ldr01/finish'

landminesAndObstacles = [{'landmine': 0, 'obstacle': 0, 'lat': 7.2699, 'lon': 80.5938},
                         {'landmine': 0, 'obstacle': 1, 'lat': 7.2699, 'lon': 80.59381},
                         {'landmine': 0, 'obstacle': 0, 'lat': 7.2699, 'lon': 80.59382},
                         {'landmine': 1, 'obstacle': 0, 'lat': 7.26989, 'lon': 80.59381},
                         {'landmine': 0, 'obstacle': 0, 'lat': 7.26989, 'lon': 80.59382},
                         {'landmine': 0, 'obstacle': 0, 'lat': 7.26988, 'lon': 80.5938},
                         {'landmine': 1, 'obstacle': 0, 'lat': 7.26988, 'lon': 80.59381},
                         {'landmine': 0, 'obstacle': 1, 'lat': 7.26988, 'lon': 80.59382}]


def sendData():
    for i in range(len(landminesAndObstacles)):
        # mqtt_client.connect("mqtt.eclipseprojects.io", port=1883)
        mqtt_client.publish(topic, json.dumps(landminesAndObstacles[i]))
        print("published to topic " + topic)
        time.sleep(5)

detections = []

coordinates = []
coordinatesDict = {}

mqtt_client = Mqtt(app)


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic, 0)
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   data = dict(
       topic=message.topic,
       payload=message.payload.decode()
    )
   data = json.loads(data['payload'])

   #  check whether it is an endpoint
   wayPoint = [data['lat'], data['lon']]

   if (wayPoint in coordinates):
       coordinates.remove(wayPoint)
       print(len(coordinates))

       if (len(coordinates) == 0):
           x = {
               "finished": True
           }
           mqtt_client.publish(finishedTopic, json.dumps(x), 0)

       return

   print('its not a waypoint')
   detections.append([data['landmine'], data['obstacle'], data['lat'], data['lon']])

   print(detections)

@app.route('/')
def index():
    return "Welcome to GPS handler"

@app.route('/get-detections', methods=['GET'])
def sendDetections():
    return jsonify(detections)

@app.route('/create-search', methods=['POST'])
def createSearch():
    data = request.json
    # print(request.json)
    lat = data['lat']
    lan = data['lan']
    rad = data['rad']

    # global coordinates
    global coordinatesDict
    global coordinates
    # coordinatesDict, coordinates = calculateWaypoints(lat, lan, rad)

    # mqtt_client.publish(coordinatesTopic, json.dumps(coordinatesDict), 0)
    # print(type(json.dumps(coordinatesDict)))
    # print(len(coordinates))

    sendData()

    return "data receieved"

def calculateWaypoints(lat, lan, rad):
    coordinatesD = {}
    coordinates = []
    arraySize = int((2*rad)/1.1)
    topLeftLat = lat + (((arraySize/2)-1)*0.00001)
    topLeftLan = lan - (((arraySize/2)-1)*0.00001)

    x = 0
    for row in range(arraySize):
        for col in range(arraySize):
            current = [round(topLeftLat-row*0.00001, 5), round(topLeftLan+col*0.00001, 5)]
            coordinates.append(current)
            coordinatesD[str(x)] = current
            x += 1
            print(coordinatesD)
    return coordinatesD, coordinates



if __name__ == '__main__':
   app.run(host='127.0.0.1', port=5000)



# todos
# listen to create search mqtt topic - **(change to post request)
# calculate waypoints for robot - **
# then send waypoints (5) through mqtt **
# listen and check waypoints are acheived **
# listen detections **
# until all points are checked **

# send to finish signal to separate topic **
