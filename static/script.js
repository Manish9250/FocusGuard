document.addEventListener('DOMContentLoaded', function() {
    // --- Countdown logic (remains the same) ---
    const countdownElement = document.getElementById('countdown');
    setInterval(updateCountdown, 60000);
    updateCountdown();

    function updateCountdown() {
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                if (data.blocked && data.type === 'permanent') {
                    countdownElement.textContent = "FOR THE DAY";
                } else if (data.blocked && data.remaining_seconds > 0) {
                    const seconds = Math.floor(data.remaining_seconds);
                    const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
                    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
                    const s = String(seconds % 60).padStart(2, '0');
                    countdownElement.textContent = `${h}:${m}:${s}`;
                } else {
                    countdownElement.textContent = "You are free!";
                }
            });
    }

    // --- NEW and IMPROVED Data Dashboard Logic ---
    loadProductivityData();

    function loadProductivityData() {
        fetch('/api/data')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('data-dashboard').innerHTML = `<p>${data.error}</p>`;
                    return;
                }

                // Card 1: Productivity Score
                const scoreCard = document.getElementById('score-card');
                const score = data.productivity_score_percent;
                scoreCard.innerHTML = `
                    <h4>Overall Score</h4>
                    <div class="score-circle" style="--p:${score};">
                        <div>${score}%</div>
                    </div>
                `;

                // Card 2: Time by Category
                const categoryCard = document.getElementById('category-card');
                const time = data.time_by_category;
                categoryCard.innerHTML = `
                    <h4>Time Breakdown</h4>
                    <p><strong>Distracting:</strong> ${time.Distracting} min</p>
                    <p><strong>Productive:</strong> ${time.Productive} min</p>
                    <p><strong>Neutral:</strong> ${time.Neutral} min</p>
                `;

                // Card 3: Top Sites
                const sitesCard = document.getElementById('sites-card');
                let sitesHTML = '<h4>Top Sites by Duration</h4>';
                if (data.sites_by_duration && data.sites_by_duration.length > 0) {
                    sitesHTML += '<ul class="site-list">';
                    data.sites_by_duration.slice(0, 5).forEach(item => { // Show top 5
                        sitesHTML += `<li><strong>${item.site}:</strong> ${item.duration_minutes} min</li>`;
                    });
                    sitesHTML += '</ul>';
                } else {
                    sitesHTML += '<p>No site data recorded yet.</p>';
                }
                sitesCard.innerHTML = sitesHTML;
            })
            .catch(error => {
                document.getElementById('data-dashboard').innerHTML = `<p>Could not load productivity data.</p>`;
            });
    }
});