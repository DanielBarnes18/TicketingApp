from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User

class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return response

@login_required
def profile_view(request):
    """Display the user's profile."""
    return render(request, 'users/profile.html')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

def logout_view(request):
    """Logout a user and redirect to login page."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login') 