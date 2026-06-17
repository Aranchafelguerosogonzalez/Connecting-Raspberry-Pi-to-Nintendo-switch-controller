import struct
import time
import RPi.GPIO as GPIO

# --- Motor pins ---
IN1, IN2 = 17, 27
IN3, IN4 = 22, 23
ENA, ENB = 18, 19

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB], GPIO.OUT)

pwm_a = GPIO.PWM(ENA, 100)
pwm_b = GPIO.PWM(ENB, 100)
pwm_a.start(0)
pwm_b.start(0)

def set_motors(left, right):
    if left > 0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif left < 0:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)

    if right > 0:
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    elif right < 0:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)

    pwm_a.ChangeDutyCycle(abs(left) * 100)
    pwm_b.ChangeDutyCycle(abs(right) * 100)

def normalize(val):
    return val / 32767.0

DEVICE = '/dev/input/js0'
EVENT_FORMAT = 'IhBB'
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

drive_val = 0.0
turn_val = 0.0

print("Rover ready.")

try:
    while True:
        try:
            with open(DEVICE, 'rb') as js:
                while True:
                    data = js.read(EVENT_SIZE)
                    _, value, ev_type, number = struct.unpack(EVENT_FORMAT, data)

                    if ev_type == 2:
                        if number == 1:
                            drive_val = -normalize(value)
                        elif number == 0:
                            turn_val = normalize(value)

                        left  = max(-1.0, min(1.0, drive_val - turn_val))
                        right = max(-1.0, min(1.0, drive_val + turn_val))

                        set_motors(left, right)

        except OSError:
            print("Controller disconnected, retrying...")
            set_motors(0, 0)
            time.sleep(2)

except KeyboardInterrupt:
    print("Stopping.")
    set_motors(0, 0)
    GPIO.cleanup()
