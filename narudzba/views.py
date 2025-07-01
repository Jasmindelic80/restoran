
from django.shortcuts import render, get_object_or_404, redirect
from .models import Narudzba
from .forms import NarudzbaForm

def narudzba_list(request):
    # Primer, renderujemo template
    return render(request, 'narudzba/narudzba_list.html')


def narudzba_list(request):
    narudzbe = Narudzba.objects.all().order_by('-datum')
    return render(request, 'narudzba/narudzba_list.html', {'narudzbe': narudzbe})

def narudzba_detail(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    return render(request, 'narudzba/narudzba_detail.html', {'narudzba': narudzba})

def narudzba_create(request):
    if request.method == 'POST':
        form = NarudzbaForm(request.POST)
        if form.is_valid():
            narudzba = form.save()
            return redirect('narudzba_detail', pk=narudzba.pk)
    else:
        form = NarudzbaForm()
    return render(request, 'narudzba/narudzba_create.html', {'form': form})

def narudzba_update(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    if request.method == 'POST':
        form = NarudzbaForm(request.POST, instance=narudzba)
        if form.is_valid():
            form.save()
            return redirect('narudzba_detail', pk=narudzba.pk)
    else:
        form = NarudzbaForm(instance=narudzba)
    return render(request, 'narudzba/narudzba_update.html', {'form': form, 'narudzba': narudzba})

def narudzba_delete(request, pk):
    narudzba = get_object_or_404(Narudzba, pk=pk)
    if request.method == 'POST':
        narudzba.delete()
        return redirect('narudzba_list')
    return render(request, 'narudzba/narudzba_delete.html', {'narudzba': narudzba})
