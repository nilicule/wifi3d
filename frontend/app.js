// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  ssid: '',
  password: '',
  auth_type: 'WPA',
  hidden: false,
  qr_size_mm: 60,
  base_color_hex: '#ffffff',
  module_color_hex: '#1a1a1a',
  header_text: '',
  sub_label: '',
  wifi_icon: true,
  desk_stand_tab: false,
};

// ── Theme ─────────────────────────────────────────────────────────────────────
const html = document.documentElement;
const savedTheme = localStorage.getItem('wifi3d-theme');
if (savedTheme === 'light') html.classList.remove('dark');

document.getElementById('theme-toggle')?.addEventListener('click', () => {
  const dark = html.classList.toggle('dark');
  localStorage.setItem('wifi3d-theme', dark ? 'dark' : 'light');
  updateThreeBackground();
});

// ── Color swatches ────────────────────────────────────────────────────────────
const PALETTE = ['#ffffff', '#9ca3af', '#fbbf24', '#ef4444', '#f97316', '#3b82f6', '#22c55e', '#1a1a1a'];
const BASE_COLORS = PALETTE;
const MOD_COLORS  = PALETTE;

function makeSwatch(color, swatchContainer, stateKey) {
  const btn = document.createElement('button');
  btn.style.background = color;
  btn.className = 'w-7 h-7 rounded-md border-2 transition-all';
  const selected = state[stateKey] === color;
  btn.style.borderColor = selected ? '#10b981' : 'rgba(156,163,175,0.5)';
  btn.onclick = () => {
    state[stateKey] = color;
    updateColorPreview();
    swatchContainer.querySelectorAll('button').forEach(b => {
      b.style.borderColor = 'rgba(156,163,175,0.5)';
    });
    btn.style.borderColor = '#10b981';
    schedulePreview();
  };
  swatchContainer.appendChild(btn);
}

function updateColorPreview() {
  document.getElementById('color-preview').style.background = state.base_color_hex;
  document.getElementById('color-preview-dot').style.background = state.module_color_hex;
}

const baseContainer = document.getElementById('base-swatches');
const modContainer  = document.getElementById('mod-swatches');
BASE_COLORS.forEach(c => makeSwatch(c, baseContainer, 'base_color_hex'));
MOD_COLORS.forEach(c  => makeSwatch(c, modContainer,  'module_color_hex'));
updateColorPreview();

// ── Accordion ─────────────────────────────────────────────────────────────────
document.querySelectorAll('.accordion-btn').forEach(btn => {
  const targetId = btn.dataset.target;
  const body = document.getElementById(targetId);
  const chevron = btn.querySelector('.accordion-chevron');

  // Only step1 starts open; Styling (step2) starts collapsed
  if (targetId === 'step1-body') {
    body.classList.add('open');
    chevron.style.transform = 'rotate(180deg)';
  }

  btn.addEventListener('click', () => {
    const open = body.classList.toggle('open');
    chevron.style.transform = open ? 'rotate(180deg)' : 'rotate(0deg)';
  });
});

// ── Form bindings ─────────────────────────────────────────────────────────────
function bind(id, stateKey, transform = v => v) {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', () => {
    state[stateKey] = transform(el.value);
    schedulePreview();
    updateExportButtons();
  });
}

bind('ssid', 'ssid');
bind('password', 'password');
bind('header-text', 'header_text', v => v.toUpperCase().replace(/[^A-Z0-9 ]/g, ''));
bind('sub-label', 'sub_label',    v => v.toUpperCase().replace(/[^A-Z0-9 ]/g, ''));

document.getElementById('open-network').addEventListener('change', e => {
  const open = e.target.checked;
  document.getElementById('password-row').style.display = open ? 'none' : '';
  state.auth_type = open ? 'nopass' : 'WPA';
  if (open) state.password = '';
  schedulePreview();
  updateExportButtons();
});

document.getElementById('hidden-network').addEventListener('change', e => {
  state.hidden = e.target.checked;
  schedulePreview();
});

document.getElementById('wifi-icon').addEventListener('change', e => {
  state.wifi_icon = e.target.checked;
  schedulePreview();
});

document.getElementById('desk-stand').addEventListener('change', e => {
  state.desk_stand_tab = e.target.checked;
  schedulePreview();
});

// Password show/hide
document.getElementById('pw-toggle').addEventListener('click', () => {
  const pw = document.getElementById('password');
  pw.type = pw.type === 'password' ? 'text' : 'password';
});

// Password strength meter
function calcPasswordStrength(v) {
  if (!v) return 0;
  let score = 0;
  if (v.length >= 8)  score++;                              // meets WPA minimum
  if (v.length >= 14) score++;                              // good length
  if (/[A-Z]/.test(v) && /[a-z]/.test(v)) score++;         // mixed case
  if (/[0-9]/.test(v)) score++;                             // has digits
  if (/[^A-Za-z0-9]/.test(v)) score++;                     // has symbols
  return Math.min(4, score);
}

document.getElementById('password').addEventListener('input', e => {
  const strength = calcPasswordStrength(e.target.value);
  const colors  = ['', '#ef4444', '#f59e0b', '#84cc16', '#10b981'];
  const labels  = ['', 'Weak', 'Fair', 'Good', 'Strong'];
  for (let i = 1; i <= 4; i++) {
    document.getElementById(`str-${i}`).style.background =
      i <= strength ? colors[strength] : '#374151';
  }
  const lbl = document.getElementById('str-label');
  lbl.textContent = e.target.value ? labels[strength] : '';
  lbl.style.color = colors[strength] || '';
});

// Size presets
function activateSizeBtn(active) {
  document.querySelectorAll('.size-btn').forEach(b => {
    const on = b === active;
    b.classList.toggle('border-accent', on);
    b.classList.toggle('bg-accent/10', on);
    b.classList.toggle('text-accent', on);
    b.classList.toggle('border-gray-700', !on);
  });
}

function setCustomVisible(show) {
  const row = document.getElementById('custom-size-row');
  row.classList.toggle('hidden', !show);
  row.classList.toggle('flex', show);
  const customBtn = document.getElementById('btn-custom-size');
  customBtn.classList.toggle('border-accent', show);
  customBtn.classList.toggle('bg-accent/10', show);
  customBtn.classList.toggle('text-accent', show);
  customBtn.classList.toggle('border-gray-700', !show);
}

document.querySelectorAll('.size-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    setCustomVisible(false);
    activateSizeBtn(btn);
    state.qr_size_mm = parseInt(btn.dataset.size, 10);
    schedulePreview();
  });
});

document.getElementById('btn-custom-size').addEventListener('click', () => {
  setCustomVisible(true);
  activateSizeBtn(null);
  document.getElementById('custom-size').focus();
});

document.getElementById('custom-size').addEventListener('input', e => {
  const v = parseInt(e.target.value, 10);
  if (v >= 50 && v <= 150) {
    state.qr_size_mm = v;
    schedulePreview();
  }
});

// ── Export buttons ────────────────────────────────────────────────────────────
function updateExportButtons() {
  const valid = state.ssid.trim().length > 0 &&
    (state.auth_type === 'nopass' || state.password.length > 0);
  ['btn-stl', 'btn-3mf'].forEach(id => {
    const btn = document.getElementById(id);
    btn.disabled = !valid;
    if (valid) {
      btn.classList.remove('opacity-40', 'cursor-not-allowed');
    } else {
      btn.classList.add('opacity-40', 'cursor-not-allowed');
    }
  });
}

async function doExport(format) {
  const res = await fetch('api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...state, format }),
  });
  if (!res.ok) return;
  const blob = await res.blob();
  const slug = state.ssid.replace(/[^a-zA-Z0-9]/g, '-').slice(0, 20);
  const ext = format === 'stl' ? 'zip' : format;
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `wifi3d-${slug}.${ext}`;
  a.click();
  URL.revokeObjectURL(a.href);
}

document.getElementById('btn-stl').addEventListener('click', () => doExport('stl'));
document.getElementById('btn-3mf').addEventListener('click', () => doExport('3mf'));

document.getElementById('btn-reset').addEventListener('click', () => {
  ['ssid', 'password', 'header-text', 'sub-label', 'custom-size'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  Object.assign(state, {
    ssid: '', password: '', auth_type: 'WPA', hidden: false,
    qr_size_mm: 60, base_color_hex: '#ffffff', module_color_hex: '#1a1a1a',
    header_text: '', sub_label: '', wifi_icon: true, desk_stand_tab: false,
  });
  setCustomVisible(false);
  activateSizeBtn(document.querySelector('.size-btn[data-size="60"]'));
  clearPreview();
  updateExportButtons();
});

// Initialise button state
updateExportButtons();

// ── Preview API calls ─────────────────────────────────────────────────────────
let debounceTimer = null;
const emptyState = document.getElementById('empty-state');

function schedulePreview() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(fetchPreview, 300);
}

async function fetchPreview() {
  if (!state.ssid.trim()) {
    clearPreview();
    return;
  }
  if (emptyState) emptyState.style.display = 'none';
  try {
    const res = await fetch('api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state),
    });
    if (!res.ok) return;
    const data = await res.json();
    renderPreview(data);
  } catch (e) {
    console.warn('Preview fetch failed:', e);
  }
}

// ── Three.js (dynamic import — CDN failure cannot break the form above) ────────
let _THREE = null;
let _scene = null;
let _camera = null;
let _controls = null;
let _previewGroup = null;
let _pendingData = null;

function updateThreeBackground() {
  if (!_scene || !_THREE) return;
  const dark = html.classList.contains('dark');
  _scene.background = new _THREE.Color(dark ? 0x111827 : 0xf9fafb);
}

function clearPreview() {
  if (_previewGroup && _scene) {
    _scene.remove(_previewGroup);
    _previewGroup.traverse(obj => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
    _previewGroup = null;
  }
  if (emptyState) emptyState.style.display = '';
}

function renderPreview(data) {
  if (!_THREE || !_scene) {
    _pendingData = data;
    return;
  }
  _pendingData = null;

  if (_previewGroup) {
    _scene.remove(_previewGroup);
    _previewGroup.traverse(obj => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) obj.material.dispose();
    });
  }
  _previewGroup = new _THREE.Group();

  const plateMat = new _THREE.MeshStandardMaterial({
    color: new _THREE.Color(data.plate_color),
    roughness: 0.6,
    metalness: 0.05,
  });
  const modMat = new _THREE.MeshStandardMaterial({
    color: new _THREE.Color(data.module_color),
    roughness: 0.5,
    metalness: 0.05,
  });

  function buildGeo(vertices, faces) {
    const geo = new _THREE.BufferGeometry();
    geo.setAttribute('position', new _THREE.Float32BufferAttribute(vertices, 3));
    geo.setIndex(faces);
    geo.computeVertexNormals();
    return geo;
  }

  if (data.plate_vertices.length > 0) {
    _previewGroup.add(new _THREE.Mesh(buildGeo(data.plate_vertices, data.plate_faces), plateMat));
  }
  if (data.module_vertices.length > 0) {
    _previewGroup.add(new _THREE.Mesh(buildGeo(data.module_vertices, data.module_faces), modMat));
  }

  // Geometry uses Z-up; rotate so the plate lies flat on the grid (Y-up world)
  _previewGroup.rotation.x = -Math.PI / 2;

  // Centre in XZ and sit the bottom face on y=0
  const box = new _THREE.Box3().setFromObject(_previewGroup);
  const center = box.getCenter(new _THREE.Vector3());
  _previewGroup.position.set(-center.x, -box.min.y, -center.z);
  _scene.add(_previewGroup);

  const size = box.getSize(new _THREE.Vector3()).length();
  const dist = size * 1.2;
  _camera.position.set(dist * 0.6, dist * 0.55, dist * 0.8);
  _controls.target.set(0, 0, 0);
  _controls.update();
}

async function initThree() {
  const container = document.getElementById('canvas-container');

  const THREE = await import('three');
  const { OrbitControls } = await import('three/addons/controls/OrbitControls.js');
  _THREE = THREE;

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  _scene = new THREE.Scene();
  updateThreeBackground();

  _camera = new THREE.PerspectiveCamera(45, 1, 0.1, 2000);
  _camera.position.set(60, 55, 80);

  _controls = new OrbitControls(_camera, renderer.domElement);
  _controls.enableDamping = true;
  _controls.dampingFactor = 0.08;
  _controls.enablePan = true;
  _controls.enableZoom = true;

  // Three-point lighting
  _scene.add(new THREE.AmbientLight(0xffffff, 0.4));
  const key = new THREE.DirectionalLight(0xffffff, 1.2);
  key.position.set(60, 80, 100);
  _scene.add(key);
  const fill = new THREE.DirectionalLight(0x8ecae6, 0.5);
  fill.position.set(-60, -40, 60);
  _scene.add(fill);

  // Grid floor
  const dark = html.classList.contains('dark');
  const gridColor = dark ? 0x1f2937 : 0xe5e7eb;
  const grid = new THREE.GridHelper(200, 20, gridColor, gridColor);
  _scene.add(grid);

  // Responsive canvas — min 400px height guard
  function resize() {
    const w = container.clientWidth;
    const h = Math.max(container.clientHeight, 400);
    renderer.setSize(w, h);
    _camera.aspect = w / h;
    _camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container);
  resize();

  // Animation loop
  (function animate() {
    requestAnimationFrame(animate);
    _controls.update();
    renderer.render(_scene, _camera);
  })();

  // Fade drag hint on first interaction
  _controls.addEventListener('start', () => {
    const hint = document.getElementById('drag-hint');
    if (hint) hint.style.opacity = '0';
  });

  if (_pendingData) {
    renderPreview(_pendingData);
  }
}

initThree().catch(e => {
  console.warn('3D preview unavailable:', e);
  if (emptyState) {
    emptyState.innerHTML =
      '<p class="text-gray-500 text-sm">3D preview unavailable<br>' +
      '<span class="text-xs opacity-60">Export still works</span></p>';
    emptyState.style.display = '';
  }
});
