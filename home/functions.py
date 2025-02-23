from datetime import timedelta, datetime
import os
from pathlib import Path

def generate_unique_filename(filename):
    """Generate a unique filename with timestamp."""
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{name}_{timestamp}{ext}" 


def scan_documentation_files(request):
    """Determine path"""
    base_dir = Path(__file__).resolve().parent.parent
    if str(base_dir).find('Users/muz') == -1:
        if str(base_dir).find('invoicer_DEV') == -1:
            base_path = Path('/var/www/html/worldcz.eu/shopify_django_app/documents') # Production
        else: 
            base_path = Path('/var/www/html/worldcz.eu/invoicer_DEV/documents')  # UAT
    else:
        base_path = Path('/Users/muz/Dev/django/shopify_django_app/documents')      # Development  
    
    file_data = []
    
   # Get directories with creation times
    directories = [(d, datetime.fromtimestamp(os.path.getctime(d))) 
                 for d, _, _ in os.walk(base_path)]
    directories.sort(key=lambda x: x[1], reverse=True)
   
    for dir_path, _ in directories:
       txt_files = []
       for file in Path(dir_path).glob('*.*'):
           txt_files.append({
               'name': file.name,
               'path': str(file.absolute()),
               'created': datetime.fromtimestamp(os.path.getctime(file))
           })
       
       if txt_files:
           # Sort files by creation date
           txt_files.sort(key=lambda x: x['created'], reverse=True)
           file_data.append({
               'directory': str(Path(dir_path).relative_to(base_path)),
               'files': txt_files
           })    

    return file_data
