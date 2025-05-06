import os
import sys
import django

# Trỏ tới thư mục gốc dự án (nơi có file manage.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Chỉ định settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DemoDjango.settings')
django.setup()

import redis
import logging
from user.views import generate_otp, activate_account, welcome_email

logger = logging.getLogger('signup')
r = redis.Redis(host='127.0.0.1', port=6379, db=2)
pubsub = r.pubsub()
pubsub.subscribe('register', 'resend_otp', 'verify_otp_success')

def start_verification_listener():
    for message in pubsub.listen():
        if message['type'] == 'message':
            chanel = message['channel'].decode()
            user_id = int(message['data'].decode())
            logger.info(f"[EVENT] Received message from channel: {chanel}, user_id={user_id}")

            if chanel == 'register':
                logger.info(f"[EVENT] New register initiated for user_id={user_id}")
                generate_otp.delay(user_id)
            elif chanel == 'resend_otp':
                logger.info(f"[EVENT] Resend OTP triggered for user_id={user_id}")
                generate_otp.delay(user_id)
            elif chanel == 'verify_otp_success':
                logger.info(f"[EVENT] OTP verified for user_id={user_id}")
                activate_account.delay(user_id)
                welcome_email.delay(user_id)
            else:
                logger.error(f"[ERROR] Unknown channel: {chanel}")

print('start run woker')
start_verification_listener()
print('stop run woker')