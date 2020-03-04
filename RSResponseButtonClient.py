
import RPi.GPIO as GPIO
import time
import requests
import json
import subprocess

POST_TEAMS = os.environ.get('POST_TEAMS') == '1'
TEAMS_INCOMING_WEBHOOK_URL = os.environ.get('TEAMS_INCOMING_WEBHOOK_URL')
if TEAMS_INCOMING_WEBHOOK_URL is None:
    print('Teams incoming webhook URL not provided')
    POST_TEAMS = False

TITLE_OF_POST = os.environ.get('TITLE_OF_POST', 'ResponseButton')

GPIO_BUTTON_GOING = int(os.environ.get('GPIO_BUTTON_GOING', 22))
GPIO_BUTTON_WAIT = int(os.environ.get('GPIO_BUTTON_WAIT', 27))

def play(file):
    p = subprocess.Popen([ 'mpg123', file ])
    p.communicate()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_BUTTON_GOING, GPIO.IN)
    GPIO.setup(GPIO_BUTTON_WAIT, GPIO.IN)

    ts = 0
    wait = .5
    try:
        prev_pin_going = False
        prev_pin_wait = False
        while True:
            pin_going = GPIO.input(GPIO_BUTTON_GOING) == GPIO.HIGH
            pin_wait = GPIO.input(GPIO_BUTTON_WAIT) == GPIO.HIGH

            now = time.time()
            if ts + wait < now:
                post = None
                bell = None
                if pin_going and not prev_pin_going:
                    post = '[%s] いま行きます' % TITLE_OF_POST
                    bell = 'sound/going.mp3'
                    ts = now
                if pin_wait and not prev_pin_wait:
                    post = '[%s] お待ちください' % TITLE_OF_POST
                    bell = 'sound/wait.mp3'
                    ts = now

                if post is not None and POST_TEAMS:
                    data = {
                        'text': post,
                    }
                    headers = {
                        'Content-Type': 'application/json',
                    }
                    requests.post(TEAMS_INCOMING_WEBHOOK_URL, data=json.dumps(data))

                if bell is not None:
                    play(bell)

            prev_pin_going = pin_going
            prev_pin_wait = pin_wait
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
