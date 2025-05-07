import time
import logging

logger = logging.getLogger('request')

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        logger.info(f"[REQUEST] {request.method} {request.get_full_path()} - IP: {self.get_client_ip(request)}")

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(f"[RESPONSE] {request.method} {request.get_full_path()} - Duration: {duration:.2f}s - Status: {response.status_code}")

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip