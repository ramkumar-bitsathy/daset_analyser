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
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def manipulate_dataset(request):
    error_message = None
    success_message = None

    # Check if dataset exists in the session
    if 'dataset' not in request.session:
        error_message = "No dataset available for manipulation. Please upload a dataset first."
    else:
        # Load the dataset from the session
        dataset_json = request.session['dataset']
        dataset = pd.read_json(StringIO(dataset_json))

        if request.method == 'POST':
            operation = request.POST.get('operation')
            
            try:
                if operation == 'remove_nulls':
                    dataset = dataset.dropna()
                    success_message = "Null values removed successfully."

                elif operation == 'fill_nulls':
                    fill_value = request.POST.get('fill_value')
                    dataset = dataset.fillna(fill_value)
                    success_message = f"Null values filled with '{fill_value}' successfully."

                elif operation == 'convert_categorical':
                    column_name = request.POST.get('column_name')
                    if column_name in dataset.columns:
                        dataset[column_name] = dataset[column_name].astype('category').cat.codes
                        success_message = f"Column '{column_name}' converted to numerical successfully."
                    else:
                        error_message = f"Column '{column_name}' does not exist."

                elif operation == 'scaling':
                    scaling_method = request.POST.get('scaling_method')
                    scaler = StandardScaler() if scaling_method == 'standard' else MinMaxScaler()
                    numerical_cols = dataset.select_dtypes(include=['number']).columns
                    dataset[numerical_cols] = scaler.fit_transform(dataset[numerical_cols])
                    success_message = f"Dataset scaled using {scaling_method} scaling successfully."

                else:
                    error_message = "Invalid operation selected."

                # Update the dataset in the session
                request.session['dataset'] = dataset.to_json()

            except Exception as e:
                error_message = str(e)

    paginated_dataset,processed_data =  prepare_dataset(request)
    
    # Render the home page with appropriate messages
    return render(request, "home.html", {
        "manipulation_error_message": error_message,
        "manipulation_success_message": success_message,
        "processed_data": processed_data,
        "dataset_view": paginated_dataset if dataset is not None else None,
    })


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

def prepare_dataset(request):
    processed_data = {}
# Retrieve dataset from the session if available
    if 'dataset' in request.session:
        dataset_json = request.session['dataset']
        dataset = pd.read_json(io.StringIO(dataset_json))

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
                    "Data_Type": str(dataset[col].dtype),
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
                    "Data_Type": str(dataset[col].dtype),
                    "Null_Values": dataset[col].isnull().sum(),
                    "Unique_Values": dataset[col].nunique(),
                    "Mode": dataset[col].mode()[0] if not dataset[col].mode().empty else "N/A",
                }
            stats.append(column_stats)

        processed_data = stats

        return paginated_dataset,processed_data

def process_dataset(request):
    processed_data = {}
    error_message = None
      # Initialize dataset variable

    if request.method == 'POST':
        # Check if a file is uploaded
        if 'dataset' in request.FILES:
            uploaded_file = request.FILES['dataset']
            try:
                # Load the dataset into a DataFrame
                if uploaded_file.name.endswith('.csv'):
                    dataset = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    dataset = pd.read_excel(uploaded_file)
                else:
                    error_message = "Unsupported file format. Please upload a CSV or XLSX file."
                
                if dataset is not None:
                    # Store the dataset in the session
                    request.session['dataset'] = dataset.to_json()
            except Exception as e:
                error_message = f"Failed to process the file: {str(e)}"
        else:
            error_message = "No dataset provided. Please upload a file."
    paginated_dataset,processed_data =  prepare_dataset(request)
    

    # Render the template with the context data
    return render(request, "home.html", {
        "processed_data": processed_data,
        "error_message": error_message,
        "dataset_view": paginated_dataset if dataset is not None else None,
    })