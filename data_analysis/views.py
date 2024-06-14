from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

def handle_uploaded_file(f):
    fs = FileSystemStorage()
    filename = fs.save(f.name, f)
    uploaded_file_url = fs.url(filename)
    return uploaded_file_url

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_url = handle_uploaded_file(request.FILES['file'])
            try:
                data = pd.read_csv('.' + file_url)
            except Exception as e:
                return render(request, 'data_analysis/upload.html', {'form': form, 'error': 'Error reading file: ' + str(e)})

            # Basic Data Analysis
            head = data.head().to_html()
            desc = data.describe().to_html()
            missing_values = data.isnull().sum().reset_index().to_html()

            # Data Visualization
            plt.figure(figsize=(10, 6))
            sns.histplot(data.select_dtypes(include=[np.number]), kde=True)
            plt.title('Histograms for Numerical Columns')
            plt.tight_layout()
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()

            context = {
                'form': form,
                'head': head,
                'desc': desc,
                'missing_values': missing_values,
                'plot_url': plot_url,
            }
            return render(request, 'data_analysis/results.html', context)
    else:
        form = UploadFileForm()
    return render(request, 'data_analysis/upload.html', {'form': form})
