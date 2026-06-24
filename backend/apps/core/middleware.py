from typing import Callable


class AllowPrivateNetworkMiddleware:
    """Add Access-Control-Allow-Private-Network header when requested by browsers.

    Modern browsers add the `Access-Control-Request-Private-Network: true` header
    to preflight requests when the target is in a more-private address space
    (eg. loopback). To allow the browser to complete the preflight, the server
    must echo back `Access-Control-Allow-Private-Network: true`.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Django 3.2+ exposes request.headers, fallback to META for older niceties
        req_hdr = getattr(request, "headers", None)
        has_pna = False
        if req_hdr is not None:
            has_pna = req_hdr.get("Access-Control-Request-Private-Network") == "true"
        else:
            has_pna = request.META.get("HTTP_ACCESS_CONTROL_REQUEST_PRIVATE_NETWORK") == "true"

        if has_pna:
            # Signal to the browser that private network access is allowed for this origin
            response["Access-Control-Allow-Private-Network"] = "true"

        return response
