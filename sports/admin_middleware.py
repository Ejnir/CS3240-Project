from django.http import HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import redirect

# Django admins should only be able to view /admin; they should not be able to view or access the app itself
class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_staff and not request.path.startswith(reverse('admin:index')):
            return HttpResponseForbidden("Admin users are not permitted to view this page.")
        
        return self.get_response(request)