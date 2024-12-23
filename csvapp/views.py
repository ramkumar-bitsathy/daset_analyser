from django.shortcuts import render
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import io
import base64

def generate_visualization(request):
    if 'dataset' not in request.session:
        return render(request, 'visualization.html', {'error': 'No dataset found. Please upload a dataset first.'})

    # Retrieve dataset from session
    dataset_json = request.session['dataset']
    dataset = pd.read_json(dataset_json)

    if request.method == 'POST':
        chart_type = request.POST.get('chart_type')
        features_type = request.POST.get('features_type')

        # Univariate: Only one column for X
        if features_type == 'univariate':
            x_column = request.POST.get('x_column')
            y_column = None  # No Y column for univariate

            # Create plot
            plt.figure(figsize=(10, 6))
            try:
                if chart_type == 'bar':
                    sns.barplot(data=dataset, x=x_column)
                elif chart_type == 'scatter':
                    sns.scatterplot(data=dataset, x=x_column)
                elif chart_type == 'line':
                    sns.lineplot(data=dataset, x=x_column)
                elif chart_type == 'histogram':
                    sns.histplot(data=dataset, x=x_column, kde=True)
                elif chart_type == 'boxplot':
                    sns.boxplot(data=dataset, x=x_column)
                else:
                    raise ValueError("Unsupported chart type.")

                # Save plot to a string buffer
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()

                # Encode image to base64
                chart_base64 = base64.b64encode(image_png).decode('utf-8')

                return render(request, 'visualization.html', {'chart': chart_base64, 'columns': dataset.columns})

            except Exception as e:
                return render(request, 'visualization.html', {'error': str(e), 'columns': dataset.columns})

        # Bivariate: Two columns for X and Y
        elif features_type == 'bivariate':
            x_column = request.POST.get('x_column')
            y_column = request.POST.get('y_column')

            # Create plot
            plt.figure(figsize=(10, 6))
            try:
                if chart_type == 'scatter':
                    sns.scatterplot(data=dataset, x=x_column, y=y_column)
                elif chart_type == 'line':
                    sns.lineplot(data=dataset, x=x_column, y=y_column)
                elif chart_type == 'bar':
                    sns.barplot(data=dataset, x=x_column, y=y_column)
                elif chart_type == 'boxplot':
                    sns.boxplot(data=dataset, x=x_column, y=y_column)
                else:
                    raise ValueError("Unsupported chart type.")

                # Save plot to a string buffer
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()

                # Encode image to base64
                chart_base64 = base64.b64encode(image_png).decode('utf-8')

                return render(request, 'visualization.html', {'chart': chart_base64, 'columns': dataset.columns})

            except Exception as e:
                return render(request, 'visualization.html', {'error': str(e), 'columns': dataset.columns})

        # Multivariate: More than two columns
        elif features_type == 'multivariate':
            x_column = request.POST.get('x_column')
            y_column = request.POST.get('y_column')
            z_column = request.POST.get('z_column')

            # Create plot
            plt.figure(figsize=(10, 6))
            try:
                if chart_type == 'scatter':
                    sns.scatterplot(data=dataset, x=x_column, y=y_column, hue=z_column)
                elif chart_type == 'line':
                    sns.lineplot(data=dataset, x=x_column, y=y_column)
                elif chart_type == 'bar':
                    sns.barplot(data=dataset, x=x_column, y=y_column)
                elif chart_type == 'boxplot':
                    sns.boxplot(data=dataset, x=x_column, y=y_column)
                else:
                    raise ValueError("Unsupported chart type.")

                # Save plot to a string buffer
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()

                # Encode image to base64
                chart_base64 = base64.b64encode(image_png).decode('utf-8')

                return render(request, 'visualization.html', {'chart': chart_base64, 'columns': dataset.columns})

            except Exception as e:
                return render(request, 'visualization.html', {'error': str(e), 'columns': dataset.columns})

    return render(request, 'visualization.html', {'columns': dataset.columns})

def home(request):
    return render(request, 'home.html')


def process_dataset(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['dataset']
        dataset = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)

        selected_details = request.POST.getlist('details')
        processed_data = {}

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

        request.session['dataset'] = dataset.to_json()

        return render(request, 'home.html', {'processed_data': processed_data})

    return render(request, 'home.html')
