# facedetection/views.py

import time
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import face_recognition
import os
import cv2
import threading

# Load the known image (for example, your reference image)
KNOWN_IMAGE_PATH = os.path.join('media', 'known_image.jpg')
KNOWN_IMAGE = face_recognition.load_image_file(KNOWN_IMAGE_PATH)
KNOWN_FACE_ENCODINGS = face_recognition.face_encodings(KNOWN_IMAGE)[0]  # Assuming there is only one face in the known image

# Initialize camera
camera = cv2.VideoCapture(0)
lock = threading.Lock()

captured_image_path = None  # Variable to store the path of the captured image


# Function to generate video frames with face recognition
def generate():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Perform face detection in the frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Draw rectangles around the faces and update the result text
        for i, (top, right, bottom, left) in enumerate(face_locations):
            captured_face_encoding = face_encodings[i]
            results = face_recognition.compare_faces([KNOWN_FACE_ENCODINGS], captured_face_encoding)
            result_text = "Face Matched: Known Person" if results[0] else "No Match Found"

            # Draw rectangles around the faces
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw the result text on the face rectangle
            font = cv2.FONT_HERSHEY_DUPLEX
            font_size = 0.8
            font_thickness = 1
            text_color = (0, 0, 255)
            cv2.putText(frame, result_text, (left, top - 10), font, font_size, text_color, font_thickness, cv2.LINE_AA)

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()

        # Yield the frame to be streamed
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n'
               b'--result\r\n'
               b'Content-Type: text/plain\r\n\r\n' + result_text.encode() + b'\r\n\r\n')


# Function to capture an image from the video feed
def capture_image(request):
    global captured_image_path

    # Capture a frame from the video feed
    success, frame = camera.read()

    if success:
        # Generate a unique filename for the captured image
        timestamp = int(time.time())
        filename = f"captured_image_{timestamp}.jpg"
        captured_image_path = os.path.join('media', filename)

        # Save the captured image
        cv2.imwrite(captured_image_path, frame)

        # Perform face recognition on the captured image
        captured_image = face_recognition.load_image_file(captured_image_path)
        captured_face_encoding = face_recognition.face_encodings(captured_image)[0]

        # Compare the face encodings
        results = face_recognition.compare_faces([KNOWN_FACE_ENCODINGS], captured_face_encoding)

        if results[0]:
            result_text = "Face Matched: Known Person"
        else:
            result_text = "No Match Found"

        return JsonResponse({'result': result_text, 'image_path': captured_image_path})

    return JsonResponse({'result': 'Error capturing image'})

# Function to render the face detection page
def face_detection(request):
    return render(request, 'facedetection/face_detection.html')

# Function to render the match faces page
def match_faces(request):
    return render(request, 'facedetection/match_faces.html')

# Function to stream video feed
def video_feed(request):
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


# View to handle known image upload
def upload_known_image(request):
    if request.method == 'POST' and request.FILES.get('known_image'):
        known_image = request.FILES['known_image']

        # Save the uploaded image
        known_image_path = os.path.join('media', 'known_image.jpg')
        with open(known_image_path, 'wb') as destination:
            for chunk in known_image.chunks():
                destination.write(chunk)

        # Reload the known image and update KNOWN_FACE_ENCODINGS
        global KNOWN_FACE_ENCODINGS
        KNOWN_IMAGE = face_recognition.load_image_file(known_image_path)
        KNOWN_FACE_ENCODINGS = face_recognition.face_encodings(KNOWN_IMAGE)[0]

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

# *****************************************************************************

# Function to generate video frames
# def generate():
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break

#         # Perform face detection in the frame
#         face_locations = face_recognition.face_locations(frame)
#         face_encodings = face_recognition.face_encodings(frame, face_locations)

#         # Draw rectangles around the faces
#         for (top, right, bottom, left) in face_locations:
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#         # Convert the frame to JPEG format
#         ret, jpeg = cv2.imencode('.jpg', frame)
#         frame_bytes = jpeg.tobytes()

#         # Yield the frame to be streamed
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
# facedetection/views.py


# # facedetection/views.py

# from django.shortcuts import render
# from django.http import JsonResponse, StreamingHttpResponse
# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# import face_recognition
# from PIL import Image, ImageDraw, ImageFont
# import os
# import cv2
# import threading
# import time

# # Load the known image (for example, your reference image)
# KNOWN_IMAGE_PATH = os.path.join('media', 'known_image.jpg')
# KNOWN_IMAGE = face_recognition.load_image_file(KNOWN_IMAGE_PATH)
# KNOWN_FACE_LOCATIONS = face_recognition.face_locations(KNOWN_IMAGE)
# KNOWN_FACE_ENCODINGS = face_recognition.face_encodings(KNOWN_IMAGE, KNOWN_FACE_LOCATIONS)

# # Initialize camera
# camera = cv2.VideoCapture(0)
# lock = threading.Lock()

# # Function to generate video frames
# def generate():
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break

#         # Perform face detection in the frame
#         face_locations = face_recognition.face_locations(frame)
#         face_encodings = face_recognition.face_encodings(frame, face_locations)

#         # Draw rectangles around the faces
#         for (top, right, bottom, left) in face_locations:
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#         # Convert the frame to JPEG format
#         ret, jpeg = cv2.imencode('.jpg', frame)
#         frame_bytes = jpeg.tobytes()

#         # Yield the frame to be streamed
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')



# # Function to stream video feed
# def video_feed(request):
#     return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

# # Function to render the face detection page
# def face_detection(request):
#     return render(request, 'facedetection/face_detection.html')

# # Function to match faces
# def match_faces(request):
#     return render(request, 'facedetection/match_faces.html')

# # Start the update_known_faces thread
# update_thread = threading.Thread(target=face_detection)
# update_thread.daemon = True
# update_thread.start()


# =============================================================================================





# Thread to continuously update the known face encodings
# def update_known_faces():
#     global KNOWN_FACE_LOCATIONS, KNOWN_FACE_ENCODINGS

#     while True:
#         # Load the known image
#         known_image = face_recognition.load_image_file(KNOWN_IMAGE_PATH)

#         # Find all face locations and face encodings in the known image
#         known_face_locations = face_recognition.face_locations(known_image)
#         known_face_encodings = face_recognition.face_encodings(known_image, known_face_locations)

#         # Update the global variables
#         with lock:
#             KNOWN_FACE_LOCATIONS = known_face_locations
#             KNOWN_FACE_ENCODINGS = known_face_encodings

#         # Sleep for a while before the next update
#         time.sleep(60)  # Update every 60 seconds


# # Function to capture an image
# def capture_image(request):
#     if request.method == 'POST' and request.POST.get('image_data'):
#         image_data = request.POST['image_data']

#         # Decode base64 image data and save it to the media folder
#         image_data_decoded = ContentFile(image_data, name='captured_image.jpg')
#         image_path = default_storage.save('captured_image.jpg', image_data_decoded)

#         # Load the captured image
#         captured_image_path = os.path.join('media', 'captured_image.jpg')
#         captured_image = face_recognition.load_image_file(captured_image_path)

#         # Find all face locations and face encodings in the captured image
#         captured_face_locations = face_recognition.face_locations(captured_image)
#         captured_face_encodings = face_recognition.face_encodings(captured_image, captured_face_locations)

#         # Perform face matching logic
#         if captured_face_encodings:
#             # Assuming there is only one face in the captured image
#             captured_face_encoding = captured_face_encodings[0]

#             # See if the captured face matches any known faces
#             matches = face_recognition.compare_faces(KNOWN_FACE_ENCODINGS, captured_face_encoding)

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 result = 'Face Matched: Known Person'
#             else:
#                 result = 'No Match Found'

#             return render(request, 'facedetection/capture_result.html', {'result': result})


#     return render(request, 'facedetection/capture_result.html', {'error': 'Invalid request'})


# def capture_result(request):
#     return render(request, 'facedetection/capture_result.html')
