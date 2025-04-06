import GUI
import HAL
import cv2
import numpy as np
from collections import deque


Kp = 0.6  
Ki = 0.0001  
Kd = 0.2  

previous_error = 0
integral = 0
previous_cx = None  

alpha = 0.5  
previous_cx_values = deque(maxlen=5)  

max_steering_rate = 0.1  
current_steering = 0  

max_integral = 50  

last_known_cx = None  

def get_line_position(image):
    
    global last_known_cx  
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            last_known_cx = int(M["m10"] / M["m00"])  
            return last_known_cx  
    
    return last_known_cx  

def pid_control(cx, img_width):
   
    global previous_error, integral, previous_cx

    if previous_cx is None:
        previous_cx = cx
    smoothed_cx = alpha * previous_cx + (1 - alpha) * cx
    previous_cx = smoothed_cx  

    previous_cx_values.append(smoothed_cx)
    final_cx = sum(previous_cx_values) / len(previous_cx_values)

    center = img_width // 2
    error = center - final_cx  

    if abs(error) < 10:
        return 0, abs(error)  

    integral += error
    integral = max(-max_integral, min(max_integral, integral))  

    derivative = error - previous_error
    correction = Kp * error + Ki * integral + Kd * derivative
    previous_error = error

    correction = max(-1.5, min(1.5, correction))  

    return correction, abs(error)  

def apply_steering(steering):
   
    global current_steering
    if abs(steering - current_steering) > max_steering_rate:
        steering = current_steering + np.sign(steering - current_steering) * max_steering_rate
    current_steering = steering
    HAL.setW(steering)

while True:
    frame = HAL.getImage()  

    if frame is not None:
        cx = get_line_position(frame)  

        if cx is not None:
            steering, error_magnitude = pid_control(cx, frame.shape[1])  

            if abs(steering) > 0.8:  
                speed = 1.5    
            elif abs(steering) < 0.3:
                speed = 2.5  
            else:
                speed = 3.0  

            HAL.setV(speed)  
            apply_steering(steering)  

        GUI.showImage(frame)