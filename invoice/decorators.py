from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect

def roles_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('home')  # Or a custom 'unauthorized' page
        return _wrapped_view
    return decorator

admin_required = roles_required(['admin'])
accountant_required = roles_required(['accountant'])
project_manager_required = roles_required(['project_manager'])
