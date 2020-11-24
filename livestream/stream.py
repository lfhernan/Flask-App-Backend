# ------------------------
#   USAGE
# ------------------------
# python webstreaming.py --ip 0.0.0.0 --port 8000

from livestream.motionservice.motiondetector import SingleMotionDetector
from imutils.video import VideoStream
import threading
import datetime
import imutils
import time
import cv2

# Initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs are viewing the stream)
output_frame = None
lock = threading.Lock()

# Initialize the video stream and allow the camera sensor to warmup
video_stream = VideoStream(src=0).start()
time.sleep(2.0)

def detect_motion(frame_count):
    # grab global references to the video stream, output frame and lock variables
    global video_stream, output_frame, lock
    # initialize the motion detector and the total number of frames read thus far
    smd = SingleMotionDetector(accum_weight=0.1)
    total = 0
    # loop over frames from the video stream
    while True:
        # read the next frame from the video stream, resize it,
        # convert the frame to grayscale and blur it
        frame = video_stream.read()
        frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
        # if the total number of frames has reached a sufficient number to construct a reasonable background model,
        # then continue to process the frame
        if total > frame_count:
            # detect motion in the image
            motion = smd.detect(gray)
            # check to see if motion was found in the frame
            if motion is not None:
                # unpack the tuple and draw the box surrounding the "motion area" on the output frame
                (threshold, (minX, minY, maxX, maxY)) = motion
                cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
        # update the background model and increment the total number of frames read thus far
        smd.update(gray)
        total += 1
        # acquire the lock, set the output frame and release the lock
        with lock:
            output_frame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global output_frame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip the iteration of the loop
            if output_frame is None:
                continue
            # encode the frame in JPEG format
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

# release the video stream pointer
video_stream.stop()