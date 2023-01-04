import RPi.GPIO as GPIO
import time

time.sleep(20)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Defining motor pins

in1 = 6
in2 = 13
in3 = 19
in4 = 26
ena = 23
enb = 24
GPIO_TRIGGER = 22
GPIO_ECHO = 27
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
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

def stop():
    print ("stop")
    GPIO.output(in1, 0)
    GPIO.output(in2, 0)
    GPIO.output(in3, 0)
    GPIO.output(in4, 0)
    pa.ChangeDutyCycle(0)
    pb.ChangeDutyCycle(0)
    
def forward():
    GPIO.output(in1, 1)
    GPIO.output(in2, 0)
    GPIO.output(in3, 1)
    GPIO.output(in4, 0)
    print ("forward")
    pa.ChangeDutyCycle(75)
    pb.ChangeDutyCycle(75)

def back():
    GPIO.output(in1, 0)
    GPIO.output(in2, 1)
    GPIO.output(in3, 0)
    GPIO.output(in4, 1)
    print ("back")
    pa.ChangeDutyCycle(75)
    pb.ChangeDutyCycle(75)

def left():
    GPIO.output(in1, 0)
    GPIO.output(in2, 0)
    GPIO.output(in3, 1)
    GPIO.output(in4, 0)
    print ("left")
    pa.ChangeDutyCycle(75)
    pb.ChangeDutyCycle(0)

def right():
    GPIO.output(in1, 1)
    GPIO.output(in2, 0)
    GPIO.output(in3, 0)
    GPIO.output(in4, 0)
    print ("right")
    pa.ChangeDutyCycle(0)
    pb.ChangeDutyCycle(75)
       
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance

def control():
    stop()
    time.sleep(2)
    back()
    time.sleep(1)
    stop()
    time.sleep(2)
    right()
    time.sleep(0.5)
    stop()
    time.sleep(2)
    
stop()

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            if dist < 25:
                control() 
            else:
                forward()
                
                
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

    
    
   
   
