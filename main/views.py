from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from . import emotion_predictor
from django.conf import settings
from django.core.files.storage import default_storage

def index(request):
    return render(request, 'main/index.html')

@csrf_exempt # For simplicity in this example. Use proper CSRF handling in production.
def analyze_audio(request):
    if request.method == 'POST':
        if 'audio_file' not in request.FILES:
            return JsonResponse({'error': 'No audio file found'}, status=400)

        audio_file = request.FILES['audio_file']

        # Save the file temporarily
        file_name = default_storage.save(f"tmp/{audio_file.name}", audio_file)
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        try:
            # Predict emotion
            results = emotion_predictor.predict_emotion(file_path)
            return JsonResponse(results)
        finally:
            # Clean up the temporary file
            default_storage.delete(file_name)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
