import base64
import hashlib
import json
import os
import subprocess
import uuid

import pandas as pd
from django.conf import settings
from django.http import (FileResponse, Http404, HttpResponseBadRequest,
                         JsonResponse)
from django.shortcuts import redirect, render

from .forms import UploadCSVForm


def index(request):
    jwt = request.COOKIES.get('zrok-access', '')

    if jwt:
        payload = jwt.split('.')[1]  # Get the payload of the JWT
        # Add padding to the payload for correct decoding
        payload += '=' * (-len(payload) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload).decode('utf-8')

        # Load the payload as a JSON object
        payload_json = json.loads(decoded_payload)

        # Get the email and iat claims
        email = payload_json.get('email', 'default')
        iat = payload_json.get('iat', '')

        # Concatenate the email and iat to create a unique string for each session
        unique_string = email + str(iat)
    else:
        # Generate a random, unique string
        email = 'tester@example.com'
        unique_string = email + str(uuid.uuid4())

    # Hash the unique string to create a unique directory name
    session_id = hashlib.md5(unique_string.encode()).hexdigest()

    # Construct the path to the "static" directory
    media_root = settings.MEDIA_ROOT

    # Create the temp_dir within the "static" directory
    temp_dir = os.path.join(media_root, f"session-{session_id}")

    request.session['temp_dir'] = temp_dir  # Save the temp_dir in the session

    # Create the directory if it doesn't exist
    os.makedirs(temp_dir, exist_ok=True)

    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_path = os.path.join(temp_dir, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            request.session['session_id'] = session_id  # Save the email hash in the session
            request.session['filename'] = file.name
            return redirect('display_data')  # Redirect to the new page
    else:
        form = UploadCSVForm()
    return render(request, 'index.html', {'form': form, 'email': email})


def display_data(request):
    filename = request.session.get('filename', '')  # Retrieve the filename from the session
    temp_dir = request.session.get('temp_dir', '')
    file_path = os.path.join(temp_dir, filename)  # Use the correct file name

    # Load the data from the CSV file
    data = pd.read_csv(file_path)
    # Convert the DataFrame into an HTML table
    table = data.to_html(index=False)

    return render(request, 'display_data.html', {'table': table})


def generate_radial(request):
    title = request.GET.get('title', '')  # Retrieve the title from the query parameters
    image_type = request.GET.get('type', '')  # Retrieve the image type from the query parameters
    labels = request.GET.get('labels', '')
    legend = request.GET.get('legend', '')
    filename = request.session.get('filename', '')  # Retrieve the filename from the session
    temp_dir = request.session.get('temp_dir', '')
    file_path = os.path.join(temp_dir, filename)  # Use the correct file name
    print(f"Got title '{title}', image_type '{image_type}', labels '{labels}', legend '{legend}'")
    # Run the generate_radial.py script and pass the file_path as an argument
    cmd_args = ['python', 'generate.py', title, file_path,
                            "--legend" if legend == "true" else "--no-legend",
                            "--labels" if labels == "true" else "--no-labels",
                            f"--image-type={image_type}"]
    print("Running command:", cmd_args)
    result = subprocess.run(cmd_args, capture_output=True, text=True)

    # Log the output and errors
    print("Output:", result.stdout)
    print("Error:", result.stderr)

    # Remove the .csv suffix from file_path and add the .png suffix
    img_path = f"{os.path.splitext(file_path)[0]}.{image_type}"

    # Save the path of the generated PNG file in the session
    request.session['img_path'] = img_path

    return JsonResponse({'status': 'success'})


def display_image(request):
    img_path = request.session.get('img_path', '')  # Retrieve the path from the session
    if not img_path:
        raise Http404("Image not found")

    # Extract the file name from img_path
    file_name = os.path.basename(img_path)
    if not file_name:
        raise Http404("File name not found")

    return render(request, 'display_image.html', {'file_name': file_name})


def serve_file(request, file_name):
    if not file_name:
        return HttpResponseBadRequest("File name cannot be empty")

    # Retrieve the temp_dir from the session
    temp_dir = request.session.get('temp_dir', '')

    # Construct the full file path
    file_path = os.path.join(temp_dir, file_name)

    # Check if the file is in the session's temp directory and exists
    if os.path.commonprefix([temp_dir, file_path]) != temp_dir or not os.path.exists(file_path):
        raise Http404("File not found")

    # Serve the file
    return FileResponse(open(file_path, 'rb'))
