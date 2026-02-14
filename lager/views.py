from django.shortcuts import render, redirect, get_object_or_404
from .models import Sirovina
from .forms import SirovinaForm
from django.contrib.auth.decorators import login_required

@login_required
def stanje_robe(request):
    sirovine = Sirovina.objects.all()

    if request.method == 'POST':
        form = SirovinaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stanje_robe')
    else:
        form = SirovinaForm()

    return render(request, 'lager/stanje_robe.html', {
        'form': form,
        'sirovine': sirovine,
    })

@login_required
def edit_sirovina(request, pk):
    sirovina = get_object_or_404(Sirovina, pk=pk)

    if request.method == 'POST':
        form = SirovinaForm(request.POST, instance=sirovina)
        if form.is_valid():
            form.save()
            return redirect('stanje_robe')
    else:
        form = SirovinaForm(instance=sirovina)

    return render(request, 'lager/edit_sirovina.html', {
        'form': form,
        'sirovina': sirovina,
    })

def lager_list(request):
    sirovine = Sirovina.objects.all().order_by('naziv')
    low = sirovine.filter(kolicina__lte=models.F('min_kolicina'))
    return render(request, 'lager/lager_list.html', {'sirovine': sirovine, 'low': low})