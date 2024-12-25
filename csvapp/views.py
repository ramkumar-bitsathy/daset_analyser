from django.shortcuts import render
from django.core.paginator import Paginator

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import io
import base64

def generate_visualization(request):
    if 'dataset' not in request.session:
        return render(request, 'visualization.html', {'error': 'No dataset found. Please upload a dataset first.'})

    # Retrieve dataset from session
    dataset_json = request.session['dataset']
    dataset = pd.read_json(StringIO(dataset_json))

    if request.method == 'POST':
        
        features_type = request.POST.get('features_type')
        print(features_type)
        # Univariate: Only one column for X
        if features_type == 'univariate':
            chart_type = request.POST.get('univariate_chart_type')
            x_column = request.POST.get('univariate_x_column')
            
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
            chart_type = request.POST.get('bivariate_chart_type')
            x_column = request.POST.get('bivariate_x_column')
            y_column = request.POST.get('bivariate_y_column')

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
            chart_type = request.POST.get('multivariate_chart_type')
            x_column = request.POST.get('multivariate_x_column')
            y_column = request.POST.get('multivariate_y_column')
            z_column = request.POST.get('multivariate_z_column')

            # Create plot
            plt.figure(figsize=(10, 6))
            try:
                if chart_type == 'scatter':
                    sns.scatterplot(data=dataset, x=x_column, y=y_column, hue=z_column)
                elif chart_type == "pairplot":
                    dataset1 = request.session.get('dataset')
                    subset = dataset1[[x_column,y_column,z_column]]
                    sns.pairplot(subset)
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
    processed_data = {}
    error_message = None
    dataset = None  # Initialize dataset variable

    if request.method == 'POST':
        # Check if a file is uploaded
        if 'dataset' in request.FILES:
            uploaded_file = request.FILES['dataset']
            # Load the dataset into a DataFrame
            dataset = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            # Store the dataset in the session
            request.session['dataset'] = dataset.to_json()
        elif 'dataset' not in request.session:
            error_message = "No dataset provided. Please upload a file."

    # Retrieve dataset from the session if available
    if 'dataset' in request.session:
        dataset_json = request.session['dataset']
        dataset = pd.read_json(StringIO(dataset_json))

    # Process the dataset if it exists
    if dataset is not None:
        # Pagination setup
        page_number = request.GET.get('page', 1)  # Get the current page number
        paginator = Paginator(dataset.values.tolist(), 10)  # 10 rows per page
        current_page = paginator.get_page(page_number)
        paginated_dataset = {
            'columns': dataset.columns.tolist(),
            'rows': current_page.object_list,
            'current_page': current_page.number,
            'num_pages': paginator.num_pages,
            'has_previous': current_page.has_previous(),
            'has_next': current_page.has_next(),
            'previous_page_number': current_page.previous_page_number() if current_page.has_previous() else None,
            'next_page_number': current_page.next_page_number() if current_page.has_next() else None,
        }

        stats = []
        for col in dataset.columns:
            if pd.api.types.is_numeric_dtype(dataset[col]):
                column_stats = {
                    "Column": col,
                    "Data_Type": dataset[col].dtype,
                    "Null_Values": dataset[col].isnull().sum(),
                    "Mean": dataset[col].mean(),
                    "Median": dataset[col].median(),
                    "Mode": dataset[col].mode()[0] if not dataset[col].mode().empty else "N/A",
                    "percentile_25": dataset[col].quantile(0.25),
                    "percentile_50": dataset[col].quantile(0.5),
                    "percentile_75": dataset[col].quantile(0.75),
                }
            else:
                column_stats = {
                    "Column": col,
                    "Data_Type": dataset[col].dtype,
                    "Null_Values": dataset[col].isnull().sum(),
                    "Unique_Values": dataset[col].nunique(),
                    "Mode": dataset[col].mode()[0] if not dataset[col].mode().empty else "N/A",
                }
            stats.append(column_stats)

        processed_data = stats

    # Render the template with the context data
    return render(request, "home.html", {
        "processed_data": processed_data,
        "error_message": error_message,
        "dataset_view": paginated_dataset if dataset is not None else None,
    })