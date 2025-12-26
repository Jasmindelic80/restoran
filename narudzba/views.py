from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import io
from collections import defaultdict
from rest_framework.viewsets import ModelViewSet


# --- DRF ---
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status

# --- modeli i serializeri ---
from .models import Narudzba, StavkaNarudzbe
from meni.models import Stavka
from .serializers import NarudzbaSerializer, StavkaNarudzbeSerializer, StavkaSerializer
from .forms import NarudzbaForm
from lager.models import Recept

# =========================================
# ✅ DRF ViewSet API
# =========================================

class NarudzbaViewSet(ModelViewSet):
    queryset = Narudzba.objects.all()
    serializer_class = NarudzbaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        sto = self.request.query_params.get("sto")
        status = self.request.query_params.get("status")

        if sto:
            qs = qs.filter(sto_broj=sto)

        if status:
            qs = qs.filter(status=status)

        return qs


class StavkaNarudzbeViewSet(viewsets.ModelViewSet):
    queryset = StavkaNarudzbe.objects.all()
    serializer_class = StavkaNarudzbeSerializer
    permission_classes = [permissions.IsAuthenticated]


class StavkaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stavka.objects.all()
    serializer_class = StavkaSerializer
    permission_classes = [permissions.IsAuthenticated]

# =========================================
# ✅ Standard Django Views
# =========================================

@login_required
def narudzba_list(request):
    narudzbe = Narudzba.objects.all().order_by('-datum')
    return render(request, 'narudzba/narudzba_list.html', {'narudzbe': narudzbe})


@login_required
def narudzba_detail(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    stavke = narudzba.stavke.all()
    ukupno = sum(st.kolicina * st.stavka.cijena for st in stavke)
    return render(request, 'narudzba/narudzba_detail.html', {
        'narudzba': narudzba,
        'stavke': stavke,
        'ukupno': ukupno
    })


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

                    # provjera sirovina
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

            # update lagera
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
    return render(request, 'narudzba/narudzba_delete.html', {'narudzba': narudzba})


from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa

from .models import Narudzba
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(["GET"])
@permission_classes([IsAuthenticated])
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

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="racun_{pk}.pdf"'

    pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")),
        dest=response,
        encoding='UTF-8'
    )

    return response

def sank_required(view_func):
    return user_passes_test(lambda u: hasattr(u, 'profil') and u.profil.uloga == 'sank')(view_func)


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



from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from .models import Narudzba

def izdaj_racun(request, pk):
    try:
        narudzba = Narudzba.objects.get(pk=pk)
    except Narudzba.DoesNotExist:
        return HttpResponse("Narudžba ne postoji", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="racun_{pk}.pdf"'

    c = canvas.Canvas(response, pagesize=A5)
    width, height = A5

    # Registriraj Unicode font
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    c.setFont("DejaVu", 12)

    # Zaglavlje
    c.setFont("DejaVu", 14)
    c.drawCentredString(width/2, height-50, "RESTAURANT POS RAČUN")
    c.setFont("DejaVu", 10)
    c.drawString(40, height-70, f"Broj stola: {narudzba.sto_broj}")
    c.drawString(40, height-85, f"Narudžba ID: {narudzba.id}")
    c.drawString(40, height-100, f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

    # Stavke
    y = height-130
    c.setFont("DejaVu", 10)
    c.drawString(40, y, "Naziv")
    c.drawString(150, y, "Količina")
    c.drawString(220, y, "Cijena")
    y -= 15
    c.line(40, y, width-40, y)
    y -= 10

    total = 0
    for stavka in narudzba.stavke.all():
        naziv = stavka.stavka.naziv
        kolicina = stavka.kolicina
        cijena = stavka.stavka.cijena * kolicina
        total += cijena

        c.drawString(40, y, naziv)
        c.drawString(150, y, str(kolicina))
        c.drawString(220, y, f"{cijena:.2f}€")
        y -= 15
        if y < 50:
            c.showPage()
            c.setFont("DejaVu", 10)
            y = height - 50

    # Ukupno
    y -= 10
    c.line(40, y, width-40, y)
    y -= 20
    c.setFont("DejaVu", 12)
    c.drawString(40, y, f"UKUPNO: {total:.2f}€")

    c.showPage()
    c.save()
    return response


    for stavka in narudzba.stavke.all():
        line_total = stavka.kolicina * stavka.stavka.cijena
        total += line_total
        c.drawString(40, y, stavka.stavka.naziv)
        c.drawString(150, y, str(stavka.kolicina))
        c.drawString(220, y, f"{line_total:.2f}€")
        y -= 15

    # Separator
    c.line(40, y, width-40, y)
    y -= 20

    # Ukupno
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"UKUPNO: {total:.2f}€")

    c.showPage()
    c.save()
    return response
