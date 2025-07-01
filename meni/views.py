from .models import Stavka
from django.contrib.auth import  logout
from django.shortcuts import render, redirect
from .forms import StavkaForm
from django.shortcuts import get_object_or_404


def meni_list(request):
    stavke = Stavka.objects.all()
    return render(request, 'meni/meni_list.html', {'stavke': stavke})


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
