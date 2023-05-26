from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from .sendmail import sendmail
from .models import Otp, Appointment
import random
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime, timezone
from django.views.generic import CreateView

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def authenticate_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("index"))
    if request.method == "POST":

        if request.POST.get("action") == "login":

            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "message": "Invalid username or password"})
        elif request.POST.get("action") == "sign_up":

            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                return JsonResponse({"success": False, "message": "Password and Confirm Password do not match"})
            if User.objects.filter(username=username).exists():
                return JsonResponse({"success": False, "message": "Username already exists"})
            if User.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "message": "Email already exists"})

            try:
                Otp.objects.get(username=username, mail=email).delete()
            except:
                pass
            otp = Otp.objects.create(mail=email, username=username, otp=random.randint(100000, 999999))
            otp.save()

            sendmail(email, "BloodBridge OTP", f"Hello {username},\n\nYour OTP is {otp.otp}\n\nIf You did not request this code, please ignore this email.\n\nRegards,\nBloodBridge Team")

            return JsonResponse({"success": True})

        elif request.POST.get("action") == "verify_otp":

            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

            otp = request.POST.get("otp").strip()
            try:
                update_otp = Otp.objects.get(username=username, mail=email)
                update_otp.tries += 1
                update_otp.save()
            except:
                return JsonResponse({"success": False, "message": "Invalid OTP"})

            confirm = Otp.objects.get(username=username, mail=email).otp
            if otp != confirm:
                return JsonResponse({"success": False, "message": "Invalid OTP"})
            if Otp.objects.get(username=username, mail=email).tries >= 5:
                Otp.objects.get(username=username, mail=email).delete()
                return JsonResponse({"success": False, "message": "Too many tries. Please try again later."})
            
            created = Otp.objects.get(username=username, mail=email).created_at
            now = datetime.now(timezone.utc)
            diff = now - created

            if diff.total_seconds() > 43200:
                return JsonResponse({"success": False, "message": "OTP Expired. Please try again."})

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            user = User.objects.get(username=request.POST.get("username"))
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            Otp.objects.get(username=username, mail=email).delete()

            login(request, user)

            return JsonResponse({"success": True})

    return render(request, "0-authenticate.html")

def logout_view(request):
    logout(request)
    return redirect(reverse("authenticate"))

class Appointment_form(LoginRequiredMixin, CreateView):
    model = Appointment
    template_name = 'appointment_form.html'
    fields = ['reason', 'contact']
