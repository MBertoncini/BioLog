# In un nuovo file middleware.py
class JustLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.has_header('X-Just-Logged-In'):
            response.delete_cookie('X-Just-Logged-In')
            response['Set-Cookie'] = 'just_logged_in=true; Path=/; Max-Age=60'
        return response

