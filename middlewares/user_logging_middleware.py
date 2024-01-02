from django.utils.deprecation import MiddlewareMixin
import logging


class UserLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user_info = "Anonymous"
        if request.user.is_authenticated:
            request.user_info = f"User {request.user.username}"

    def process_response(self, request, response):
        logger = logging.getLogger("django")
        logger.info(f"{request.user_info} made a request to {request.path}")
        return response
