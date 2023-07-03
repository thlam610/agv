import RPi.GPIO as GPIO
import time
import cv2
from flask import Flask, render_template, Response, request

app = Flask(__name__)
camera = None

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Defining motor pins

in1 = 6
in2 = 13
in3 = 19
in4 = 26
ena = 23
enb = 24
TRIG1 = 22
ECHO1 = 27
TRIG2 = 17
ECHO2 = 18
TRIG3 = 25
ECHO3 = 28

# Set up GPIO pins
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)
 
#set GPIO direction (IN / OUT)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setup(ena,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)
pb = GPIO.PWM(ena, 1000)
pa = GPIO.PWM(enb, 1000)
pa.start(0)
pb.start(0)
time.sleep(3)

# Motor control functions
def move_forward():
    GPIO.output(in1, 1)
    GPIO.output(in2, 0)
    GPIO.output(in3, 1)
    GPIO.output(in4, 0)
    print ("forward")
    pa.ChangeDutyCycle(75)
    pb.ChangeDutyCycle(100)
    pass

def move_backward():
    GPIO.output(in1, 0)
    GPIO.output(in2, 1)
    GPIO.output(in3, 0)
    GPIO.output(in4, 1)
    print ("back")
    pa.ChangeDutyCycle(75)
    pb.ChangeDutyCycle(100)
    pass

def turn_left():
    GPIO.output(in1, 0)
    GPIO.output(in2, 0)
    GPIO.output(in3, 1)
    GPIO.output(in4, 0)
    print ("left")
    pa.ChangeDutyCycle(75)
    pb.ChangeDutyCycle(0)
    pass

def turn_right():
    GPIO.output(in1, 1)
    GPIO.output(in2, 0)
    GPIO.output(in3, 0)
    GPIO.output(in4, 0)
    print ("right")
    pa.ChangeDutyCycle(0)
    pb.ChangeDutyCycle(100)
    pass

def stop():
    print ("stop")
    GPIO.output(in1, 0)
    GPIO.output(in2, 0)
    GPIO.output(in3, 0)
    GPIO.output(in4, 0)
    pa.ChangeDutyCycle(0)
    pb.ChangeDutyCycle(0)
    pass

def avoid_right():
    stop()
    time.sleep(2)
    move_backward()
    time.sleep(1)
    stop()
    time.sleep(2)
    turn_right()
    time.sleep(0.5)
    stop()
    time.sleep(2)
    pass

def avoid_left():
    stop()
    time.sleep(2)
    move_backward()
    time.sleep(1)
    stop()
    time.sleep(2)
    turn_left()
    time.sleep(0.5)
    stop()
    time.sleep(2)
    pass

def measure_distance(trig_pin, echo_pin):
    # Send ultrasonic pulse
    GPIO.output(trig_pin, True)
    time.sleep(0.00001)
    GPIO.output(trig_pin, False)

    # Wait for echo response
    pulse_start = time.time()
    pulse_end = time.time()
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()

    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2  # Speed of sound = 343 m/s
    distance = round(distance, 2)

    return distance

def initialize_camera():
    global camera
    camera = cv2.VideoCapture(0)
    # Set camera properties for optimization
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)

def generate_frames():
    global camera
    while True:
        # Capture a frame from the camera
        success, frame = camera.read()
        if not success:
            break

        # Perform any necessary image processing or operations here

        # Compress the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame = jpeg.tobytes()

        # Yield the frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_status')
def toggle_status():
    global status
    status = 1 - status  # Toggle the status between 0 and 1
    return '', 200

def keyboard_input():
    global status
    key = request.form['key']
    if key == 'Tab':
        status = 1 - status  # Toggle the status between 0 and 1
    return '', 200

@app.route('/measure_distance')
def measure_distance_route():
    distance_1 = measure_distance(TRIG1, ECHO1)
    distance_2 = measure_distance(TRIG2, ECHO2)
    distance_3 = measure_distance(TRIG3, ECHO3)

    return render_template('index.html', distance_1=distance_1, distance_2=distance_2, distance_3=distance_3, status=status)

@app.route('/control', methods=['POST'])
def control():
    key = request.form['key']
    if status == 0:  # Auto running mode
        distance_1 = measure_distance(TRIG1, ECHO1)
        distance_2 = measure_distance(TRIG2, ECHO2)
        distance_3 = measure_distance(TRIG3, ECHO3)
        if (distance_1 < 20):
            if (distance_2 < 20):
                avoid_right()
            else:
                avoid_left()
        else:
            move_forward()
        pass
    else:  # Manual control mode
        if key == 'ArrowUp':  # Forward
            move_forward()
            time.sleep(1)
            pass
        elif key == 'ArrowDown':  # Backward
            move_backward()
            time.sleep(1)
            pass
        elif key == 'ArrowLeft':  # Left
            turn_left()
            time.sleep(1)
            pass
        elif key == 'ArrowRight':  # Right
            turn_right()
            time.sleep(1)
            pass
        elif key == ' ':  # Space (Stop)
            stop()
            pass
    return '', 200

if __name__ == '__main__':
    try:
        while True:
            initialize_camera()
            measure_distance_route()
            control()
            app.run(host='0.0.0.0', port=5000, debug=True)

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()