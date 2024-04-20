
from django.shortcuts import render
from django.http import HttpResponse
from fpdf import FPDF
import requests
import json
import random
import string
import os
from django.shortcuts import render
from django.conf import settings


def home(request):
    error = ""
    if request.method == 'POST':
        # Assuming you have a form with a file input field named 'image_file'
        image_file = request.FILES['image_file']

        # Handle the uploaded file, save it if necessary
        # Here, I'm assuming you're saving it temporarily in the media directory
        image_path = 'media/' + image_file.name
        print(image_path)
        with open(image_path, 'wb') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # Generate PDF path
        pdf_path = 'media/'+image_file.name.split(".")[0]+'.pdf'

        # Convert image to PDF
        image_to_pdf(image_path, pdf_path)

        # You may want to serve the PDF for download or display it in the browser
        try :
            error = "no"
            with open(pdf_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename=output_pdf.pdf'
                return response
        except:
            error = "yes"
    return render(request, "convert_image_to_pdf.html", locals())


def image_to_pdf(image_path, pdf_path):
    pdf = FPDF()
    pdf.add_page()

    # Set image size to fit the page
    pdf.image(image_path, x=0, y=0, w=210, h=297)

    pdf.output(pdf_path, "F")

# def convert_image_to_pdf(request):
#     if request.method == 'POST':
#         # Assuming you have a form with a file input field named 'image_file'
#         image_file = request.FILES['image_file']

#         # Handle the uploaded file, save it if necessary
#         # Here, I'm assuming you're saving it temporarily in the media directory
#         image_path = 'media/' + image_file.name
#         print(image_path)
#         with open(image_path, 'wb') as destination:
#             for chunk in image_file.chunks():
#                 destination.write(chunk)

#         # Generate PDF path
#         pdf_path = 'media/output_pdf.pdf'

#         # Convert image to PDF
#         image_to_pdf(image_path, pdf_path)

#         # You may want to serve the PDF for download or display it in the browser
#         with open(pdf_path, 'rb') as pdf_file:
#             response = HttpResponse(pdf_file.read(), content_type='application/pdf')
#             response['Content-Disposition'] = 'inline; filename=output_pdf.pdf'
#             return response

#     return render(request, 'convert_image_to_pdf.html')

def generate_random_filename(length=7):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


def pdf_merger(request):
    error = ""
    if request.method == 'POST':
        pdf1_temp = request.FILES['pdf1']
        pdf2_temp = request.FILES['pdf2']
        
        # Save the uploaded PDF files in the media directory
        pdf1_path = os.path.join(settings.MEDIA_ROOT, pdf1_temp.name)
        pdf2_path = os.path.join(settings.MEDIA_ROOT, pdf2_temp.name)
        
        with open(pdf1_path, 'wb') as destination:
            for chunk in pdf1_temp.chunks():
                destination.write(chunk)
        with open(pdf2_path, 'wb') as destination:
            for chunk in pdf2_temp.chunks():
                destination.write(chunk)
                
        instructions = {
            'parts': [
                {'file': 'first_half'},
                {'file': 'second_half'}
            ]
        }

        response = requests.post(
            'https://api.pspdfkit.com/build',
            headers={
                'Authorization': 'Bearer pdf_live_eZFObhRnaQa4cufDtiSxpfLKAcAIsjYQqQeF3nipnn8'
            },
            files={
                'first_half': open(pdf1_path, 'rb'),
                'second_half': open(pdf2_path, 'rb')
            },
            data={
                'instructions': json.dumps(instructions)
            },
            stream=True
        )
        
        try:
            error = "no"
            if response.ok:
                # Save the resulting PDF file in the media directory
                result_pdf_path = os.path.join(settings.MEDIA_ROOT, 'result2.pdf')
                with open(result_pdf_path, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=8096):
                        fd.write(chunk)
            else:
                print(response.text)
                exit()
        except Exception as e:
            error = "yes"
            print(str(e))
    
    return render(request, "pdf_merger.html", locals())