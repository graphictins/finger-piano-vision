import cv2 as cv
import mediapipe as mp
import math
import time

# --- ASSUMING THESE EXIST IN YOUR FOLDER ---
from libss import handtool
import beepplayer

PRESS_DEADZONE = 30 # Tweak this based on your camera distance

mp_hands_solution = mp.solutions.hands
hands = mp_hands_solution.Hands(
    model_complexity=1,
    max_num_hands=2 # Ensure we can see both hands
)

# --- CONFIGURATION ---
# Map specific fingers to specific notes
FINGER_NOTES = {
    "left_thumb":  "Do",
    "left_index":  "Re",
    "left_middle": "Mi",
    "left_ring":   "Fa",
    "left_pinky":  "Sol",
    "right_thumb":  "La",
    "right_index":  "Ti",
    "right_middle": "Do_High",
    "right_ring":   "Re_High",
    "right_pinky":  "Mi_High"
}

# Current State
current_press_state = { k: False for k in FINGER_NOTES.keys() }
# Previous State (for "Just Pressed" logic)
previous_press_state = { k: False for k in FINGER_NOTES.keys() }


def draw_dotted_line(img, pt1, pt2, color, thickness=1, gap=10) :
    dist = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
    if dist == 0: return
    dots_count = int(dist // gap)
    for i in range(dots_count + 1):
        alpha = i / dots_count if dots_count > 0 else 0
        x = int(pt1[0] * (1 - alpha) + pt2[0] * alpha)
        y = int(pt1[1] * (1 - alpha) + pt2[1] * alpha)
        cv.circle(img, (x, y), thickness, color, -1)

def check_press(landmark_of_tip, landmark_of_mcp, deadzone=PRESS_DEADZONE) :
    dx = landmark_of_tip[0] - landmark_of_mcp[0]
    dy = landmark_of_tip[1] - landmark_of_mcp[1]
    distance = math.hypot(dx, dy)
    return distance <= deadzone

def side_of(landmark_x, frame_width) :
    # FIXED: Compare x against Width / 2
    if landmark_x < frame_width / 2 : # < because 0 is on the left
        return "left"
    else :
        return "right"

def main() :
    global current_press_state, previous_press_state
    
    capture = cv.VideoCapture(0)

    while capture.isOpened() :
        ret, frame = capture.read()
        if not ret: break

        # 1. Flip and Convert
        frame = cv.flip(frame, 1)
        RGBframe = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        h, w, c = frame.shape # Get dimensions once per frame

        # 2. Reset Current State for this new frame
        for key in current_press_state:
            current_press_state[key] = False

        # 3. Process Hands
        result = hands.process(RGBframe)
        
        if result.multi_hand_landmarks :
            for hand_index, handLms in enumerate(result.multi_hand_landmarks):
                
                # --- A. Extract Landmarks ---
                lm_points = {}
                most_right_x = 0 # To determine side
                
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_points[id] = (cx, cy)
                    
                    # Track X to determine if hand is left or right side of screen
                    if cx > most_right_x: most_right_x = cx
                    
                    # Draw visual
                    cv.circle(frame, lm_points[id], 5, (255, 0, 0), -1)

                # --- B. Determine Hand Side ---
                # (Note: MediaPipe has .multi_handedness, but we use your x-split logic here)
                # We use the wrist (0) or average X to determine side usually, 
                # but using your method:
                hand_side = side_of(lm_points[0][0], w) 

                # --- C. Draw Connections ---
                for connection in mp_hands_solution.HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx in lm_points and end_idx in lm_points:
                        draw_dotted_line(frame, lm_points[start_idx], lm_points[end_idx], (255, 255, 255), 1, 5)

                # --- D. Check Fingers (Loop instead of long if/else) ---
                # We define which landmarks correspond to which finger name suffix
                fingers_to_check = [
                    ("thumb",  handtool.list_landmark.THUMB_TIP,  handtool.list_landmark.THUMB_MCP),
                    ("index",  handtool.list_landmark.INDEX_FINGER_TIP,  handtool.list_landmark.INDEX_FINGER_MCP),
                    ("middle", handtool.list_landmark.MIDDLE_FINGER_TIP, handtool.list_landmark.MIDDLE_FINGER_MCP),
                    ("ring",   handtool.list_landmark.RING_FINGER_TIP,   handtool.list_landmark.RING_FINGER_MCP),
                    ("pinky",  handtool.list_landmark.PINKY_TIP,   handtool.list_landmark.PINKY_MCP),
                ]

                for f_name, tip_id, mcp_id in fingers_to_check:
                    # Construct key (e.g., "left_index")
                    full_key_name = f"{hand_side}_{f_name}"
                    
                    # Check if pressed
                    if check_press(lm_points[tip_id], lm_points[mcp_id]):
                        if full_key_name in current_press_state:
                            current_press_state[full_key_name] = True
                            
                            # Visual Feedback (Green when pressed)
                            cv.circle(frame, lm_points[tip_id], 10, (0, 255, 0), -1)

        # 4. --- AUDIO LOGIC (The "Rising Edge" Check) ---
        # We do this AFTER processing both hands
        for finger_key, is_pressed_now in current_press_state.items():
            
            # If Pressed NOW ... AND ... NOT Pressed BEFORE
            if is_pressed_now and not previous_press_state[finger_key]:
                
                # Get the note name
                note = FINGER_NOTES.get(finger_key)
                if note:
                    print(f"Playing {note} ({finger_key})")
                    beepplayer.play_note_threaded(note)

        # 5. --- UPDATE PREVIOUS STATE ---
        # This is where your code was broken. We simply copy the dictionary.
        previous_press_state = current_press_state.copy()

        # 6. UI
        cv.imshow("Finger Piano", frame)
        key = cv.waitKey(1) & 0xFF
        if key == ord("e") or key == ord("E") : break

    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main() 