from django.shortcuts import render, redirect


def index(request):

    return render(request,'web/index.html')

def logout(request):
    request.session.flush()
    return redirect('/index/')