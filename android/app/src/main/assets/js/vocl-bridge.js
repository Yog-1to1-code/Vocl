// Shared navigation, fallback catalog, and native bridge helpers

var VOCL_FALLBACK_PROBLEMS = [
    {
        id: 'longest-palindrome',
        title: 'Longest palindromic substring',
        category: 'DSA',
        difficulty: 'Medium',
        duration_min: 10,
        statement: 'Given a string s, return its longest palindromic substring. Explain your approach out loud before optimizing it.',
        constraints: ['1 <= len(s) <= 10^5', 's consists of ASCII letters and digits only'],
        optimal_complexity: 'O(N) time · O(1) space',
        key_edge_cases: ['Single character string', 'Empty string', 'All identical characters', 'Even-length palindromes'],
        example_input: '"babad"',
        example_output: '"bab"  (or "aba")',
        tagline: 'Find the pattern. Defend the trade-offs.'
    },
    {
        id: 'url-shortener',
        title: 'Design a global URL shortener',
        category: 'System Design',
        difficulty: 'Medium',
        duration_min: 15,
        statement: 'Design a scalable URL shortening service like bit.ly. Discuss storage, hashing strategy, read/write ratio, collisions, and analytics.',
        constraints: ['100M new URLs per month', 'Read-to-write ratio ~100:1', 'Redirection latency < 50 ms p99'],
        optimal_complexity: 'O(1) read / O(1) write',
        key_edge_cases: ['Hash collision resolution', '301 vs 302 redirect caching', 'Hot-key thundering herd on viral links'],
        example_input: 'https://vocl.dev/drills/42',
        example_output: 'https://vcl.io/aB9x2K',
        tagline: 'Scale the reads. Guard the hot keys.'
    },
    {
        id: 'postgres-cpu-spike',
        title: 'Postgres at 99% CPU',
        category: 'DevOps',
        difficulty: 'Hard',
        duration_min: 10,
        statement: 'Your PostgreSQL 15 primary is pinned at 100% CPU on a 4-vCPU Cloud SQL instance and p99 latency jumped from 12 ms to 3.2 s. Walk through your diagnostic runbook and mitigations.',
        constraints: ['DB size ~200 GB, ~50 tables', 'PgBouncer max 100 connections', 'Autovacuum enabled with defaults'],
        optimal_complexity: 'pg_stat_activity -> EXPLAIN -> fix',
        key_edge_cases: ['Lock contention vs CPU-bound queries', 'Bloated tables forcing seq scans', 'Autovacuum blocked by long transactions'],
        example_input: 'CPU 100% · p99 3,200 ms',
        example_output: 'Identify top query -> mitigate -> index',
        tagline: 'Triage fast. Stabilize without guesswork.'
    }
];

function navigateTo(page) {
    window.location.href = 'file:///android_asset/' + page;
}

function getQueryParam(name) {
    var params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function getBackendUrl() {
    if (window.VoclNative && typeof window.VoclNative.getBackendUrl === 'function') {
        return window.VoclNative.getBackendUrl();
    }
    return 'http://10.0.2.2:8080';
}

function startSession(problemId) {
    if (window.VoclNative && typeof window.VoclNative.startSession === 'function') {
        window.VoclNative.startSession(problemId);
    } else {
        console.warn('VoclNative bridge not available');
    }
}

function stopSession() {
    if (window.VoclNative && typeof window.VoclNative.stopSession === 'function') {
        window.VoclNative.stopSession();
    } else {
        console.warn('VoclNative bridge not available');
    }
}

function setMicMuted(muted) {
    if (window.VoclNative && typeof window.VoclNative.setMuted === 'function') {
        window.VoclNative.setMuted(Boolean(muted));
    }
}

function showToast(message) {
    var existing = document.getElementById('vocl-toast');
    if (!existing) {
        existing = document.createElement('div');
        existing.id = 'vocl-toast';
        existing.className = 'vocl-toast';
        document.body.appendChild(existing);
    }
    existing.textContent = message;
    existing.classList.add('show');
    clearTimeout(window._voclToastTimer);
    window._voclToastTimer = setTimeout(function() {
        existing.classList.remove('show');
    }, 2400);
}

function computeStreakDays(sessions) {
    if (!Array.isArray(sessions) || sessions.length === 0) return 0;
    var days = {};
    sessions.forEach(function(s) {
        var d = s && s.timestamp_utc ? new Date(s.timestamp_utc) : new Date();
        if (!isNaN(d.getTime())) {
            days[d.toDateString()] = true;
        }
    });
    return Math.max(1, Object.keys(days).length);
}

function getFallbackProblemById(id) {
    for (var i = 0; i < VOCL_FALLBACK_PROBLEMS.length; i++) {
        if (VOCL_FALLBACK_PROBLEMS[i].id === id) return VOCL_FALLBACK_PROBLEMS[i];
    }
    return VOCL_FALLBACK_PROBLEMS[0];
}

function escapeHtml(value) {
    return String(value == null ? '' : value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function saveSessionLocally(autopsy) {
    if (!autopsy) return;
    try {
        localStorage.setItem('lastAutopsy', JSON.stringify(autopsy));
        var history = JSON.parse(localStorage.getItem('voclSessions') || '[]');
        var exists = autopsy.session_id && history.some(function(item) {
            return item && item.session_id === autopsy.session_id;
        });
        if (!exists) {
            history.push(autopsy);
            localStorage.setItem('voclSessions', JSON.stringify(history));
        }
    } catch (e) {
        console.warn('localStorage write failed', e);
    }
}

function setOfflineBadge(isOffline) {
    var existing = document.getElementById('vocl-offline-badge');
    if (!isOffline) {
        if (existing) existing.remove();
        return;
    }
    if (existing) return;
    var badge = document.createElement('div');
    badge.id = 'vocl-offline-badge';
    badge.textContent = 'OFFLINE FALLBACK';
    badge.style.cssText = 'position:fixed;top:10px;right:12px;z-index:99;padding:3px 8px;border-radius:999px;background:rgba(240,82,72,0.16);border:1px solid rgba(240,82,72,0.45);color:#F05248;font-size:10px;font-weight:700;letter-spacing:0.06em;pointer-events:none;';
    document.body.appendChild(badge);
}

function renderBottomNav(activeTab) {
    var tabs = [
        {
            id: 'drills',
            label: 'Drills',
            page: 'drills.html',
            icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"></rect><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"></rect><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"></rect><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"></rect></svg>'
        },
        {
            id: 'grades',
            label: 'Grades',
            page: 'grades.html',
            icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="20" x2="6" y2="14"></line><line x1="12" y1="20" x2="12" y2="6"></line><line x1="18" y1="20" x2="18" y2="10"></line></svg>'
        },
        {
            id: 'profile',
            label: 'Profile',
            page: 'profile.html',
            icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"></circle><path d="M4.5 20.5c1.2-3.6 4.1-5.5 7.5-5.5s6.3 1.9 7.5 5.5"></path></svg>'
        }
    ];

    var html = '<nav class="vocl-bottom-nav"><div class="vocl-bottom-nav-inner">';

    tabs.forEach(function(tab) {
        var cls = 'vocl-nav-tab' + (tab.id === activeTab ? ' active' : '');
        html += '<a class="' + cls + '" onclick="navigateTo(\'' + tab.page + '\')">';
        html += tab.icon;
        html += '<span>' + tab.label + '</span>';
        html += '</a>';
    });

    html += '</div></nav>';
    document.write(html);
}
