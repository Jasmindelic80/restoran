from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch

from .forms import StavkaForm
from .models import Stavka
from lager.models import Recept


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch

from .forms import StavkaForm
from .models import Stavka
from lager.models import Recept


def meni_list(request):
    stavke = (
        Stavka.objects
        .all()
        .order_by('naziv')
        .prefetch_related(
            Prefetch('recept_set', queryset=Recept.objects.select_related('sirovina'))
        )
    )

    for stavka in stavke:
        recepti = stavka.recept_set.all()

        if not recepti.exists():
            stavka.is_available = True      # ili False ako želiš da bez recepta nije dostupno
            stavka.max_portions = None
            continue

        porcije_po_sirovini = []
        for r in recepti:
            if r.kolicina is None or r.kolicina <= 0:
                continue
            porcije_po_sirovini.append(int(float(r.sirovina.kolicina) // float(r.kolicina)))

        max_porcija = min(porcije_po_sirovini) if porcije_po_sirovini else 0
        stavka.max_portions = max_porcija
        stavka.is_available = max_porcija > 0

    kategorije = dict(Stavka.KATEGORIJE)

    return render(request, 'meni/meni_list.html', {
        'stavke': stavke,
        'kategorije': kategorije,
    })

def stavka_update(request, pk):
    stavka = get_object_or_404(Stavka, pk=pk)
    if request.method == 'POST':
        form = StavkaForm(request.POST, instance=stavka)
        if form.is_valid():
            form.save()
            return redirect('stavka_detail', pk=stavka.pk)
    else:
        form = StavkaForm(instance=stavka)
    return render(request, 'meni/stavka_update.html', {'form': form})


def stavka_create(request):
    if request.method == 'POST':
        form = StavkaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('meni_list')
    else:
        form = StavkaForm()
    return render(request, 'meni/stavka_create.html', {'form': form})


def stavka_detail(request, pk):
    stavka = get_object_or_404(Stavka, pk=pk)
    return render(request, 'meni/stavka_detail.html', {'stavka': stavka})


def stavka_delete(request, pk):
    stavka = get_object_or_404(Stavka, pk=pk)
    if request.method == 'POST':
        stavka.delete()
        return redirect('meni_list')
    return render(request, 'meni/stavka_delete.html', {'stavka': stavka})
