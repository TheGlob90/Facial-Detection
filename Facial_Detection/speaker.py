import pwmio
import board

def speaker(): 
    pwm = pwmio.PWMOut(board.D12, duty_cycle=2 ** 15, frequency=880)
    count = 0
    while count < 100:
        time.sleep(0.1)
        pwm.frequency = 500
        time.sleep(0.1)
        pwm.frequency = 880
