"""
main.py
-------
Grow-With-Me Study Wellness Guardian — main application.

Run this file. It opens your webcam, tracks posture (spine slouch) and
eye strain (blink rate), and gives age-appropriate nudges based on the
AGE_GROUP you set below.

Controls while running:
  - Press 'q' to quit and see your session summary.

Before running, install dependencies:
    pip install opencv-python mediapipe

Note: this needs an actual webcam and a display, so run it on your own
laptop/PC — not in a cloud sandbox.
"""

import time
import cv2
import mediapipe as mp

from age_profiles import get_profile, get_message
from posture_utils import is_slouching, get_landmarks_from_pose_result
from eye_strain_utils import eye_aspect_ratio, BlinkTracker, LEFT_EYE, RIGHT_EYE

# ----------------------------------------------------------------------
# 1. SET THE STUDENT'S AGE GROUP HERE (this is the "grow with me" switch)
#    Options: "lower", "middle", "higher"
# ----------------------------------------------------------------------
AGE_GROUP = "middle"


def run():
    profile = get_profile(AGE_GROUP)
    print(f"Starting session for: {profile['label']}")

    mp_pose = mp.solutions.pose
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )

    blink_tracker = BlinkTracker(window_seconds=60)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam. Check your camera connection/permissions.")
        return

    slouch_start_time = None       # when continuous slouching began
    last_alert_time = 0
    alert_cooldown = 8             # seconds between repeated alerts (avoid spamming)
    session_start = time.time()
    posture_alert_count = 0
    eye_alert_count = 0

    print("Session started. Press 'q' to stop.")

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)  # mirror for a natural selfie-view
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ---------------- POSTURE CHECK ----------------
        pose_result = pose.process(rgb_frame)
        slouch_flag = False
        angle = None

        if pose_result.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )
            shoulder, ear = get_landmarks_from_pose_result(
                pose_result.pose_landmarks, w, h
            )
            slouch_flag, angle = is_slouching(shoulder, ear, angle_threshold_deg=20)

        now = time.time()

        if slouch_flag:
            if slouch_start_time is None:
                slouch_start_time = now
            slouch_duration = now - slouch_start_time
        else:
            slouch_start_time = None
            slouch_duration = 0

        if (
            slouch_duration > profile["max_slouch_seconds"]
            and (now - last_alert_time) > alert_cooldown
        ):
            print("[POSTURE ALERT]", get_message(AGE_GROUP, "posture"))
            last_alert_time = now
            posture_alert_count += 1
            slouch_start_time = now  # reset so we don't alert every frame

        # ---------------- EYE STRAIN CHECK ----------------
        face_result = face_mesh.process(rgb_frame)
        if face_result.multi_face_landmarks:
            face_landmarks = face_result.multi_face_landmarks[0]
            landmark_points = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]

            left_eye_pts = [landmark_points[i] for i in LEFT_EYE]
            right_eye_pts = [landmark_points[i] for i in RIGHT_EYE]

            left_ear = eye_aspect_ratio(left_eye_pts)
            right_ear = eye_aspect_ratio(right_eye_pts)
            avg_ear = (left_ear + right_ear) / 2.0

            blink_tracker.update(avg_ear)
            blink_rate = blink_tracker.blinks_per_minute()

            # Only judge blink rate after we've collected ~20s of data,
            # otherwise the rate estimate is too noisy.
            elapsed = now - session_start
            if elapsed > 20 and blink_rate < profile["min_blink_rate"]:
                if (now - last_alert_time) > alert_cooldown:
                    print("[EYE STRAIN ALERT]", get_message(AGE_GROUP, "eye_strain"))
                    last_alert_time = now
                    eye_alert_count += 1

            cv2.putText(
                frame, f"Blink rate: {blink_rate:.1f}/min", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        if angle is not None:
            cv2.putText(
                frame, f"Slouch angle: {angle:.1f} deg", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )

        cv2.putText(
            frame, f"Profile: {profile['label']}", (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
        )

        cv2.imshow("Grow-With-Me Study Wellness Guardian", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # ---------------- SESSION SUMMARY ----------------
    total_minutes = (time.time() - session_start) / 60
    print("\n--- Session Summary ---")
    print(f"Age profile: {profile['label']}")
    print(f"Session length: {total_minutes:.1f} minutes")
    print(f"Posture alerts: {posture_alert_count}")
    print(f"Eye strain alerts: {eye_alert_count}")

    if posture_alert_count == 0 and eye_alert_count == 0:
        print(get_message(AGE_GROUP, "good_session"))


if __name__ == "__main__":
    run()
