from imutils.video import FPS
# from utils.mailer import Mailer
from itertools import zip_longest
from tracker.centroidtracker import CentroidTracker
from tracker.trackableobject import TrackableObject
import numpy as np
import threading
import argparse
import datetime
import schedule
import logging
import imutils
import time
import json
import csv
import cv2

# execution start time
start_time = time.time()
# setup logger
logging.basicConfig(level=logging.INFO, format="[INFO] %(message)s")
logger = logging.getLogger(__name__)
# initiate features config.
with open("utils/config.json", "r") as file:
    config = json.load(file)

def parse_arguments():
    # function to parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", required=True,
                    help="path to TensorFlow pre-trained model")
    ap.add_argument("-i", "--input", type=int, default=0,
                    help="index of webcam video source")
    ap.add_argument("-o", "--output", type=str,
                    help="path to optional output video file")
    # confidence default 0.4
    ap.add_argument("-c", "--confidence", type=float, default=0.4,
                    help="minimum probability to filter weak detections")
    ap.add_argument("-s", "--skip-frames", type=int, default=30,
                    help="# of skip frames between detections")
    args = vars(ap.parse_args())
    return args

# def send_mail():
#     # function to send the email alerts
#     Mailer().send(config["Email_Receive"])

def log_data(move_in, in_time, move_out, out_time):
    # function to log the counting data
    data = [move_in, in_time, move_out, out_time]
    # transpose the data to align the columns properly
    export_data = zip_longest(*data, fillvalue='')

    with open('utils/data/logs/counting_data.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if myfile.tell() == 0:  # check if header rows are already existing
            wr.writerow(("Move In", "In Time", "Move Out", "Out Time"))
            wr.writerows(export_data)

def people_counter():
    # main function for people_counter.py
    args = parse_arguments()
    # initialize the list of class labels
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]

    # load our serialized model from disk
    net = cv2.dnn.readNetFromTensorflow(args["model"])

    # if a video path was not supplied, grab a reference to the webcam
    if not args.get("input", False):
        logger.info("Starting the webcam stream..")
        vs = cv2.VideoCapture(args["input"])
        time.sleep(2.0)

    # otherwise, grab a reference to the video file
    else:
        logger.info("Starting the video..")
        vs = cv2.VideoCapture(args["input"])
        # initialize the video writer (we'll instantiate later if need be)
    writer = None

    # initialize the frame dimensions (we'll set them as soon as we read the first frame from the video)
    W = None
    H = None

    # instantiate our centroid tracker, then initialize a list to store each of our dlib correlation trackers, followed by a dictionary to map each unique object ID to a TrackableObject
    ct = CentroidTracker(max_disappeared=40, max_distance=50)
    trackers = []
    trackable_objects = {}

    # initialize the total number of frames processed
    total_frames = 0
    # initialize the total number of objects moved in/out of the frame
    total_move_in = 0
    total_move_out = 0

    # start the frames per second throughput estimator
    fps = FPS().start()

    def run_inference(frame):
        # construct a blob from the frame, pass it through the network, obtain the detections and predictions
        blob = cv2.dnn.blobFromImage(frame, size=(300, 300), swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward()

        # initialize the list of bounding box rectangles and corresponding confidence scores
        boxes = []
        confidences = []

        # loop over the detections
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the confidence is greater than the minimum confidence
            if confidence > args["confidence"]:
                # compute the (x, y)-coordinates of the bounding box for the object
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")

                # update the list of bounding box rectangles and confidences
                boxes.append((startX, startY, endX, endY))
                confidences.append(confidence)

        # apply non-maxima suppression to suppress weak, overlapping bounding boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"], config["NMS_Threshold"])

        # loop over the bounding box indices
        for i in indices.flatten():
            # extract the bounding box coordinates
            (startX, startY, endX, endY) = boxes[i]

            # construct a dlib rectangle object from the bounding box coordinates and then start the dlib correlation tracker
            tracker = dlib.correlation_tracker()
            rect = dlib.rectangle(startX, startY, endX, endY)
            tracker.start_track(rgb, rect)

            # add the tracker to our list of trackers so we can utilize it during skip frames
            trackers.append(tracker)

    # ...

def update_counting(frame, move_in, move_out):
    rects = []  # Initialize an empty list for bounding box coordinates

    # Loop over the trackers
    for tracker in trackers:
        # Update the tracker and grab the updated position
        tracker.update(frame)
        pos = tracker.get_position()

        # Unpack the position object
        startX = int(pos.left())
        startY = int(pos.top())
        endX = int(pos.right())
        endY = int(pos.bottom())

        # Add the bounding box coordinates and object ID to the rects list
        rects.append((startX, startY, endX, endY, object_id))

    # Use the centroid tracker to associate the (1) old object centroids with (2) the newly computed object centroids
    objects = ct.update(rects)

    # Loop over the tracked objects
    for (object_id, centroid) in objects.items():
        # Check to see if a trackable object exists for the current object ID
        to = trackable_objects.get(object_id, None)

        # If there is no existing trackable object, create one
        if to is None:
            to = TrackableObject(object_id, centroid)

        # Otherwise, if there is a trackable object and its position changed, increment the movement count
        else:
            if not to.moved and centroid[1] < H // 2:
                move_out += 1
                to.moved = True
            elif not to.moved and centroid[1] > H // 2:
                move_in += 1
                to.moved = True

        # Store the trackable object in our dictionary
        trackable_objects[object_id] = to

        # Draw both the ID of the object and the centroid of the object on the output frame
        text = "ID {}".format(object_id)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

        # Check if we should write the frame to disk
        if args["output"] is not None and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 30, (frame.shape[1], frame.shape[0]), True)

        # If the writer is not None, write the frame with the tracked objects to disk
        if writer is not None:
            writer.write(frame)

        # Show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    #
    # return move_in, move_out


    # ...



    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] Approximate FPS: {:.2f}".format(fps.fps()))

    # check if we need to release the video writer pointer
    if writer is not None:
        writer.release()

    # if we are not using a video file, stop the camera video stream
    if not args.get("input", False):
        vs.stop()

    # otherwise, release the video file pointer
    else:
        vs.release()

    # close any open windows
    cv2.destroyAllWindows()
