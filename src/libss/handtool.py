

from enum import IntEnum
import math


import numpy as np
import mediapipe
import cv2


class list_landmark(IntEnum) : 
    WRIST     = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP  = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20

def get_finger_points(landmark: int) :
    return (landmark, landmark+1, landmark+2, landmark+3)
    

class list_bounding_preset() :
    ALL = (
        0, 
        1 , 2 , 3 , 4 , 5 , 6 , 7 , 8 , 9 , 10, 
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    )
    ALL_NO_INDEX_TIP = (
        0, 
        1 , 2 , 3 , 4 , 5 , 6 , 7     , 9 , 10, 
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    )
    STATIC = (
        list_landmark.INDEX_FINGER_MCP,
        list_landmark.MIDDLE_FINGER_MCP,
        list_landmark.RING_FINGER_MCP,
        list_landmark.PINKY_MCP,
        list_landmark.WRIST,
    )
    STATIC_EXTENDED = (
        list_landmark.INDEX_FINGER_MCP,
        list_landmark.MIDDLE_FINGER_MCP,
        list_landmark.RING_FINGER_MCP,
        list_landmark.PINKY_MCP,
        list_landmark.WRIST,
        list_landmark.THUMB_IP,
    )


def npArrayXY(value) :

    return np.array( (value.x, value.y) )

def getPositional(landmark, frame) :
    return ( int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0]) )

def getDistance(mark1, mark2) :

    point1 , point2 = npArrayXY(mark1), npArrayXY(mark2)

    direction = np.array( point1 - point2 )

    distance = (direction[0]**2 + direction[1]**2)**0.5

    distance = round(distance, 2)

    return distance

def getRelDistance(mark1, mark2, based_scaler) : # inaccuracy most of .2 value
    distance = getDistance(
        mark1,
        mark2
    ) * (370 / based_scaler)

    return round(distance, 2)

def getHandLength(landmark) :
    
    pivot = landmark[list_landmark.WRIST]
    finger_pivot_middle = landmark[list_landmark.MIDDLE_FINGER_DIP]

    distance = getDistance(
        npArrayXY(pivot),
        npArrayXY(finger_pivot_middle)
    )

    distance = min( distance, 1.0)

    distance = 1.0 - distance

    distance = max(distance, 0.1)

    distance = round(distance, 2)

    print("handlenght is deprecated use bound instead")

    return distance

def getAngle(mark1) : 

    radian = math.atan2( mark1.y, mark1.x)

    degree = math.degrees(radian)

    return round(degree, 2)

def getHandBounding(
        landmarks, 
        frame, 
        draw=False, 
        returnbestvalue=False, 
        returnbothvalue=False,
        bounding_preset=list_bounding_preset.STATIC_EXTENDED
    ) :

    bounding_box = []

    for index in bounding_preset : 
        point = landmarks[index]
        
        bounding_box.append( getPositional(point, frame) )
    
    bounding_box = np.array( bounding_box )

    x, y, w, h = cv2.boundingRect( bounding_box )

    if draw : cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

    best_value = (w**2 + h**2)**0.5
    bounding = (x, y, w, h)
    
    if returnbothvalue : 
        return (best_value, bounding)
    
    elif returnbestvalue : 
        return best_value
    
    return bounding

def getMarkInBounding(mark, boundingXYWH, frame, array=False) :

    x, y, w, h = boundingXYWH[0], boundingXYWH[1], boundingXYWH[2], boundingXYWH[3]

    if array : markX, markY = int(mark[0] * frame.shape[1]), int(mark[1] * frame.shape[0])
    else     : markX, markY = int(mark.x * frame.shape[1]), int(mark.y * frame.shape[0])

    # if markX < x or markX > x + w :
    # if markX < x or markX > x + w or markY < y or markY < y + h :
    #     return False
    
    # return True
    return not(
    (markX < x) or
    (markX > x + w) or
    (markY < y) or
    (markY > y + h)
    )

def new_hands(detect_hand_amount=1, detect_conf=0.5, track_conf=0.5) :
    return mediapipe.solutions.hands.Hands(
        max_num_hands=detect_hand_amount, 
        min_detection_confidence=detect_conf, 
        min_tracking_confidence=track_conf
    )

def getBoundingCenter( bounding ):
    x, y, w, h = bounding
    cx = x + w / 2
    cy = y + h / 2
    return (int(cx), int(cy))

def simpleExtract(frame, new_hands, draw_frame=False, bounding_preset=list_bounding_preset.STATIC_EXTENDED) : #return all hand landmarks and drew frame

    mp_draw = mediapipe.solutions.drawing_utils
    mp_hand = mediapipe.solutions.hands
    hands = new_hands

    results = hands.process(frame)
    multihand_landmarks = results.multi_hand_landmarks # this store the right and left hand only

    multihands = [] #return all hand landmarks
    registered_bounding = [ (0, 0, 0, 0) ]

    if multihand_landmarks :
        for landmarks in multihand_landmarks :

            if draw_frame : 
                mp_draw.draw_landmarks(
                    frame, 
                    landmarks, 
                    mediapipe.solutions.hands.HAND_CONNECTIONS
                )

                bounding = getHandBounding(landmarks.landmark, frame, draw=draw_frame, bounding_preset=bounding_preset)
                center = np.array( getBoundingCenter(bounding), dtype=float )
                center[0], center[1] = center[0] / frame.shape[1], center[1] / frame.shape[0]

                for bounds in registered_bounding :
                    is_inside = getMarkInBounding(center, bounds, frame, array=True)
                    if not is_inside :
                        registered_bounding.append(bounding)

                        landmark = landmarks.landmark

                        multihands.append(landmark)

    return multihands, frame

def drawConnectedLine(frame, mark1, mark2, radius, thickness, array=False) :

    # point1, point2 = npArrayXY(mark1), npArrayXY(mark2)
    point1, point2 = mark1, mark2
    if array : 
        pos1 = point1
        pos2 = point2
    else : 
        pos1 = getPositional(
            point1, 
            frame
        )
        pos2 = getPositional(
            point2, 
            frame
        )

    cv2.circle(
        frame,
        pos1,
        radius,
        (255, 255, 255),
        2
    )
    cv2.circle(
        frame,
        pos2,
        radius,
        (255, 255, 255),
        2
    )

    cv2.line(
        frame,
        pos1,
        pos2,
        (255, 255, 255),
        thickness
    )

