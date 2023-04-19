import pwmio
import board
import time

pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=880)
while True:
    time.sleep(0.1)
    pwm.frequency = 500
    time.sleep(0.1)
    pwm.frequency = 880
