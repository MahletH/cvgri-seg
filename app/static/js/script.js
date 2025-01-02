document.getElementById('segmentationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const response = await fetch('/api/segment', {
        method: 'POST',
        body: formData,
    });

    const result = await response.json();

    if (response.ok) {
        document.getElementById('result').innerHTML = `
            <h2>Segmented Image</h2>
            <img src="${result.segmented_image}" alt="Segmented">
        `;
    } else {
        document.getElementById('result').innerText = `Error: ${result.error}`;
    }
});
