"""
age_profiles.py
----------------
This is the "Grow-With-Me" brain of the project.

Instead of using ONE fixed rule for everyone (like most posture apps do),
we define different thresholds and messages for different age groups.
This is the part you should highlight in your viva as the "innovative"
piece — the AI's tolerance and coaching tone changes based on the
student's age/grade.
"""

# Each profile defines:
# - max_slouch_seconds: how long bad posture is allowed before we alert
# - max_screen_stare_seconds: how long without a blink/break before eye-strain alert
# - min_blink_rate: blinks per minute below this = eye strain risk
# - message_style: which set of messages to use (playful / habit / analytical)

AGE_PROFILES = {
    "lower": {  # roughly 5-9 years
        "label": "Lower Classes (5-9 yrs)",
        "max_slouch_seconds": 20,
        "max_screen_stare_seconds": 90,
        "min_blink_rate": 12,       # blinks per minute
        "message_style": "playful",
    },
    "middle": {  # roughly 10-14 years
        "label": "Middle Classes (10-14 yrs)",
        "max_slouch_seconds": 40,
        "max_screen_stare_seconds": 150,
        "min_blink_rate": 10,
        "message_style": "habit",
    },
    "higher": {  # roughly 15-18 years
        "label": "Higher Classes (15-18 yrs)",
        "max_slouch_seconds": 60,
        "max_screen_stare_seconds": 240,
        "min_blink_rate": 8,
        "message_style": "analytical",
    },
}

# Messages shown for each style, so the SAME event (e.g. "bad posture detected")
# is communicated differently depending on age.
MESSAGES = {
    "playful": {
        "posture": "Ouch! Buddy the Bear says: sit up tall like a superhero! 🦸",
        "eye_strain": "Blink, blink! Your eyes want a little rest. Look far away for 10 seconds!",
        "good_session": "Wow, great sitting today! You're a study star! ⭐",
    },
    "habit": {
        "posture": "Posture check: you've been slouching a bit. Straighten up — small habits add up!",
        "eye_strain": "Your eyes have been on the screen a while. Try the 20-20-20 rule: look 20 feet away for 20 seconds.",
        "good_session": "Nice work — you kept steady posture for this whole session. Keep the habit going!",
    },
    "analytical": {
        "posture": "Posture alert: spine angle has been outside the healthy range for a while. Consider adjusting your seating.",
        "eye_strain": "Blink rate has dropped below the healthy threshold, indicating early eye strain. A short break is recommended.",
        "good_session": "Session summary: posture and eye-strain metrics stayed within healthy range throughout.",
    },
}


def get_profile(age_group: str) -> dict:
    """Return the threshold profile for a given age group key."""
    if age_group not in AGE_PROFILES:
        raise ValueError(
            f"Unknown age_group '{age_group}'. Choose from: {list(AGE_PROFILES.keys())}"
        )
    return AGE_PROFILES[age_group]


def get_message(age_group: str, event: str) -> str:
    """Return the right-tone message for an event ('posture', 'eye_strain', 'good_session')."""
    profile = get_profile(age_group)
    style = profile["message_style"]
    return MESSAGES[style][event]
