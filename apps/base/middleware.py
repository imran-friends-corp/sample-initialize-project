# django
from django.core.cache import cache
from django.http.response import HttpResponse, JsonResponse, HttpResponseBase
from django.urls import resolve
from django.contrib.auth.middleware import AuthenticationMiddleware
import threading

# rest framework
from rest_framework.response import Response

# backend
from django.conf import settings

# third-party
import json
import logging

# live urls
# from apps.user.urls import live_urls as user_live_urls
# live_urls = user_live_urls
live_urls = []

logger = logging.getLogger(__name__)

# Create a thread-local storage to store the current request object.
request_local = threading.local()


class CacheQueryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define a list of API paths or patterns to exclude from caching
        # excluded_paths = self.collect_live_urls()
        excluded_paths = live_urls

        resolver_match = resolve(request.path_info)
        kwargs = resolver_match.kwargs

        if 'pk' in kwargs:
            excluded_paths = [url.replace('<str:pk>', str(kwargs['pk'])) for url in excluded_paths]

        # Check if the request method is a GET request and if the path is not in the exclusion list
        cache_query = request.method == 'GET' and request.path not in excluded_paths

        # print(excluded_paths)

        # print(request.path)

        # Check if the request method is a GET request and if the path is not in the exclusion list
        if cache_query:
            # Generate a cache key based on the request path and query parameters
            cache_key = f'api_cache:{request.path}:{request.GET.urlencode()}'

            # Try to fetch the data from the cache
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                if isinstance(cached_data, HttpResponseBase):
                    # If data is an HttpResponse, return it as-is
                    return cached_data
                elif isinstance(cached_data, JsonResponse):
                    # If data is a JsonResponse, convert it to HttpResponse
                    return HttpResponse(
                        content=cached_data.content,
                        content_type='application/json',
                        status=cached_data.status_code,
                    )
                elif isinstance(cached_data, Response):
                    # If data is a DRF Response, convert it to HttpResponse
                    # return HttpResponse(
                    #     content=cached_data.rendered_content,
                    #     content_type='application/json',
                    #     status=cached_data.status_code,
                    # )
                    return self.deserialize_response(cached_data)

        # If data is not found in the cache or the request is not a GET request,
        # continue with the normal view processing
        response = self.get_response(request)

        # If it's a successful GET request and not in the exclusion list, cache the response data
        if cache_query and 200 <= response.status_code < 300:
            if not response.streaming:
                cache.set(cache_key, self.serialize_response(response), settings.CACHE_MIDDLEWARE_SECONDS)  # Set cache

        return response

    def serialize_response(self, response):
        data = {
            'content': response.content.decode('utf-8'),
            'status_code': response.status_code,
            'headers': dict(response.items()),
            'response_type': str(type(response)),
        }
        return json.dumps(data)

    def deserialize_response(self, data):
        data = json.loads(data)
        content = data['content']
        status_code = data['status_code']
        headers = data['headers']
        response_type = data['response_type']

        if response_type == "<class 'django.http.response.HttpResponse'>":
            response = HttpResponse(content=content, status=status_code)
        elif response_type == "<class 'django.http.response.JsonResponse'>":
            response = JsonResponse(data={}, status=status_code)
            response.content = content.encode('utf-8')
        elif response_type == "<class 'rest_framework.response.Response'>":
            response = Response(data={}, status=status_code)
            response._content = content.encode('utf-8')

        for header, value in headers.items():
            response[header] = value

        return response


class RequestTrackerMiddleware(AuthenticationMiddleware):

    def __init__(self, get_response):
        """
        Initialize the middleware.

        Args:
            get_response (callable): The next middleware or view function in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the incoming request and store the request object in thread-local storage.

        Args:
            request (HttpRequest): The incoming request.

        Returns:
            HttpResponse: The response generated by the next middleware or view function.
        """
        # Store the current request in thread-local storage for access in the same thread.
        request_local.current_request = request

        # Continue processing the request and response in the middleware chain.
        response = self.get_response(request)

        return response
