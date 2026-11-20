// Shared navigation and native bridge helpers

function navigateTo(page) {
    window.location.href = 'file:///android_asset/' + page;
}

function getQueryParam(name) {
    var params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function getBackendUrl() {
    if (window.VoclNative) return window.VoclNative.getBackendUrl();
    return 'http://localhost:8080';
}

function startSession(problemId) {
    if (window.VoclNative) {
        window.VoclNative.startSession(problemId);
    } else {
        console.warn('VoclNative bridge not available');
    }
}

function stopSession() {
    if (window.VoclNative) {
        window.VoclNative.stopSession();
    } else {
        console.warn('VoclNative bridge not available');
    }
}

function renderBottomNav(activeTab) {
    var tabs = [
        { id: 'drills',  label: 'Drills',  page: 'drills.html',  icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6.75A2.75 2.75 0 016.75 4h10.5A2.75 2.75 0 0120 6.75v10.5A2.75 2.75 0 0117.25 20H6.75A2.75 2.75 0 014 17.25V6.75z" stroke-linecap="round" stroke-linejoin="round"></path><path d="M8 10l3 2.5-3 2.5m5 0h3" stroke-linecap="round" stroke-linejoin="round"></path></svg>' },
        { id: 'grades',  label: 'Grades',  page: 'grades.html',  icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" stroke-linecap="round" stroke-linejoin="round"></path></svg>' },
        { id: 'profile', label: 'Profile', page: 'profile.html', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" stroke-linecap="round" stroke-linejoin="round"></path></svg>' }
    ];

    var html = '<nav style="position:fixed;bottom:0;width:100%;z-index:50;background:rgba(0,0,0,0.85);backdrop-filter:blur(40px);-webkit-backdrop-filter:blur(40px);border-top:1px solid rgba(255,255,255,0.08)">';
    html += '<div style="height:56px;display:flex;align-items:center;justify-content:space-around;max-width:480px;margin:0 auto;padding:0 16px">';
    tabs.forEach(function(tab) {
        var isActive = (tab.id === activeTab);
        var color = isActive ? '#ffffff' : '#8e8e93';
        html += '<a onclick="navigateTo(\'' + tab.page + '\')" style="flex:1;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:' + color + ';cursor:pointer;position:relative;-webkit-tap-highlight-color:transparent">';
        html += '<div style="position:relative;display:flex;align-items:center;justify-content:center">' + tab.icon;
        if (isActive) html += '<span style="position:absolute;bottom:-4px;width:4px;height:4px;border-radius:50%;background:#30d158"></span>';
        html += '</div>';
        html += '<span style="font-size:10px;font-weight:' + (isActive ? '600' : '500') + ';letter-spacing:-0.02em">' + tab.label + '</span>';
        html += '</a>';
    });
    html += '</div></nav>';
    document.write(html);
}
