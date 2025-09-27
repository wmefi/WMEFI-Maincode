from django.shortcuts import redirect

class PortalRedirectMiddleware:
    """Redirect any '/gc/' prefixed URLs to '/cp/' equivalents.

    This normalizes portal prefixes so that all navigation uses '/cp/'.
    It also handles the bare '/gc' and '/gc/' roots.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or '/'
        # Normalize bare gc root
        if path == '/gc' or path == '/gc/':
            return redirect('/cp/')
        # Redirect any /gc/<rest> -> /cp/<rest>
        if path.startswith('/gc/'):
            return redirect('/cp/' + path[len('/gc/'):])
        # Also normalize 'next' parameter if present
        next_url = request.GET.get('next')
        if next_url and next_url.startswith('/gc/'):
            # Build a new GET dict replacing next
            mutable = request.GET.copy()
            mutable['next'] = '/cp/' + next_url[len('/gc/'):]
            request.GET = mutable
        return self.get_response(request)
