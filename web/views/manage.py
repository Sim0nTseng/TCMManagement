from django.shortcuts import render

def manage_dashboard(request, nid):
    return render(request,'web/manage_dashboard.html')

def manage_issue(request, nid):
    return render(request,'web/manage_issue.html')