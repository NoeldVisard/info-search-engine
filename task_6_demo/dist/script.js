const MAX_RESULTS = 10

document.querySelector('input[name="search-text"]')
    .addEventListener('keydown',
    function () {
        var query = document.querySelector('input[name="search-text"]').value;

        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'http://localhost:8000/search', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var results = JSON.parse(xhr.responseText);
                var resultsDiv = document.getElementById('results');
                resultsDiv.innerHTML = '';
                var resultNumber = 1
                results.forEach(result => {
                    if (resultNumber < MAX_RESULTS) {
                        var resultElement = document.createElement('div');
                        resultElement.textContent = resultNumber + '. ' + result[0];
                        resultsDiv.appendChild(resultElement);
                        resultNumber++
                    }
                });
            } else {
                document.getElementById('results').innerHTML = ''
            }
        };
        xhr.send(JSON.stringify({ query: query }));
})