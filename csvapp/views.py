from django.shortcuts import render
import pandas as pd

def home(request):
    return render(request, 'csvapp\home.html')

def visualization(request):
    return render(request, r'csvapp\visualization.html')

def process_dataset(request):
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.FILES['dataset']
        dataset = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

        # Get selected details
        selected_details = request.POST.getlist('details')
        processed_data = {}

        # Process based on selected details
        if 'null_values' in selected_details:
            processed_data['Null Values'] = dataset.isnull().sum().to_dict()
        if 'data_types' in selected_details:
            processed_data['Data Types'] = dataset.dtypes.astype(str).to_dict()
        if 'statistical_info' in selected_details:
            processed_data['Statistical Info'] = dataset.describe().to_string()
        if 'unique_values' in selected_details:
            processed_data['Unique Values'] = dataset.nunique().to_dict()
        if 'column_summary' in selected_details:
            processed_data['Column Summary'] = dataset.head().to_string()

        return render(request, 'csvapp\home.html', {'processed_data': processed_data})

    return render(request, 'csvapp\home.html')
