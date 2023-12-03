# facedetection/urls.py

from django.urls import path
from .views import face_detection, video_feed, capture_image, upload_known_image
# ,capture_result, match_faces, capture_image

urlpatterns = [
    path('', face_detection, name='face_detection'),
    path('video_feed/', video_feed, name='video_feed'), 
    path('upload_known_image/', upload_known_image, name='upload_known_image'),
    path('capture_image/', capture_image, name='capture_image'),
  
    # path('match_faces/', match_faces, name='match_faces'),
    # path('capture_result/', capture_result, name='capture_result'),
]
