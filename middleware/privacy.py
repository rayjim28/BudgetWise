"""Cross-cutting response headers for a personal-finance application.

Django's own SecurityMiddleware, CSRF middleware, and authentication middleware
remain configured in budgetmanager/settings.py.
"""


class PrivacyHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        return response
