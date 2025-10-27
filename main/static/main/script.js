document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const audioFileInput = document.getElementById('audio-file');
    const progressBarContainer = document.querySelector('.progress-container');
    const progressBar = document.getElementById('progress-bar');
    const resultsContainer = document.getElementById('results-container');
    const mouth = document.getElementById('mouth');
    const customUploadButton = document.querySelector('.custom-file-upload');

    // Update the label when a file is chosen
    audioFileInput.addEventListener('change', () => {
        if (audioFileInput.files.length > 0) {
            customUploadButton.textContent = audioFileInput.files[0].name;
        } else {
            customUploadButton.textContent = 'انتخاب فایل';
        }
    });

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!audioFileInput.files.length) {
            alert('لطفاً یک فایل صوتی انتخاب کنید.');
            return;
        }

        const formData = new FormData();
        formData.append('audio_file', audioFileInput.files[0]);

        // Reset UI
        resultsContainer.innerHTML = '';
        progressBar.style.width = '0%';
        progressBarContainer.style.display = 'block';
        updateMouth(50); // Reset to neutral

        try {
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    progressBar.style.width = percentComplete + '%';
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const results = JSON.parse(xhr.responseText);
                    displayResults(results);
                } else {
                    resultsContainer.innerHTML = `<p style="color: red;">خطا: ${xhr.statusText}</p>`;
                }
                 setTimeout(() => { progressBarContainer.style.display = 'none'; }, 1000);
            });

            xhr.addEventListener('error', () => {
                resultsContainer.innerHTML = '<p style="color: red;">خطایی در هنگام آپلود رخ داد.</p>';
                progressBarContainer.style.display = 'none';
            });

            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            xhr.open('POST', '/analyze/', true);
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.send(formData);

        } catch (error) {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<p style="color: red;">یک خطای ناشناخته رخ داد.</p>';
            progressBarContainer.style.display = 'none';
        }
    });

    function displayResults(results) {
        if (results.error) {
            resultsContainer.innerHTML = `<p style="color: red;">${results.error}</p>`;
            return;
        }

        let resultsHTML = '<h3>نتایج تحلیل:</h3><ul>';
        let maxEmotion = 'happy'; // Default emotion
        let maxScore = -1;

        for (const [emotion, score] of Object.entries(results)) {
            resultsHTML += `<li><strong>${translateEmotion(emotion)}:</strong> ${score}%</li>`;
            if (score > maxScore) {
                maxScore = score;
                maxEmotion = emotion;
            }
        }
        resultsHTML += '</ul>';
        resultsContainer.innerHTML = resultsHTML;

        // Update emoji based on the dominant emotion's score
        if (maxEmotion === 'happy') {
            updateMouth(results.happy);
        } else if (maxEmotion === 'sad') {
            updateMouth(-results.sad);
        } else { // Angry
            updateMouth(-results.angry / 2); // Less sad-looking for angry
        }
    }

    function translateEmotion(emotion) {
        switch (emotion) {
            case 'happy': return 'شادی';
            case 'sad': return 'غم';
            case 'angry': return 'عصبانیت';
            default: return emotion;
        }
    }

    function updateMouth(sentimentScore) {
        // sentimentScore should be between -100 (sad) and 100 (happy)
        const curvature = sentimentScore * 0.2; // Scale score to a reasonable curvature
        const newPath = `M 40 80 Q 60 ${80 + curvature} 80 80`;
        mouth.setAttribute('d', newPath);
    }
});
