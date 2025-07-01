
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    return render(request, 'korisnici/dashboard.html')

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # ili na profil ili dashboard
        else:
            error = "Neispravno korisničko ime ili lozinka."
    return render(request, 'korisnici/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profil_view(request):
    return render(request, 'korisnici/profil.html')


from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            error = "Lozinke se ne poklapaju."
        elif User.objects.filter(username=username).exists():
            error = "Korisničko ime je već zauzeto."
        elif User.objects.filter(email=email).exists():
            error = "Email je već registrovan."
        else:
            user = User.objects.create_user(username=username,first_name=first_name,
                last_name=last_name, email=email, password=password1)
            user.save()
            return redirect('login')

    return render(request, 'korisnici/register.html', {'error': error})

