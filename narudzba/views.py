from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from lager.models import Recept
from .models import Narudzba, StavkaNarudzbe
from .forms import NarudzbaForm
from meni.models import Stavka
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Narudzba

from rest_framework.decorators import api_view
from rest_framework import status

@api_view(['GET'])
def narudzba_detail_api(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    serializer = NarudzbaSerializer(narudzba)
    return Response(serializer.data)

@api_view(['POST'])
def narudzba_create_api(request):
    serializer = NarudzbaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def narudzbe_api(request):
    narudzbe = Narudzba.objects.all()
    serializer = NarudzbaSerializer(narudzbe, many=True)
    return Response(serializer.data)


@login_required
def izdaj_racun(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    stavke = narudzba.stavke.all()
    ukupno = sum(st.kolicina * st.stavka.cijena for st in stavke)

    template_path = 'narudzba/racun_pdf.html'
    context = {
        'narudzba': narudzba,
        'stavke': stavke,
        'ukupno': ukupno
    }

    # Render HTML u string
    template = get_template(template_path)
    html = template.render(context)

    # Kreiraj PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="racun_{narudzba.id}.pdf"'
    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('Greška pri kreiranju PDF-a')
    return response


def sank_required(view_func):
    return user_passes_test(lambda u: hasattr(u, 'profil') and u.profil.uloga == 'sank')(view_func)


@login_required
def izvjestaj(request):
    today = now().date()
    start_month = today.replace(day=1)

    dnevne = Narudzba.objects.filter(datum__date=today)
    mjesecne = Narudzba.objects.filter(datum__date__gte=start_month)

    def ukupno(narudzbe):
        return sum([
            sum(st.kolicina * st.stavka.cijena for st in n.stavke.all())
            for n in narudzbe
        ])

    return render(request, 'izvjestaji.html', {
        'dnevno': ukupno(dnevne),
        'mjesečno': ukupno(mjesecne),
        'broj_dnevno': dnevne.count(),
        'broj_mjesečno': mjesecne.count(),
    })

# --- ✅ Lista svih narudžbi
@login_required
def narudzba_list(request):
    narudzbe = Narudzba.objects.all().order_by('-datum')
    return render(request, 'narudzba/narudzba_list.html', {'narudzbe': narudzbe})

# --- ✅ Detalji narudžbe
@login_required
def narudzba_detail(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    stavke = narudzba.stavke.all()
    ukupno = sum(stavka.kolicina * stavka.stavka.cijena for stavka in stavke)

    return render(request, 'narudzba/narudzba_detail.html', {
        'narudzba': narudzba,
        'stavke': stavke,
        'ukupno': ukupno
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from .forms import NarudzbaForm
from .models import StavkaNarudzbe, Narudzba
from meni.models import Stavka
from lager.models import Recept
from collections import defaultdict

@login_required
def narudzba_create(request):
    sve_stavke = Stavka.objects.all().order_by('kategorija', 'naziv')
    stavke_po_kategoriji = defaultdict(list)
    for s in sve_stavke:
        stavke_po_kategoriji[s.kategorija].append(s)


    if request.method == 'POST':
        form = NarudzbaForm(request.POST)
        if form.is_valid():
            stavke_za_narudzbu = []
            greske = []


            potrosnja_sirovina = defaultdict(int)

            for stavka in sve_stavke:
                kolicina = request.POST.get(f'kolicina_{stavka.id}')
                if kolicina:
                    try:
                        kolicina = int(kolicina)
                    except ValueError:
                        continue
                    if kolicina <= 0:
                        continue

                    stavke_za_narudzbu.append((stavka, kolicina))

                    recepti = Recept.objects.filter(stavka=stavka)
                    for recept in recepti:
                        ukupno_potrebno = kolicina * recept.kolicina
                        potrosnja_sirovina[recept.sirovina] += ukupno_potrebno
                        if recept.sirovina.kolicina < potrosnja_sirovina[recept.sirovina]:
                            greske.append(
                                f"Nema dovoljno '{recept.sirovina.naziv}' za {stavka.naziv} "
                                f"(potrebno: {potrosnja_sirovina[recept.sirovina]}, dostupno: {recept.sirovina.kolicina})"
                            )


            if greske:
                return render(request, 'narudzba/narudzba_create.html', {
                    'form': form,
                    'stavke': sve_stavke,
                    'greske': greske
                })


            narudzba = form.save(commit=False)
            narudzba.konobar = request.user
            narudzba.status = 'na_sanku'
            narudzba.save()


            for stavka, kolicina in stavke_za_narudzbu:
                StavkaNarudzbe.objects.create(
                    narudzba=narudzba,
                    stavka=stavka,
                    kolicina=kolicina
                )


            for sirovina, ukupno_potroseno in potrosnja_sirovina.items():
                sirovina.kolicina -= ukupno_potroseno
                sirovina.save()

            return redirect('narudzba_detail', pk=narudzba.pk)

    else:
        form = NarudzbaForm()

    return render(request, 'narudzba/narudzba_create.html', {
        'form': form,
        'stavke': sve_stavke
    })



@login_required
def narudzba_update(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    if request.method == 'POST':
        form = NarudzbaForm(request.POST, instance=narudzba)
        if form.is_valid():
            form.save()
            return redirect('narudzba_detail', pk=narudzba.pk)
    else:
        form = NarudzbaForm(instance=narudzba)

    return render(request, 'narudzba/narudzba_update.html', {
        'form': form,
        'narudzba': narudzba
    })


@login_required
def narudzba_delete(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    if request.method == 'POST':
        narudzba.delete()
        return redirect('narudzba_list')

    return render(request, 'narudzba/narudzba_delete.html', {
        'narudzba': narudzba
    })

# --- ✅ Pogled za šankera
@sank_required
@login_required
def sank_view(request):
    narudzbe = Narudzba.objects.filter(status='u_pripremi').order_by('datum')

    if request.method == 'POST':
        narudzba_id = request.POST.get('narudzba_id')
        narudzba = Narudzba.objects.get(pk=narudzba_id)
        narudzba.status = 'spremna'
        narudzba.save()
        return redirect('sank')

    return render(request, 'korisnici/sank.html', {'narudzbe': narudzbe})
