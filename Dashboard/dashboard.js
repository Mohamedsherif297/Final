/* ============================================================
   Surveillance Car Dashboard — JavaScript
   Protocol:
     Receive  → binary[0]=0x00 JSON msg | 0x01 video JPEG | 0x02 audio
     Send     → JSON { topic, payload }
   ============================================================ */

'use strict';

// ── State ────────────────────────────────────────────────────
const state = {
  ws: null,
  mqtt: null,
  connected: false,
  mqttConnected: false,
  arrowMode: 'motor',   // 'motor' | 'servo'
  speed: 70,
  pan: 90,              // Center position (0-180 range)
  tilt: 90,             // Center position (0-180 range)
  keysDown: new Set(),
  servoStep: 5,         // degrees per arrow press
  uptimeStart: null,
  frameCount: 0,
  fpsTimer: null,
};

// ── DOM refs ──────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const canvas       = $('videoCanvas');
const ctx          = canvas.getContext('2d');
const videoOverlay = $('videoOverlay');
const statusPill   = $('connectionPill');
const statusDot    = $('statusDot');
const statusText   = $('statusText');
const fpsBadge     = $('fpsBadge');
const uptimeBadge  = $('uptimeBadge');
const connectBtn   = $('connectBtn');
const piIpInput    = $('piIpInput');
const eventLog     = $('eventLog');

// ── Logging ──────────────────────────────────────────────────
function log(msg, type = 'info') {
  const ts = new Date().toLocaleTimeString('en-GB', { hour12: false });
  const el = document.createElement('div');
  el.className = `log-entry log-${type}`;
  el.textContent = `[${ts}] ${msg}`;
  eventLog.appendChild(el);
  eventLog.scrollTop = eventLog.scrollHeight;
  // Trim to 200 entries
  while (eventLog.children.length > 200) eventLog.removeChild(eventLog.firstChild);
}

$('clearLogBtn').onclick = () => { eventLog.innerHTML = ''; };

// ── WebSocket connection ──────────────────────────────────────
function connect() {
  const ip = piIpInput.value.trim();
  if (!ip) { log('Enter the Pi IP address (or Ngrok URL) first.', 'warn'); return; }

  // 1. Connect MQTT to HiveMQ Cloud for commands
  if (!state.mqttConnected) {
    connectMqtt();
  }

  // 2. Connect WebSocket for video streaming
  let url;
  if (ip.startsWith('ws://') || ip.startsWith('wss://')) {
    // Already has protocol
    url = ip;
  } else if (ip.includes('trycloudflare.com') || ip.includes('ngrok.io') || ip.includes(':')) {
    // Cloudflare/Ngrok URL or already has port - don't add port
    url = `ws://${ip}`;
  } else {
    // Local IP - add port
    url = `ws://${ip}:8765`;
  }
  log(`Connecting to WebSocket ${url}…`);
  setStatus('connecting');

  state.ws = new WebSocket(url);
  state.ws.binaryType = 'arraybuffer';

  state.ws.onopen = () => {
    state.connected = true;
    setStatus('connected');
    connectBtn.textContent = 'Disconnect';
    log(`Connected to ${url}`, 'ok');
    state.uptimeStart = Date.now();
    startFpsCounter();
    startUptimeTick();
  };

  state.ws.onclose = () => {
    state.connected = false;
    setStatus('disconnected');
    connectBtn.textContent = 'Connect';
    videoOverlay.classList.remove('hidden');
    log('Connection closed.', 'warn');
    stopFpsCounter();
    stopUptimeTick();
  };

  state.ws.onerror = () => {
    setStatus('error');
    log('WebSocket error — check IP and that the Pi is running.', 'error');
  };

  state.ws.onmessage = onMessage;
}

function disconnect() {
  if (state.ws) { state.ws.close(); state.ws = null; }
}

connectBtn.onclick = () => {
  if (state.connected) disconnect();
  else connect();
};

// ── Status helpers ────────────────────────────────────────────
function setStatus(s) {
  statusPill.className = 'status-pill';
  if (s === 'connected')    { statusPill.classList.add('connected'); statusText.textContent = 'Connected'; }
  else if (s === 'error')   { statusPill.classList.add('error');     statusText.textContent = 'Error'; }
  else if (s === 'connecting') { statusText.textContent = 'Connecting…'; }
  else                      { statusText.textContent = 'Disconnected'; }
}

// ── Message handler ───────────────────────────────────────────
function onMessage(ev) {
  const data = ev.data;

  if (data instanceof ArrayBuffer) {
    const view = new Uint8Array(data);
    const tag  = view[0];

    if (tag === 0x01) {
      // Video JPEG frame
      console.log(`[Video] Received frame: ${view.length} bytes`);
      const blob = new Blob([view.slice(1)], { type: 'image/jpeg' });
      const url  = URL.createObjectURL(blob);
      const img  = new Image();
      img.onload = () => {
        canvas.width  = img.naturalWidth  || 640;
        canvas.height = img.naturalHeight || 480;
        ctx.drawImage(img, 0, 0);
        URL.revokeObjectURL(url);
        videoOverlay.classList.add('hidden');
        state.frameCount++;
      };
      img.onerror = () => {
        console.error('[Video] Failed to load image');
      };
      img.src = url;
    }
    // 0x02 audio — skip for now (no speaker UI)

    if (tag === 0x00) {
      // JSON message wrapped as binary
      try {
        const text = new TextDecoder().decode(view.slice(1));
        handleJson(JSON.parse(text));
      } catch (_) {}
    }
    return;
  }

  // Plain text (shouldn't happen but handle anyway)
  try { handleJson(JSON.parse(data)); } catch (_) {}
}

// ── JSON event handler ────────────────────────────────────────
function handleJson(msg) {
  if (msg.event === 'connected') {
    log(`Server: ${msg.server || 'surveillance-car'}`, 'ok');
    return;
  }

  if (msg.event === 'mqtt' && msg.topic && msg.payload) {
    const topic   = msg.topic;
    let   payload;
    try { payload = JSON.parse(msg.payload); } catch (_) { payload = msg.payload; }

    if (topic === 'sensors/ultrasonic') {
      updateDistance(payload.distance);
    } else if (topic === 'sensors/obstacle') {
      handleObstacle(payload.distance);
    } else if (topic === 'emergency/alert') {
      handleEmergency(payload);
    } else if (topic === 'dev/status') {
      updateStatusBadges(payload);
    }
  }
}

// ── MQTT connection (Cloud WAN) ───────────────────────────────
const MQTT_CONFIG = {
  host: '78ed3eab06c348d0948ef7681cf4a377.s1.eu.hivemq.cloud',
  port: 8884, // WebSockets over TLS port for HiveMQ Cloud
  useTLS: true,
  username: 'mohamed',
  password: 'P@ssw0rd',
  clientId: 'dashboard-' + Math.random().toString(16).substr(2, 8)
};

function connectMqtt() {
  log(`Connecting to HiveMQ Cloud...`);
  
  // Initialize Paho MQTT client
  state.mqtt = new Paho.MQTT.Client(MQTT_CONFIG.host, Number(MQTT_CONFIG.port), "/mqtt", MQTT_CONFIG.clientId);

  state.mqtt.onConnectionLost = (responseObject) => {
    state.mqttConnected = false;
    if (responseObject.errorCode !== 0) {
      log(`MQTT Connection lost: ${responseObject.errorMessage}`, 'warn');
    }
  };

  state.mqtt.onMessageArrived = (message) => {
    // Route MQTT messages into our existing JSON handler
    handleJson({ 
      event: 'mqtt', 
      topic: message.destinationName, 
      payload: message.payloadString 
    });
  };

  const options = {
    useSSL: MQTT_CONFIG.useTLS,
    userName: MQTT_CONFIG.username,
    password: MQTT_CONFIG.password,
    timeout: 3,
    onSuccess: () => {
      state.mqttConnected = true;
      log('Connected to HiveMQ Cloud (Commands Active)', 'ok');
      state.mqtt.subscribe('dev/status');
      state.mqtt.subscribe('sensors/#');
      state.mqtt.subscribe('emergency/alert');
    },
    onFailure: (message) => {
      state.mqttConnected = false;
      log(`MQTT Connection failed: ${message.errorMessage}`, 'error');
    }
  };

  state.mqtt.connect(options);
}

// ── Send command ──────────────────────────────────────────────
function send(topic, payload) {
  const payloadStr = JSON.stringify(payload);

  if (state.mqttConnected && state.mqtt) {
    // Primary: Send via HiveMQ Cloud MQTT (WAN)
    const message = new Paho.MQTT.Message(payloadStr);
    message.destinationName = topic;
    state.mqtt.send(message);
  } else if (state.connected && state.ws) {
    // Fallback: Send via WebSocket (Local LAN)
    state.ws.send(JSON.stringify({ topic, payload: payloadStr }));
  } else {
    log('Not connected to MQTT or WebSocket — command dropped.', 'warn');
  }
}

// ── FPS counter ───────────────────────────────────────────────
function startFpsCounter() {
  state.frameCount = 0;
  state.fpsTimer = setInterval(() => {
    fpsBadge.textContent = `${state.frameCount} FPS`;
    state.frameCount = 0;
  }, 1000);
}
function stopFpsCounter() {
  clearInterval(state.fpsTimer);
  fpsBadge.textContent = '-- FPS';
}

// ── Uptime ticker ─────────────────────────────────────────────
let _uptimeTick = null;
function startUptimeTick() {
  _uptimeTick = setInterval(() => {
    if (!state.uptimeStart) return;
    const s = Math.floor((Date.now() - state.uptimeStart) / 1000);
    const h = String(Math.floor(s / 3600)).padStart(2, '0');
    const m = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const sec = String(s % 60).padStart(2, '0');
    uptimeBadge.textContent = `Uptime: ${h}:${m}:${sec}`;
  }, 1000);
}
function stopUptimeTick() {
  clearInterval(_uptimeTick);
  uptimeBadge.textContent = 'Uptime: --';
}

// ══════════════════════════════════════════════════════════════
// MOTOR CONTROL
// ══════════════════════════════════════════════════════════════
const MOTOR_DIRS = { up: 'forward', down: 'backward', left: 'left', right: 'right' };

function sendMotor(direction) {
  send('dev/motor', { direction, speed: state.speed });
  log(`Motor → ${direction} @ ${state.speed}%`, 'cmd');
  $('motorBadge').textContent = direction;
}

function stopMotor() {
  send('dev/motor', { direction: 'stop' });
  $('motorBadge').textContent = 'stop';
}

// ── Speed slider ──────────────────────────────────────────────
const speedSlider = $('speedSlider');
speedSlider.oninput = () => {
  state.speed = +speedSlider.value;
  $('speedVal').textContent = `${state.speed}%`;
};

// ══════════════════════════════════════════════════════════════
// SERVO CONTROL
// ══════════════════════════════════════════════════════════════
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

function sendServo(pan, tilt) {
  // Map 0-180 range (standard servo range)
  state.pan  = clamp(pan,  0, 180);
  state.tilt = clamp(tilt, 0, 180);
  send('dev/servo', { action: 'set_angle', pan: state.pan, tilt: state.tilt });
  syncServoUI();
}

function nudgeServo(dPan, dTilt) {
  sendServo(state.pan + dPan, state.tilt + dTilt);
  log(`Servo → pan ${state.pan}° tilt ${state.tilt}°`, 'cmd');
}

function syncServoUI() {
  $('panSlider').value   = state.pan;
  $('tiltSlider').value  = state.tilt;
  $('panVal').textContent  = `${state.pan}°`;
  $('tiltVal').textContent = `${state.tilt}°`;
  $('panLabel').textContent  = `Pan: ${state.pan}°`;
  $('tiltLabel').textContent = `Tilt: ${state.tilt}°`;
  $('servoPanBadge').textContent  = `${state.pan}°`;
  $('servoTiltBadge').textContent = `${state.tilt}°`;
  updateCrosshair();
}

function updateCrosshair() {
  // Map 0…180 → 5%…95% of the circle
  const x = (state.pan / 180) * 90 + 5;
  const y = (state.tilt / 180) * 90 + 5;
  const dot = $('crosshairDot');
  dot.style.left = `${x}%`;
  dot.style.top  = `${y}%`;
}

// Servo sliders (manual drag)
$('panSlider').oninput = () => {
  state.pan = +$('panSlider').value;
  sendServo(state.pan, state.tilt);
};
$('tiltSlider').oninput = () => {
  state.tilt = +$('tiltSlider').value;
  sendServo(state.pan, state.tilt);
};

// Center servo
$('centerServoBtn').onclick = () => {
  sendServo(90, 90);
  log('Servo → centered', 'cmd');
};

// ── Mode toggle ───────────────────────────────────────────────
$('modeMotor').onclick = () => setArrowMode('motor');
$('modeServo').onclick = () => setArrowMode('servo');

function setArrowMode(mode) {
  state.arrowMode = mode;
  $('modeMotor').classList.toggle('active', mode === 'motor');
  $('modeServo').classList.toggle('active', mode === 'servo');
  $('modeHint').innerHTML = '<kbd>W A S D</kbd> Motor &nbsp;|&nbsp; <kbd>↑ ↓ ← →</kbd> Servo &nbsp;|&nbsp; <kbd>Q/E</kbd> Speed';

  if (mode === 'motor') {
    $('btnUp').innerHTML = '<span style="font-size: 1.2rem; font-weight: bold;">W</span>';
    $('btnDown').innerHTML = '<span style="font-size: 1.2rem; font-weight: bold;">S</span>';
    $('btnLeft').innerHTML = '<span style="font-size: 1.2rem; font-weight: bold;">A</span>';
    $('btnRight').innerHTML = '<span style="font-size: 1.2rem; font-weight: bold;">D</span>';
  } else {
    $('btnUp').innerHTML = '<span style="font-size: 1.5rem; font-weight: bold;">↑</span>';
    $('btnDown').innerHTML = '<span style="font-size: 1.5rem; font-weight: bold;">↓</span>';
    $('btnLeft').innerHTML = '<span style="font-size: 1.5rem; font-weight: bold;">←</span>';
    $('btnRight').innerHTML = '<span style="font-size: 1.5rem; font-weight: bold;">→</span>';
  }
}

// ══════════════════════════════════════════════════════════════
// KEYBOARD INPUT  (Explicit WASD for motor, Arrows for servo)
// ══════════════════════════════════════════════════════════════
// KEYBOARD INPUT  (Explicit WASD for motor, Arrows for servo)
// ══════════════════════════════════════════════════════════════
document.addEventListener('keydown', e => {
  // Don't hijack input fields
  if (e.target.tagName === 'INPUT') return;

  const key = e.key;
  let dir = null;

  // 1. WASD Controls -> Motor (ignore repeats for motors)
  if (['w', 'W'].includes(key)) { dir = 'up'; }
  else if (['s', 'S'].includes(key)) { dir = 'down'; }
  else if (['a', 'A'].includes(key)) { dir = 'left'; }
  else if (['d', 'D'].includes(key)) { dir = 'right'; }

  if (dir) {
    if (e.repeat) return; // Ignore repeats for motors
    state.keysDown.add(key);
    sendMotor(MOTOR_DIRS[dir]);
    // Only light up the UI if the Motor tab is selected
    if (state.arrowMode === 'motor') highlightDpad(dir, true);
    return;
  }

  // 2. Arrow Controls -> Servo (allow repeats for continuous movement)
  if (key === 'ArrowUp') { dir = 'up'; }
  else if (key === 'ArrowDown') { dir = 'down'; }
  else if (key === 'ArrowLeft') { dir = 'left'; }
  else if (key === 'ArrowRight') { dir = 'right'; }

  if (dir) {
    e.preventDefault(); // Prevent page scroll
    state.keysDown.add(key);
    const steps = { up: [0, -state.servoStep], down: [0, state.servoStep], left: [-state.servoStep, 0], right: [state.servoStep, 0] };
    nudgeServo(...steps[dir]);
    // Only light up the UI if the Servo tab is selected
    if (state.arrowMode === 'servo') highlightDpad(dir, true);
    return;
  }

  // 3. Speed Controls (Q to decrease, E to increase)
  if (e.repeat) return; // Ignore repeats for speed controls
  if (['e', 'E'].includes(key)) {
    const newSpeed = Math.min(100, state.speed + 5);
    $('speedSlider').value = newSpeed;
    speedSlider.oninput(); // trigger the visual update
  } else if (['q', 'Q'].includes(key)) {
    const newSpeed = Math.max(0, state.speed - 5);
    $('speedSlider').value = newSpeed;
    speedSlider.oninput(); // trigger the visual update
  }
});

document.addEventListener('keyup', e => {
  if (e.target.tagName === 'INPUT') return;
  
  const key = e.key;
  let dir = null;

  // WASD Released
  if (['w', 'W'].includes(key)) { dir = 'up'; }
  else if (['s', 'S'].includes(key)) { dir = 'down'; }
  else if (['a', 'A'].includes(key)) { dir = 'left'; }
  else if (['d', 'D'].includes(key)) { dir = 'right'; }

  if (dir) {
    state.keysDown.delete(key);
    stopMotor();
    if (state.arrowMode === 'motor') highlightDpad(dir, false);
    return;
  }

  // Arrows Released
  if (key === 'ArrowUp') { dir = 'up'; }
  else if (key === 'ArrowDown') { dir = 'down'; }
  else if (key === 'ArrowLeft') { dir = 'left'; }
  else if (key === 'ArrowRight') { dir = 'right'; }

  if (dir) {
    state.keysDown.delete(key);
    if (state.arrowMode === 'servo') highlightDpad(dir, false);
    return;
  }
});

function highlightDpad(dir, on) {
  const map = { up: 'btnUp', down: 'btnDown', left: 'btnLeft', right: 'btnRight' };
  const el = $(map[dir]);
  if (el) el.classList.toggle('pressed', on);
}

// ── D-pad click (pointer events, works for touch too) ─────────
['btnUp','btnDown','btnLeft','btnRight'].forEach(id => {
  const btn = $(id);
  const dir = btn.dataset.dir;

  btn.addEventListener('pointerdown', e => {
    e.preventDefault();
    btn.setPointerCapture(e.pointerId);
    if (state.arrowMode === 'motor') {
      sendMotor(MOTOR_DIRS[dir]);
    } else {
      const steps = { up:[0,-state.servoStep], down:[0,state.servoStep], left:[-state.servoStep,0], right:[state.servoStep,0] };
      nudgeServo(...steps[dir]);
    }
  });

  btn.addEventListener('pointerup', () => {
    if (state.arrowMode === 'motor') stopMotor();
  });
});

$('btnStop').onclick = () => {
  stopMotor();
  log('Stop', 'cmd');
};

// ══════════════════════════════════════════════════════════════
// LED CONTROL
// ══════════════════════════════════════════════════════════════
document.querySelectorAll('.led-preset').forEach(btn => {
  btn.onclick = () => {
    const color = btn.dataset.color;
    send('dev/led', { action: 'set_color', color });
    log(`LED → ${color}`, 'cmd');
    updateLedPreview(btn.style.getPropertyValue('--c'));
  };
});

document.querySelectorAll('.effect-btn').forEach(btn => {
  if (btn.id === 'stopEffectBtn') return;
  btn.onclick = () => {
    const effect = btn.dataset.effect;
    send('dev/led', { action: 'start_effect', effect });
    log(`LED effect → ${effect}`, 'cmd');
  };
});

$('stopEffectBtn').onclick = () => {
  send('dev/led', { action: 'stop_effect' });
  log('LED effect → stopped', 'cmd');
};

$('setRgbBtn').onclick = () => {
  const r = +$('rSlider').value;
  const g = +$('gSlider').value;
  const b = +$('bSlider').value;
  send('dev/led', { action: 'set_rgb', red: r, green: g, blue: b });
  log(`LED RGB → rgb(${r},${g},${b})`, 'cmd');
  updateLedPreview(`rgb(${r},${g},${b})`);
};

function updateLedPreview(color) {
  const p = $('ledPreview');
  p.style.background = color;
  p.style.boxShadow  = `0 0 12px ${color}`;
}

// ══════════════════════════════════════════════════════════════
// EMERGENCY
// ══════════════════════════════════════════════════════════════
$('emergencyBtn').onclick = () => {
  send('dev/commands', { command: 'emergency_stop' });
  log('⚠ EMERGENCY STOP sent!', 'error');
  $('emergencyBtn').classList.add('active');
  $('emergencyBadge').textContent = 'ACTIVE';
  $('emergencyBadge').className = 'status-badge badge-danger';
};

$('resetEmergencyBtn').onclick = () => {
  send('dev/commands', { command: 'reset_emergency' });
  log('Emergency reset sent', 'ok');
  $('emergencyBtn').classList.remove('active');
  $('emergencyBadge').textContent = 'OK';
  $('emergencyBadge').className = 'status-badge badge-ok';
};

function handleEmergency(payload) {
  log(`⚠ Emergency: ${payload.trigger} — ${payload.message}`, 'error');
  $('emergencyBtn').classList.add('active');
  $('emergencyBadge').textContent = payload.trigger || 'ACTIVE';
  $('emergencyBadge').className = 'status-badge badge-danger';
}

// ══════════════════════════════════════════════════════════════
// SENSORS
// ══════════════════════════════════════════════════════════════
const GAUGE_ARC_LEN = 173; // full semicircle stroke-dasharray

function updateDistance(dist) {
  if (dist == null) return;
  const cm = Math.round(dist);
  $('distanceVal').textContent = cm;

  // Gauge: 0 = empty (far), full = close (danger)
  // Map 0-200 cm → full…empty
  const pct    = Math.min(1, Math.max(0, 1 - cm / 200));
  const offset = GAUGE_ARC_LEN * (1 - pct);
  const fill   = $('gaugeFill');
  fill.style.strokeDashoffset = offset;

  // Color coding
  if (cm < 15)       { fill.style.stroke = '#f87171'; }
  else if (cm < 30)  { fill.style.stroke = '#fb923c'; }
  else if (cm < 60)  { fill.style.stroke = '#facc15'; }
  else               { fill.style.stroke = '#4ade80'; }
}

function handleObstacle(dist) {
  const badge = $('obstacleBadge');
  badge.textContent = `${Math.round(dist)}cm`;
  badge.className = 'status-badge badge-danger';
  $('sensor-card')?.classList.add('obstacle-active');
  log(`⚠ Obstacle at ${Math.round(dist)} cm!`, 'warn');

  clearTimeout(handleObstacle._timer);
  handleObstacle._timer = setTimeout(() => {
    badge.textContent = 'Clear';
    badge.className = 'status-badge badge-ok';
  }, 3000);
}

function updateStatusBadges(payload) {
  if (!payload) return;
  if (payload.type === 'motor_moved' && payload.message?.direction) {
    $('motorBadge').textContent = payload.message.direction;
  }
  if (payload.type === 'servo_moved') {
    // Will be updated by syncServoUI when we send commands
  }
  if (payload.type === 'emergency_reset') {
    $('emergencyBadge').textContent = 'OK';
    $('emergencyBadge').className = 'status-badge badge-ok';
    $('emergencyBtn').classList.remove('active');
  }
  if (payload.type === 'hardware_status' && payload.message) {
    const hw = payload.message;
    if (hw.motor?.direction)   $('motorBadge').textContent = hw.motor.direction;
    if (hw.servo?.pan != null) {
      state.pan  = hw.servo.pan;
      state.tilt = hw.servo.tilt ?? state.tilt;
      syncServoUI();
    }
    if (hw.emergency?.active != null) {
      const active = hw.emergency.active;
      $('emergencyBadge').textContent = active ? 'ACTIVE' : 'OK';
      $('emergencyBadge').className = `status-badge ${active ? 'badge-danger' : 'badge-ok'}`;
      $('emergencyBtn').classList.toggle('active', active);
    }
  }
}

// ── Initial UI sync ───────────────────────────────────────────
syncServoUI();
updateDistance(null);
setArrowMode('motor');
