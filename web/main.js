// Update clock with precise timing
function updateClock() {
    const now = new Date();
    const time = now.getHours().toString().padStart(2, '0') + ":" +
        now.getMinutes().toString().padStart(2, '0') + ":" +
        now.getSeconds().toString().padStart(2, '0');
    document.getElementById('clock').innerText = time;
}
setInterval(updateClock, 1000);

// Exposure functions for Eel
eel.expose(updateStatus);
function updateStatus(text) {
    const el = document.getElementById('status-display');
    if (el) el.innerText = text.toUpperCase();
}

eel.expose(addLog);
function addLog(text) {
    const logs = document.getElementById('log-list');
    if (!logs) return;
    const entry = document.createElement('p');
    entry.className = 'log-entry';
    entry.innerText = `[${new Date().toLocaleTimeString()}] > ${text}`;
    logs.prepend(entry);
    if (logs.children.length > 12) logs.removeChild(logs.lastChild);
}

eel.expose(updateVitals);
function updateVitals(cpu, ram, bat) {
    document.getElementById('cpu-bar').style.width = cpu + "%";
    document.getElementById('cpu-val').innerText = cpu + "%";
    document.getElementById('ram-bar').style.width = ram + "%";
    document.getElementById('ram-val').innerText = ram + "%";
    document.getElementById('bat-bar').style.width = bat + "%";
    document.getElementById('bat-val').innerText = bat + "%";
}

eel.expose(addTerminalLine);
function addTerminalLine(text) {
    const term = document.getElementById('terminal-output');
    if (!term) return;
    const line = document.createElement('p');
    line.className = 'term-line';
    line.innerText = text;
    term.appendChild(line);
    term.scrollTop = term.scrollHeight;
    if (term.children.length > 20) term.removeChild(term.firstChild);
}

eel.expose(setOrbActive);
function setOrbActive(isActive) {
    const orb = document.getElementById('jarvis-orb');
    const mic = document.getElementById('mic-indicator');
    const visualizer = document.getElementById('visualizer');

    if (isActive) {
        orb.classList.add('active');
        mic.classList.add('listening');
        visualizer.classList.add('listening');
    } else {
        orb.classList.remove('active');
        mic.classList.remove('listening');
        visualizer.classList.remove('listening');
    }
}

eel.expose(setLastCommand);
function setLastCommand(text) {
    const cmdText = document.getElementById('last-command-text');
    if (cmdText) cmdText.innerText = text.toUpperCase();
    document.getElementById('main-container').classList.add('hud-flicker');
    setTimeout(() => document.getElementById('main-container').classList.remove('hud-flicker'), 400);
}

eel.expose(showNotification);
function showNotification(message, type = 'default') {
    const area = document.getElementById('notification-area');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    let icon = '📡';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '⚠️';
    toast.innerHTML = `<span>${icon}</span> ${message}`;
    area.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => area.removeChild(toast), 500);
    }, 4500);
}

eel.expose(setOrbState);
function setOrbState(state) {
    const orb = document.getElementById('jarvis-orb');
    if (!orb) return;
    orb.classList.remove('processing', 'success', 'error');
    if (state !== 'default') orb.classList.add(state);
}

// --- High-Performance Face Scan Stream ---
eel.expose(toggleSecurityScan);
function toggleSecurityScan(show) {
    const orb = document.getElementById('jarvis-orb');
    const overlay = document.getElementById('security-overlay');

    if (show) {
        orb.classList.add('hidden');
        setTimeout(() => {
            overlay.classList.remove('hidden');
        }, 600);
    } else {
        overlay.classList.add('hidden');
        setTimeout(() => {
            orb.classList.remove('hidden');
        }, 600);
    }
}

eel.expose(updateScanView);
function updateScanView(base64Frame) {
    const canvas = document.getElementById('scan-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.onload = function () {
        ctx.save();
        // Create circular clip path
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2, 0, Math.PI * 2);
        ctx.clip();

        const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
        const x = (canvas.width / 2) - (img.width / 2) * scale;
        const y = (canvas.height / 2) - (img.height / 2) * scale;
        ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
        ctx.restore();
    };
    img.src = "data:image/jpeg;base64," + base64Frame;
}

eel.expose(setScanStatus);
function setScanStatus(text) {
    const el = document.getElementById('scan-status-text');
    if (el) el.innerText = text.toUpperCase();
}

// Global UI Hover Interaction
document.addEventListener('mousemove', (e) => {
    const orb = document.querySelector('.orb-container');
    const scanner = document.querySelector('.security-screen');
    const xAxis = (window.innerWidth / 2 - e.pageX) / 40;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 40;

    if (orb && !orb.classList.contains('hidden')) {
        orb.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    }
    if (scanner && !scanner.classList.contains('hidden')) {
        scanner.style.transform = `rotateY(${xAxis / 2}deg) rotateX(${yAxis / 2}deg)`;
    }
});

console.log("JARVIS NEURAL INTERFACE v3.0 ACTIVE");

eel.expose(updateAudioIntensity);
function updateAudioIntensity(intensity) {
    const orbInner = document.querySelector('.orb-inner');
    const orbMiddle = document.querySelector('.orb-middle');
    if (orbInner) {
        const scale = 1 + (intensity / 100) * 0.8;
        orbInner.style.transform = `scale(${scale})`;
        orbInner.style.boxShadow = `0 0 ${60 + intensity}px var(--primary), 0 0 ${120 + intensity}px var(--secondary)`;
    }
    if (orbMiddle) {
        const scale = 1 + (intensity / 100) * 0.2;
        orbMiddle.style.transform = `scale(${scale})`;
    }
}

eel.expose(setStealthMode);
function setStealthMode(isActive) {
    const body = document.body;
    const container = document.getElementById('main-container');
    if (isActive) {
        body.classList.add('stealth-active');
        container.style.filter = 'brightness(0.2) blur(10px) grayscale(1)';
        showNotification("STEALTH MODE ACTIVATED - PRESENCE LOSS", "alert");
    } else {
        body.classList.remove('stealth-active');
        container.style.filter = '';
        showNotification("IDENTITY RE-ESTABLISHED - DEPLOYING HUD", "success");
    }
}

eel.expose(updateCameraFeed);
function updateCameraFeed(base64Frame) {
    const stream = document.getElementById('camera-stream');
    if (stream) {
        stream.src = "data:image/jpeg;base64," + base64Frame;
    }
}

eel.expose(updateGesture);
function updateGesture(label) {
    const glabel = document.getElementById('gesture-label');
    if (glabel) {
        glabel.innerText = label || "NO GESTURE DETECTED";
    }
}

eel.expose(updateTacticalData);
function updateTacticalData(x, y, label) {
    const crosshair = document.querySelector('.tactical-crosshair');
    const tag = document.getElementById('sentinel-tag');
    if (crosshair) {
        // Map normalized 0-1 coords to percentage
        crosshair.style.left = `${x * 100}%`;
        crosshair.style.top = `${y * 100}%`;
        crosshair.style.opacity = '1';
    }
    if (tag && label) {
        tag.innerText = `SENTINEL MODE // TRACKING: ${label.toUpperCase()}`;
    }
}

eel.expose(setRedAlert);
function setRedAlert(isActive) {
    const body = document.body;
    const tag = document.getElementById('sentinel-tag');
    if (isActive) {
        body.classList.add('red-alert');
        if (tag) tag.innerText = "SENTINEL MODE // RED ALERT ACTIVE";
        showNotification("SECURITY PROTOCOL ENFORCED - RED ALERT", "alert");
    } else {
        body.classList.remove('red-alert');
        if (tag) tag.innerText = "SENTINEL MODE // STANDBY";
        showNotification("SECURITY THREAT NEUTRALIZED - STANDBY", "success");
    }
}
