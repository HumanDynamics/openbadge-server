

import logging

class ExceptionLoggingMiddleware(object):

    def process_exception(self, request, exception):
        logging.exception('Exception handling request for ' + request.path)


class XForwardedForMiddleware():
    def process_request(self, request):
        if request.META.has_key("HTTP_X_FORWARDED_FOR"):
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]


