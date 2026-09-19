from slowapi import Limiter
from slowapi.util import get_remote_address


def rate_limit_key(request):
    ip_address = get_remote_address(request)
    widget_id = request.path_params.get("widget_id")

    return f"{ip_address}:{widget_id}"


limiter = Limiter(key_func=rate_limit_key)