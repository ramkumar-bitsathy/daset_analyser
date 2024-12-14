import pandas as pd 
from django.shortcuts import render 
from django.http import JsonResponse


def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        df = pd.read_csv(csv_file)
        summary = df.describe().to_html()
        return render(request,'csvapp/upload.html',{'summary':summary})
        
    return render(request,'csvapp/upload.html')