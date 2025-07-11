from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profil
from narudzba.models import Narudzba
from django.utils.timezone import now
from lager.models import Sirovina


def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Neispravno korisničko ime ili lozinka."
    return render(request, 'korisnici/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profil_view(request):
    return render(request, 'korisnici/profil.html')


def register_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        uloga = request.POST.get('uloga')

        if password1 != password2:
            error = "Lozinke se ne poklapaju."
        elif User.objects.filter(username=username).exists():
            error = "Korisničko ime je već zauzeto."
        elif User.objects.filter(email=email).exists():
            error = "Email je već registrovan."
        elif uloga not in ['sef', 'konobar', 'sank']:
            error = "Neispravna uloga."
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1
            )
            Profil.objects.create(user=user, uloga=uloga)
            return redirect('login')

    return render(request, 'korisnici/register.html', {'error': error})


@login_required
def dashboard_view(request):
    profil = getattr(request.user, 'profil', None)
    if not profil:
        return redirect('login')

    if profil.uloga == 'sef':
        return render(request, 'korisnici/dashboard.html')

    elif profil.uloga == 'konobar':
        narudzbe = Narudzba.objects.filter(konobar=request.user)
        return render(request, 'korisnici/dashboard.html', {'narudzbe': narudzbe})

    elif profil.uloga == 'sank':
        narudzbe = Narudzba.objects.all().order_by('-datum')
        return render(request, 'korisnici/dashboard_sank.html', {'narudzbe': narudzbe})

    else:
        return render(request, 'korisnici/dashboard.html')


@login_required
def potvrdi_narudzbu(request, narudzba_id):
    narudzba = get_object_or_404(Narudzba, id=narudzba_id)

    if request.method == 'POST' and hasattr(request.user, 'profil') and request.user.profil.uloga == 'sank':
        narudzba.status = 'zavrsena'
        narudzba.save()

    return redirect('dashboard')


@login_required
def stanje_robe(request):
    sirovine = Sirovina.objects.all()
    return render(request, 'lager/stanje_robe.html', {'sirovine': sirovine})


@login_required
def izvjestaj(request):
    today = now().date()
    start_month = today.replace(day=1)

    dnevne_narudzbe = Narudzba.objects.filter(datum__date=today)
    mjesecne_narudzbe = Narudzba.objects.filter(datum__date__gte=start_month)

    def ukupno(narudzbe):
        return sum([
            sum(st.kolicina * st.stavka.cijena for st in n.stavke.all())
            for n in narudzbe
        ])

    return render(request, 'korisnici/izvjestaj.html', {
        'dnevno': ukupno(dnevne_narudzbe),
        'mjesecno': ukupno(mjesecne_narudzbe),
        'broj_dnevno': dnevne_narudzbe.count(),
        'broj_mjesecno': mjesecne_narudzbe.count(),
    })

@login_required
def izvjestaj_stanje_roba(request):
    sirovine = Sirovina.objects.all()
    return render(request, 'korisnici/izvjestaj_stanje_roba.html', {
        'sirovine': sirovine
    })