from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
from imutils.video import VideoStream
from itertools import zip_longest
import numpy as np
import argparse
import imutils
import time
import dlib
import csv
import cv2
import requests
import time

# Parse command line arguments
def parse_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--prototxt", required=False, help="path to Caffe 'deploy' prototxt file")
    ap.add_argument("-m", "--model", required=True, help="path to Caffe pre-trained model")
    ap.add_argument("-i", "--input", type=str, help="path to optional input video file")
    ap.add_argument("-o", "--output", type=str, help="path to optional output video file")
    ap.add_argument("-c", "--confidence", type=float, default=0.4, help="minimum probability to filter weak detections")
    ap.add_argument("-s", "--skip-frames", type=int, default=30, help="# of skip frames between detections")
    args = vars(ap.parse_args())
    return args

# Initialize previous_total_count to None
light = 2
previous_light=None
# Function to log the counting data
def log_data(move_in, in_time, move_out, out_time, total_people_inside):
    data = [move_in, in_time, move_out, out_time]
    # Transpose the data to align the columns properly
    export_data = zip_longest(*data, fillvalue='')

    with open('counting_data.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if myfile.tell() == 0:  # Check if header rows are already existing
            wr.writerow(("Move In", "In Time", "Move Out", "Out Time"))
        wr.writerows(export_data)

    global light
    global previous_light
    # Assuming total_people_inside is a list with a single element
    total_count = total_people_inside

    # Check if the total count has changed since the last update
    # if total_count ==0:
    #     light=0
    # else:
    #     light=2
    
    # if light != previous_light:
    #     light_status_thingspeak(light)
    #     # Update previous_total_count
    #     previous_light = light
    
# def light_status_thingspeak(light):
#     url = 'https://api.thingspeak.com/update'
#     api_key = 'FBLPBYDLKQGMJ4G7'  # Replace with your ThingSpeak API Key

#     params = {
#         'api_key': api_key,
#         'field1': light
#     }

#     response = requests.get(url, params=params)

#     # Check the response status
#     if response.status_code == 200:
#         print("Light Status sent to ThingSpeak successfully: ", light)
#         time.sleep(15)
#     else:
#         print("Failed to send total count to ThingSpeak. Status code:", response.status_code)

# Main function for people counting

#function to send the count to django server
def send_count_to_django(count):
    url = 'http://127.0.0.1:8000/api/updatepersoncount'  # Replace with your Django view URL
    data = {'people_count': count}
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("People count updated on Django server")
        else:
            print("Failed to update count:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error sending request to Django:", e) 

def people_counter():
    args = parse_arguments()

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]

    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

    # Use VideoStream to read from the camera or input video file
    if not args.get("input", False):
        print("Starting the live stream...")
        vs = VideoStream(src=0).start()
    else:
        print("Starting the video...")
        vs = cv2.VideoCapture(args["input"])

    W = None
    H = None

    ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
    trackers = []
    trackableObjects = {}

    totalFrames = 0
    totalDown = 0
    totalUp = 0

    move_out = []
    move_in = []
    out_time = []
    in_time = []

    fps = None

    while True:
        frame = vs.read()
        frame = frame[1] if args.get("input", False) else frame

        if args["input"] is not None and frame is None:
            break

        frame = imutils.resize(frame, width=500)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if W is None or H is None:
            (H, W) = frame.shape[:2]

        status = "Waiting"
        rects = []

        if totalFrames % args["skip_frames"] == 0:
            status = "Detecting"
            trackers = []

            blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
            net.setInput(blob)
            detections = net.forward()

            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > args["confidence"]:
                    idx = int(detections[0, 0, i, 1])

                    if CLASSES[idx] == "person":
                        box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                        (startX, startY, endX, endY) = box.astype("int")

                        tracker = dlib.correlation_tracker()
                        rect = dlib.rectangle(startX, startY, endX, endY)
                        tracker.start_track(rgb, rect)

                        trackers.append(tracker)

        else:
            for tracker in trackers:
                status = "Tracking"
                tracker.update(rgb)
                pos = tracker.get_position()

                startX = int(pos.left())
                startY = int(pos.top())
                endX = int(pos.right())
                endY = int(pos.bottom())

                rects.append((startX, startY, endX, endY))

        cv2.line(frame, (0, H // 2), (W, H // 2), (0, 0, 0), 3)
        cv2.putText(frame, "-Prediction border - Entrance-", (10, H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        objects = ct.update(rects)

        for (objectID, centroid) in objects.items():
            to = trackableObjects.get(objectID, None)

            if to is None:
                to = TrackableObject(objectID, centroid)
            else:
                y = [c[1] for c in to.centroids]
                direction = centroid[1] - np.mean(y)
                to.centroids.append(centroid)

                if not to.counted:
                    if direction < 0 and centroid[1] < H // 2:
                        totalUp += 1
                        date_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                        move_out.append(totalUp)
                        out_time.append(date_time)
                        to.counted = True
                    elif direction > 0 and centroid[1] > H // 2:
                        totalDown += 1
                        date_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                        move_in.append(totalDown)
                        in_time.append(date_time)
                        to.counted = True

            trackableObjects[objectID] = to

        info_status = [
            ("Exit", totalUp),
            ("Enter", totalDown),
            ("Status", status),
        ]

        info_total = [
            ("Total people inside", totalDown - totalUp),
        ]

        for (i, (k, v)) in enumerate(info_status):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        for (i, (k, v)) in enumerate(info_total):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (265, H - ((i * 20) + 60)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if totalFrames > 0:
            total_people_inside = totalDown - totalUp
            log_data(move_in, in_time, move_out, out_time, total_people_inside)

        cv2.imshow("Real-Time Monitoring/Analysis Window", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        totalFrames += 1

    vs.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    people_counter()