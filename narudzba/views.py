from collections import defaultdict
import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from django.http import HttpResponse

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from .models import Narudzba, StavkaNarudzbe
from .forms import NarudzbaForm
from .serializers import NarudzbaSerializer, StavkaNarudzbeSerializer, StavkaSerializer
from meni.models import Stavka
from lager.models import Recept, Sirovina


# =========================================================
# DRF API VIEWSETOVI
# =========================================================

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


class StavkaNarudzbeViewSet(ModelViewSet):
    queryset = StavkaNarudzbe.objects.all()
    serializer_class = StavkaNarudzbeSerializer
    permission_classes = [permissions.IsAuthenticated]


class StavkaViewSet(ReadOnlyModelViewSet):
    queryset = Stavka.objects.all()
    serializer_class = StavkaSerializer
    permission_classes = [permissions.IsAuthenticated]


# =========================================================
# STANDARD DJANGO VIEW-OVI
# =========================================================

@login_required
def narudzba_list(request):
    narudzbe = Narudzba.objects.all().order_by('-id')
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

    if request.method == 'POST':
        form = NarudzbaForm(request.POST)

        if form.is_valid():
            stavke_za_narudzbu = []
            greske = []
            potrosnja_sirovina = defaultdict(float)

            # 1) provjera lagera (akumulirano)
            for stavka in sve_stavke:
                kolicina = request.POST.get(f'kolicina_{stavka.id}')
                if not kolicina:
                    continue

                try:
                    kolicina = int(kolicina)
                except ValueError:
                    continue

                if kolicina <= 0:
                    continue

                stavke_za_narudzbu.append((stavka, kolicina))

                recepti = Recept.objects.filter(stavka=stavka).select_related("sirovina")
                for recept in recepti:
                    if recept.kolicina is None or recept.kolicina <= 0:
                        continue

                    ukupno_potrebno = float(kolicina) * float(recept.kolicina)
                    sid = recept.sirovina_id
                    potrosnja_sirovina[sid] += ukupno_potrebno

                    dostupno = float(recept.sirovina.kolicina)
                    potrebno = potrosnja_sirovina[sid]

                    if dostupno < potrebno:
                        greske.append(
                            f"Nema dovoljno '{recept.sirovina.naziv}' za {stavka.naziv} "
                            f"(potrebno: {potrebno}, dostupno: {dostupno})"
                        )

            if greske:
                return render(request, 'narudzba/narudzba_create.html', {
                    'form': form,
                    'stavke': sve_stavke,
                    'greske': greske
                })

            # 2) kreiranje narudžbe
            narudzba = form.save(commit=False)
            narudzba.konobar = request.user
            narudzba.status = 'u_pripremi'  # mora biti u STATUS_CHOICES
            narudzba.save()

            for stavka, kolicina in stavke_za_narudzbu:
                StavkaNarudzbe.objects.create(
                    narudzba=narudzba,
                    stavka=stavka,
                    kolicina=kolicina
                )

            # 3) skidanje lagera
            for sid, ukupno_potroseno in potrosnja_sirovina.items():
                s = Sirovina.objects.get(id=sid)
                s.kolicina -= ukupno_potroseno
                s.save()

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


# =========================================================
# SANK VIEW
# =========================================================

def sank_required(view_func):
    return user_passes_test(
        lambda u: hasattr(u, 'profil') and u.profil.uloga == 'sank'
    )(view_func)


@sank_required
@login_required
def sank_view(request):
    narudzbe = Narudzba.objects.filter(status__in=['u_pripremi']).order_by('datum')

    if request.method == 'POST':
        narudzba_id = request.POST.get('narudzba_id')
        narudzba = get_object_or_404(Narudzba, pk=narudzba_id)
        narudzba.status = 'spremna'  # mora biti u STATUS_CHOICES
        narudzba.save()
        return redirect('sank')

    return render(request, 'narudzba/sank.html', {'narudzbe': narudzbe})


# =========================================================
# IZVJEŠTAJ + GRAF
# =========================================================

@login_required
def izvjestaj(request):
    today = now().date()
    start_month = today.replace(day=1)

    dnevne = Narudzba.objects.filter(datum__date=today)
    mjesecne = Narudzba.objects.filter(datum__date__gte=start_month)

    def ukupno(qs):
        return sum(
            sum(st.kolicina * st.stavka.cijena for st in n.stavke.all())
            for n in qs
        )

    return render(request, 'izvjestaji.html', {
        'dnevno': ukupno(dnevne),
        'mjesečno': ukupno(mjesecne),
        'broj_dnevno': dnevne.count(),
        'broj_mjesečno': mjesecne.count(),
    })


@login_required
def promet_graf(request):
    data = {}

    for n in Narudzba.objects.all().order_by('datum'):
        d = n.datum.date()
        total = sum(st.kolicina * st.stavka.cijena for st in n.stavke.all())
        data[d] = data.get(d, 0.0) + float(total)

    dates = sorted(data.keys())
    totals = [data[d] for d in dates]

    if not dates:
        dates = [now().date()]
        totals = [0.0]

    fig = plt.figure()
    plt.plot(dates, totals)
    plt.title("Dnevni promet")
    plt.xlabel("Datum")
    plt.ylabel("KM")
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    fig.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type="image/png")


# =========================================================
# PDF RAČUN (ReportLab)
# =========================================================

@login_required
def izdaj_racun(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="racun_{pk}.pdf"'

    c = canvas.Canvas(response, pagesize=A5)
    width, height = A5

    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    c.setFont("DejaVu", 12)

    c.drawCentredString(width / 2, height - 50, "RESTAURANT POS RAČUN")
    c.setFont("DejaVu", 10)
    c.drawString(40, height - 70, f"Sto: {narudzba.sto_broj}")
    c.drawString(40, height - 85, f"Narudžba ID: {narudzba.id}")
    c.drawString(40, height - 100, f"Datum: {datetime.now():%d.%m.%Y %H:%M}")

    y = height - 130
    total = 0.0

    for stavka in narudzba.stavke.all():
        line_total = float(stavka.kolicina) * float(stavka.stavka.cijena)
        total += line_total

        c.drawString(40, y, stavka.stavka.naziv)
        c.drawString(150, y, str(stavka.kolicina))
        c.drawString(220, y, f"{line_total:.2f} KM")
        y -= 15

    y -= 10
    c.line(40, y, width - 40, y)
    y -= 20

    c.setFont("DejaVu", 12)
    c.drawString(40, y, f"UKUPNO: {total:.2f} KM")

    c.showPage()
    c.save()
    return response
