

import cv2 as cv
import mediapipe as mp
import math


from libss import handtool
import beepplayer


PRESS_DEADZONE = 40


mp_hands_solution = mp.solutions.hands
hands = mp_hands_solution.Hands(
    model_complexity=1
)


two_hand_press_list = {
    "left_thumb"  : False,
    "left_index"  : False,
    "left_middle" : False,
    "left_ring"   : False,
    "left_pinky"  : False,
    "right_thumb"   : False,
    "right_index"   : False,
    "right_middle"  : False,
    "right_ring"    : False,
    "right_pinky"   : False
}
previous_two_hand_press_list = {
    "left_thumb"  : False,
    "left_index"  : False,
    "left_middle" : False,
    "left_ring"   : False,
    "left_pinky"  : False,
    "right_thumb"   : False,
    "right_index"   : False,
    "right_middle"  : False,
    "right_ring"    : False,
    "right_pinky"   : False
}


# --- Helper Function to Draw Dotted Lines ---
def draw_dotted_line(img, pt1, pt2, color, thickness=1, gap=10) :
    # Calculate distance between the two points
    dist = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
    
    if dist == 0:
        return

    # Calculate how many dots to draw based on the gap
    dots_count = int(dist // gap)
    
    for i in range(dots_count + 1):
        # Linear Interpolation (find point along the line)
        alpha = i / dots_count if dots_count > 0 else 0
        x = int(pt1[0] * (1 - alpha) + pt2[0] * alpha)
        y = int(pt1[1] * (1 - alpha) + pt2[1] * alpha)
        
        # Draw a small 1px dot
        cv.circle(img, (x, y), thickness, color, -1)



def main() :
    
    
    # setup ----
    capture = cv.VideoCapture(0)

    while capture.isOpened() :

        ret, frame = capture.read()
        if not ret: break
        

        key = cv.waitKey(1) & 0xFF

        if key == ord("e") or key == ord("E") : break



        frame = cv.flip(frame, 1)

        RGBframe = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        result = hands.process(RGBframe)
        for finger in two_hand_press_list.keys() :
            two_hand_press_list[finger] = False

        
        ## processing and drawing handlandmarks ----
        if result.multi_hand_landmarks :
            # for each hand  in  multiple hand
            for handLms in result.multi_hand_landmarks :
                
                h, w, c = frame.shape
                
                
                ### Store all landmark coordinates and draw circle ----
                
                # start
                lm_points = {}
                lm_raw_points = {}
                most_right = 0
                # end
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_points[id]     = (cx, cy)
                    lm_raw_points[id] = lm
                    if cx > most_right : most_right = cx
                    
                    cv.circle(frame, lm_points[id], 5, (255, 0, 0), -1)
                    
                hand_side = side_of(most_right, frame)

                ### Draw Dotted Connections ----
                # Loop through the defined hand connections (e.g., wrist -> thumb)
                for connection in mp_hands_solution.HAND_CONNECTIONS:
                    start_idx = connection[0]
                    end_idx   = connection[1]
                    
                    if start_idx in lm_points and end_idx in lm_points:
                        pt1 = lm_points[start_idx]
                        pt2 = lm_points[end_idx]
                        
                        # Call our custom dotted line function
                        # Color: White (255, 255, 255), Thickness: 1px, Gap: 5px
                        draw_dotted_line(frame, pt1, pt2, (255, 255, 255), thickness=1, gap=5)
                



                ### doinge extraction ----
                
                if check_press(
                    lm_points[handtool.list_landmark.THUMB_TIP], 
                    lm_points[handtool.list_landmark.THUMB_MCP],
                    PRESS_DEADZONE + 10
                ) :
                    if hand_side == "left" :
                        two_hand_press_list["left_thumb"] = True
                        if previous_two_hand_press_list["left_thumb"] == False :
                            beepplayer.play_note_threaded(beepplayer.note_list.Sol)
                    elif hand_side == "right" :
                        two_hand_press_list["right_thumb"] = True
                        if previous_two_hand_press_list["right_thumb"] == False :
                            beepplayer.play_note_threaded(beepplayer.note_list.Do)
                            
                    

                
                
        # verbose
        # for finger in two_hand_press_list.keys() :
        #     if two_hand_press_list[finger] :
        #         print(finger)
                


        cv.imshow("Frame", frame)
    
    
    
    
    capture.release()
    cv.destroyAllWindows()



def side_of(landmark_x, frame) :
    # if its on the left
    if landmark_x > frame.shape[0] / 2 :
        return "left"
    else :
        return "right"

def check_press(landmark_of_tip, landmark_of_mcp, deadzone=PRESS_DEADZONE) :
    # landmark_of_tip = (x1, y1)
    # landmark_of_mcp = (x2, y2)
    
    # Calculate difference in X and Y
    dx = landmark_of_tip[0] - landmark_of_mcp[0]
    dy = landmark_of_tip[1] - landmark_of_mcp[1]
    
    # Calculate Euclidean distance
    distance = math.hypot(dx, dy)
    
    if distance <= deadzone:
        return True
    return False
        
        



def just_pressed(finger) :
    pass
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

if __name__ == "__main__":
    main()

