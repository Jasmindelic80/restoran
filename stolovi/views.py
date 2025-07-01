from django.shortcuts import render, get_object_or_404, redirect
from .models import Sto
from .forms import StoForm

def stolovi_list(request):
    stolovi = Sto.objects.all()
    return render(request, 'stolovi/stolovi_list.html', {'stolovi': stolovi})

def sto_detail(request, pk):
    sto = get_object_or_404(Sto, pk=pk)
    return render(request, 'stolovi/sto_detail.html', {'sto': sto})

def sto_create(request):
    if request.method == 'POST':
        form = StoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stolovi_list')
    else:
        form = StoForm()
    return render(request, 'stolovi/sto_create.html', {'form': form})

def sto_update(request, pk):
    sto = get_object_or_404(Sto, pk=pk)
    if request.method == 'POST':
        form = StoForm(request.POST, instance=sto)
        if form.is_valid():
            form.save()
            return redirect('stolovi_list')
    else:
        form = StoForm(instance=sto)
    return render(request, 'stolovi/sto_update.html', {'form': form, 'sto': sto})

def sto_delete(request, pk):
    sto = get_object_or_404(Sto, pk=pk)
    if request.method == 'POST':
        sto.delete()
        return redirect('stolovi_list')
    return render(request, 'stolovi/sto_delete.html', {'sto': sto})

