from django.shortcuts import render


def login_view(request):
    return render(request, 'MainApp/login.html')

def dashboard_view(request):
    return render(request, 'MainApp/dashboard.html')

def clients_view(request):
    return render(request, 'MainApp/clients.html')

def credits_view(request):
    return render(request, 'MainApp/credits.html')

def epargne_view(request):
    return render(request, 'MainApp/epargne.html')

def rapports_view(request):
    return render(request, 'MainApp/rapports.html')
