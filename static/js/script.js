document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');
    const pastAnalysesList = document.getElementById('past-analyses');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showError('Please select a file.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        loading.classList.remove('hidden');
        result.classList.add('hidden');
        error.classList.add('hidden');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showResult(data.analysis);
                loadPastAnalyses();
            } else {
                showError(data.error || 'An error occurred during analysis.');
            }
        } catch (err) {
            showError('An error occurred while sending the request.');
        } finally {
            loading.classList.add('hidden');
        }
    });

    function showResult(analysis) {
        result.textContent = analysis;
        result.classList.remove('hidden');
    }

    function showError(message) {
        error.textContent = message;
        error.classList.remove('hidden');
    }

    async function loadPastAnalyses() {
        try {
            const response = await fetch('/analyses');
            const analyses = await response.json();
            
            pastAnalysesList.innerHTML = '';
            analyses.forEach(analysis => {
                const li = document.createElement('li');
                li.textContent = `${analysis.filename} (${new Date(analysis.created_at).toLocaleString()})`;
                li.addEventListener('click', () => loadAnalysis(analysis.id));
                pastAnalysesList.appendChild(li);
            });
        } catch (err) {
            console.error('Error loading past analyses:', err);
        }
    }

    async function loadAnalysis(id) {
        try {
            const response = await fetch(`/analysis/${id}`);
            const analysis = await response.json();
            showResult(analysis.result);
        } catch (err) {
            showError('Error loading analysis.');
        }
    }

    // Load past analyses when the page loads
    loadPastAnalyses();
});
