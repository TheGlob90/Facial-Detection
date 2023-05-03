import pwmio
import board
import time

# Code to run speaker that is attached to Pi
# Speaker is connected to GPIO 12
def speaker(event): 
    pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=880)
    count = 0
    while not (event.is_set()):
        time.sleep(0.1)
        pwm.frequency = 500
        time.sleep(0.1)
        pwm.frequency = 880
