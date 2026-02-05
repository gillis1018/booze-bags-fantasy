// Booze Bags Fantasy League - Main Application

let summaryData = null;
let allSeasonsData = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    setupNavigation();
    renderDashboard();
});

// Load JSON data
async function loadData() {
    try {
        const [summaryRes, seasonsRes] = await Promise.all([
            fetch('../data/summary.json'),
            fetch('../data/all_seasons.json')
        ]);

        summaryData = await summaryRes.json();
        allSeasonsData = await seasonsRes.json();

        console.log('Data loaded successfully');
    } catch (error) {
        console.error('Error loading data:', error);
        document.querySelector('.container').innerHTML = `
            <div class="card" style="text-align: center; padding: 3rem;">
                <h2>Error Loading Data</h2>
                <p>Make sure the data files exist in the /data folder.</p>
                <p>Run the fetch_data.py script to generate the data.</p>
            </div>
        `;
    }
}

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;

            // Update active states
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Show section
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.getElementById(section).classList.add('active');

            // Render section content
            switch(section) {
                case 'dashboard':
                    renderDashboard();
                    break;
                case 'standings':
                    renderStandings();
                    break;
                case 'all-time':
                    renderAllTime();
                    break;
                case 'champions':
                    renderChampions();
                    break;
                case 'drafts':
                    renderDrafts();
                    break;
            }
        });
    });
}

// Render Dashboard
function renderDashboard() {
    if (!summaryData) return;

    // Stats
    document.getElementById('total-seasons').textContent = summaryData.total_seasons;
    document.getElementById('first-year').textContent = summaryData.years[0];

    const currentChamp = summaryData.championship_history[summaryData.championship_history.length - 1];
    document.getElementById('current-champ').textContent = currentChamp.owner.split(' ')[0];

    // Most titles
    const titleCounts = {};
    summaryData.championship_history.forEach(c => {
        const name = c.owner.split(' ')[0];
        titleCounts[name] = (titleCounts[name] || 0) + 1;
    });
    const mostTitles = Object.entries(titleCounts).sort((a, b) => b[1] - a[1])[0];
    document.getElementById('most-titles').textContent = `${mostTitles[0]} (${mostTitles[1]})`;

    // Trophy case
    const trophyCase = document.getElementById('trophy-case');
    trophyCase.innerHTML = summaryData.championship_history.map(c => `
        <div class="trophy">
            <div class="trophy-year">${c.year}</div>
            <div class="trophy-icon">🏆</div>
            <div class="trophy-owner">${c.owner}</div>
        </div>
    `).join('');

    // Wins leaders
    const leaders = summaryData.all_time_records.slice(0, 5);
    document.getElementById('wins-leaders').innerHTML = leaders.map((l, i) => `
        <div class="leader-card">
            <div class="leader-rank">#${i + 1}</div>
            <div class="leader-info">
                <div class="leader-name">${l.owner}</div>
                <div class="leader-stats">${l.wins}W - ${l.losses}L (${l.win_pct}%)</div>
            </div>
        </div>
    `).join('');

    // Last updated
    if (summaryData.last_updated) {
        const date = new Date(summaryData.last_updated);
        document.getElementById('last-updated').textContent = date.toLocaleDateString();
    }
}

// Render Standings
function renderStandings() {
    if (!allSeasonsData) return;

    const select = document.getElementById('year-select');

    // Populate year selector if empty
    if (select.options.length === 0) {
        allSeasonsData.slice().reverse().forEach(season => {
            const option = document.createElement('option');
            option.value = season.year;
            option.textContent = season.year;
            select.appendChild(option);
        });

        select.addEventListener('change', () => renderStandingsTable(parseInt(select.value)));
    }

    renderStandingsTable(parseInt(select.value));
}

function renderStandingsTable(year) {
    const season = allSeasonsData.find(s => s.year === year);
    if (!season) return;

    const tbody = document.querySelector('#standings-table tbody');
    tbody.innerHTML = season.standings.map(team => `
        <tr class="${team.rank === 1 ? 'champion' : ''}">
            <td>${team.rank || '-'}</td>
            <td>${team.team_name}</td>
            <td>${team.owner}</td>
            <td>${team.record}</td>
            <td>${team.points_for.toLocaleString()}</td>
        </tr>
    `).join('');
}

// Render All-Time Records
function renderAllTime() {
    if (!summaryData) return;

    const tbody = document.querySelector('#all-time-table tbody');
    tbody.innerHTML = summaryData.all_time_records.map(owner => `
        <tr class="${owner.championships > 0 ? 'champion' : ''}">
            <td>${owner.owner}</td>
            <td>${owner.seasons}</td>
            <td>${owner.wins}</td>
            <td>${owner.losses}</td>
            <td>${owner.win_pct}%</td>
            <td>${owner.points_for.toLocaleString()}</td>
            <td>${owner.championships > 0 ? '🏆'.repeat(owner.championships) : '-'}</td>
            <td>${owner.best_finish === 99 ? '-' : ordinal(owner.best_finish)}</td>
        </tr>
    `).join('');
}

// Render Champions
function renderChampions() {
    if (!summaryData) return;

    const grid = document.getElementById('champions-grid');
    grid.innerHTML = summaryData.championship_history.slice().reverse().map(c => `
        <div class="champion-card">
            <div class="champion-year">${c.year}</div>
            <div class="champion-icon">🏆</div>
            <div class="champion-name">${c.owner}</div>
            <div class="champion-team">${c.team_name}</div>
            <div class="champion-record">Record: ${c.record} | PF: ${c.points_for.toLocaleString()}</div>
        </div>
    `).join('');
}

// Render Drafts
function renderDrafts() {
    if (!allSeasonsData) return;

    const select = document.getElementById('draft-year-select');

    // Populate year selector if empty
    if (select.options.length === 0) {
        allSeasonsData.slice().reverse().forEach(season => {
            if (season.draft && season.draft.length > 0) {
                const option = document.createElement('option');
                option.value = season.year;
                option.textContent = season.year;
                select.appendChild(option);
            }
        });

        select.addEventListener('change', () => renderDraftTable(parseInt(select.value)));
    }

    renderDraftTable(parseInt(select.value));
}

function renderDraftTable(year) {
    const season = allSeasonsData.find(s => s.year === year);
    if (!season || !season.draft) return;

    const tbody = document.querySelector('#draft-table tbody');
    tbody.innerHTML = season.draft.map(pick => `
        <tr>
            <td>${pick.overall}</td>
            <td>${pick.round}.${pick.pick}</td>
            <td>${pick.team}</td>
            <td>${pick.player}</td>
        </tr>
    `).join('');
}

// Helper: Ordinal numbers
function ordinal(n) {
    const s = ['th', 'st', 'nd', 'rd'];
    const v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
}
