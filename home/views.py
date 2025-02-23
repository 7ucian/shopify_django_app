from django.shortcuts import render
import shopify
import os
from shopify_app.decorators import shop_login_required
from datetime import timedelta, datetime
from django.core.files.storage import FileSystemStorage
from collections import defaultdict
from pathlib import Path
from django.conf import settings

from .forms import DocFileUploadForm
from .functions import generate_unique_filename, scan_documentation_files


@shop_login_required
def index(request):
    referer = request.META.get("HTTP_REFERER", "")
    origin = request.META.get("HTTP_ORIGIN", "")

    if referer == 'https://admin.shopify.com/': 

        shop_id = shopify.Shop.current()
        print("Shop_ID:", shop_id)
        api_key = os.environ.get('SHOPIFY_API_KEY')

        products = shopify.Product.find(limit=3)
        orders = shopify.Order.find(limit=3, order="created_at DESC")
        context = {}
        context['SHOPIFY_API_KEY'] = api_key
        context['products'] = products
        context['orders'] = orders
    
        return render(request, 'home/index.html', context)
    else:
        return render(request, 'shopify_app/login.html')


@shop_login_required
def upload_document(request):
    if request.method == 'POST':
            form = DocFileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    if 'document' not in request.FILES:
                        form.add_error('document', 'No file was uploaded')
                        raise ValueError("No file uploaded")
                        
                    uploaded_file = request.FILES['document']
                    
                    # Save the file
                    unique_filename = generate_unique_filename(uploaded_file.name)
                    file_location = os.path.join(settings.MEDIA_ROOT, 'documents', datetime.now().strftime('%Y-%m-%d'))
                    fs = FileSystemStorage(location=file_location)
                    
                    saved_file = fs.save(unique_filename, uploaded_file)
                    file_path = fs.path(saved_file)

                except Exception as e:
                    # Clean up the file if something went wrong
                    if 'file_path' in locals():
                        try:
                            os.remove(file_path)
                        except OSError:
                            pass
                    form.add_error(None, f"Error uploading file: {str(e)}")

    else:   # GET request
        form = DocFileUploadForm()
    context = {}
    context['form'] = form
    file_data = scan_documentation_files(request)
    context['file_data'] = file_data
    return render(request, 'home/upload_document.html', context)