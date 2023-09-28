# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import SignUpForm


# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')  # Redirect to login page after successful sign-up
#     else:
#         form = SignUpForm()
#
#     return render(request, 'registration/signup.html', {'form': form})


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def logout_view(request):
    logout(request)
    return redirect("/")
