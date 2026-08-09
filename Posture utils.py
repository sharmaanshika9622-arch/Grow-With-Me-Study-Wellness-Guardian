"""
posture_utils.py
-----------------
Calculates a simple "spine slouch angle" using shoulder and ear
landmarks from MediaPipe Pose.

The idea: when you sit up straight, your ear is roughly above your
shoulder (near-vertical line). When you slouch forward, your ear
moves forward relative to your shoulder, increasing the angle from
vertical. We use that angle as our slouch indicator.
"""

import math


def calculate_slouch_angle(shoulder, ear):
    """
    shoulder, ear: each a tuple/list of (x, y) in normalized image
    coordinates (0-1), as returned by MediaPipe landmarks.

    Returns the angle (in degrees) between the shoulder-ear line
    and the vertical axis. 0 degrees = perfectly upright.
    Larger angle = more forward slouch.
    """
    dx = ear[0] - shoulder[0]
    dy = ear[1] - shoulder[1]

    # atan2(dx, -dy) gives angle from vertical (screen y grows downward,
    # so we negate dy to treat "up" as the reference direction)
    angle_rad = math.atan2(abs(dx), abs(dy) if dy != 0 else 1e-6)
    angle_deg = math.degrees(angle_rad)
    return angle_deg


def is_slouching(shoulder, ear, angle_threshold_deg=20):
    """
    Returns True if the calculated angle exceeds the threshold,
    meaning the student is likely slouching forward.

    angle_threshold_deg: tune this during testing. ~15-20 degrees
    is a reasonable starting point for "leaning forward noticeably".
    """
    angle = calculate_slouch_angle(shoulder, ear)
    return angle > angle_threshold_deg, angle


def get_landmarks_from_pose_result(pose_landmarks, image_width, image_height):
    """
    Extracts the (x, y) pixel coordinates of the right shoulder and
    right ear from a MediaPipe Pose result.

    We use the RIGHT side of the body (from the camera's perspective,
    this is usually the side more visible in a typical study desk
    webcam angle). You can switch to LEFT_SHOULDER / LEFT_EAR if that
    works better for your camera setup.
    """
    import mediapipe as mp
    mp_pose = mp.solutions.pose

    shoulder_lm = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    ear_lm = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR]

    shoulder = (shoulder_lm.x * image_width, shoulder_lm.y * image_height)
    ear = (ear_lm.x * image_width, ear_lm.y * image_height)

    return shoulder, ear
