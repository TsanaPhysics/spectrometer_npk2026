/**
 * NPK Spectrometer 2026 - Web Application & JSON Database Manager
 * AI4D AgriPhysics Research Unit, Rambhai Barni Rajabhat University
 * Author: Asst. Prof. Dr. Chewa Thassana & Research Team
 */

// State Management
const state = {
  ip: localStorage.getItem('wio_ip') || '192.168.1.100',
  isConnected: false,
  isMock: true,
  theme: localStorage.getItem('theme') || 'dark',
  pollInterval: null,
  activeTab: 'all',
  searchQuery: '',
  db: [],
  currentData: {
    type: 'SOIL_NPK',
    n: 45.2,
    p: 22.8,
    k: 128.5,
    refractive_n: 1.3425,
    density: 1.025,
    brix: 6.6,
    transmittance: 71.2,
    clarity: 'CLEAR',
    absorbance: [0.452, 0.312, 0.185, 0.110, 0.055],
    status: {
      battery: '4.12V',
      tcs34725: 'OK (Gain 60x)',
      sdcard: 'Mounted (FAT32)',
      currentPage: 5,
      rssi: -58
    }
  }
};

// Elements
const el = {
  ipInput: document.getElementById('device-ip-input'),
  btnConnect: document.getElementById('btn-connect'),
  statusDot: document.getElementById('connection-status-dot'),
  statusText: document.getElementById('connection-status-text'),
  themeToggle: document.getElementById('theme-toggle'),
  btnMockToggle: document.getElementById('btn-mock-toggle'),
  
  // Metrics
  valN: document.getElementById('val-n'),
  valP: document.getElementById('val-p'),
  valK: document.getElementById('val-k'),
  barN: document.getElementById('bar-n'),
  barP: document.getElementById('bar-p'),
  barK: document.getElementById('bar-k'),
  valSoilQuality: document.getElementById('val-soil-quality'),

  valRefractive: document.getElementById('val-refractive'),
  valDensity: document.getElementById('val-density'),
  valBrix: document.getElementById('val-brix'),
  valTransmittance: document.getElementById('val-transmittance'),
  valClarity: document.getElementById('val-clarity'),

  // Canvas
  spectrumCanvas: document.getElementById('spectrum-canvas'),

  // Remote controls
  btnScanSoil: document.getElementById('btn-scan-soil'),
  btnScanLiquid: document.getElementById('btn-scan-liquid'),
  btnSetBlank: document.getElementById('btn-set-blank'),
  btnCyclePage: document.getElementById('btn-cycle-page'),

  // DB Elements
  dbTableBody: document.getElementById('db-table-body'),
  recordCount: document.getElementById('record-count'),
  searchInput: document.getElementById('search-input'),
  btnExportJson: document.getElementById('btn-export-json'),
  btnImportJson: document.getElementById('btn-import-json'),
  jsonFileInput: document.getElementById('json-file-input'),
  btnExportCsv: document.getElementById('btn-export-csv'),
  btnClearDb: document.getElementById('btn-clear-db'),

  // Modal
  jsonModal: document.getElementById('json-modal'),
  jsonViewer: document.getElementById('json-viewer'),
  btnCloseModal: document.getElementById('btn-close-modal')
};

// Initial benchmark dataset
const defaultRecords = [
  {
    id: "REC-20260914-001",
    timestamp: "2026-09-14 14:15:30",
    type: "SOIL_NPK",
    mode: "TINYML_DL",
    sample_name: "สวนทุเรียนแปลง 1 (Durian Plot A)",
    n_mg_kg: 45.2,
    p_mg_kg: 22.8,
    k_mg_kg: 128.5,
    soil_quality: "Optimal (สมบูรณ์สูง)",
    absorbance: [0.452, 0.312, 0.185, 0.110, 0.055],
    operator: "ผศ.ดร.ชีวะ ทัศนา"
  },
  {
    id: "REC-20260914-002",
    timestamp: "2026-09-14 14:35:12",
    type: "SOIL_NPK",
    mode: "STANDARD_CURVE",
    sample_name: "แปลงทดลองฟิสิกส์เกษตร (Field B)",
    n_mg_kg: 24.1,
    p_mg_kg: 11.5,
    k_mg_kg: 68.0,
    soil_quality: "Medium (ปานกลาง)",
    absorbance: [0.241, 0.165, 0.098, 0.062, 0.032],
    operator: "นักวิจัย AI4D"
  },
  {
    id: "REC-20260914-003",
    timestamp: "2026-09-14 15:10:45",
    type: "LIQUID_OPTICS",
    sample_name: "น้ำหมักชีวภาพบำรุงรากทุเรียน (Bio-Fertilizer)",
    n_refractive: 1.3458,
    density_g_cm3: 1.032,
    brix_deg: 8.9,
    transmittance_pct: 65.4,
    clarity: "SLIGHTLY_TURBID",
    absorbance: [0.520, 0.380, 0.210, 0.145, 0.082],
    operator: "ผศ.ดร.ชีวะ ทัศนา"
  },
  {
    id: "REC-20260914-004",
    timestamp: "2026-09-14 16:02:20",
    type: "LIQUID_OPTICS",
    sample_name: "น้ำกลั่นบริสุทธิ์ (DI Water Blank)",
    n_refractive: 1.3330,
    density_g_cm3: 0.9982,
    brix_deg: 0.0,
    transmittance_pct: 99.8,
    clarity: "CLEAR",
    absorbance: [0.002, 0.001, 0.001, 0.001, 0.000],
    operator: "ผศ.ดร.ชีวะ ทัศนา"
  },
  {
    id: "REC-20260914-005",
    timestamp: "2026-09-14 16:45:00",
    type: "SOIL_NPK",
    mode: "POLYNOMIAL",
    sample_name: "ดินโคนต้นทุเรียนหมอนทอง แปลง C",
    n_mg_kg: 52.8,
    p_mg_kg: 28.4,
    k_mg_kg: 154.2,
    soil_quality: "High (อุดมสมบูรณ์มาก)",
    absorbance: [0.528, 0.365, 0.230, 0.138, 0.071],
    operator: "หน่วยวิจัย AI4D AgriPhysics"
  }
];

// Initialize JSON Database
function initDatabase() {
  const saved = localStorage.getItem('spectrometer_db');
  if (saved) {
    try {
      state.db = JSON.parse(saved);
    } catch (e) {
      console.error("Failed to parse local DB, resetting to defaults", e);
      state.db = [...defaultRecords];
      saveDatabase();
    }
  } else {
    state.db = [...defaultRecords];
    saveDatabase();
  }
}

function saveDatabase() {
  localStorage.setItem('spectrometer_db', JSON.stringify(state.db));
  renderTable();
}

// Render Database Table
function renderTable() {
  if (!el.dbTableBody) return;
  el.dbTableBody.innerHTML = '';

  const filtered = state.db.filter(item => {
    // Tab filter
    if (state.activeTab === 'soil' && item.type !== 'SOIL_NPK') return false;
    if (state.activeTab === 'liquid' && item.type !== 'LIQUID_OPTICS') return false;
    
    // Search query
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      const sample = (item.sample_name || '').toLowerCase();
      const id = (item.id || '').toLowerCase();
      const type = (item.type || '').toLowerCase();
      return sample.includes(q) || id.includes(q) || type.includes(q);
    }
    return true;
  });

  el.recordCount.textContent = `${filtered.length} รายการ (จากทั้งหมด ${state.db.length})`;

  if (filtered.length === 0) {
    el.dbTableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 32px;">
          ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา
        </td>
      </tr>
    `;
    return;
  }

  filtered.forEach(item => {
    const tr = document.createElement('tr');
    const isSoil = item.type === 'SOIL_NPK';
    const badge = isSoil
      ? `<span class="tag-soil">SOIL NPK</span>`
      : `<span class="tag-liquid">LIQUID</span>`;

    const summary = isSoil
      ? `N:${item.n_mg_kg} | P:${item.p_mg_kg} | K:${item.k_mg_kg} mg/kg`
      : `n:${item.n_refractive} | ${item.brix_deg}°Bx | ${item.clarity}`;

    tr.innerHTML = `
      <td style="font-family: var(--font-mono); font-size: 0.8rem;">${item.id}</td>
      <td style="font-size: 0.8rem; color: var(--text-muted);">${item.timestamp}</td>
      <td>${badge}</td>
      <td><strong>${item.sample_name || 'ตัวอย่างตรวจวัด'}</strong></td>
      <td style="font-family: var(--font-mono);">${summary}</td>
      <td><small style="color: var(--text-secondary);">${item.operator || 'ระบบอัตโนมัติ'}</small></td>
      <td style="text-align: right;">
        <button class="btn btn-secondary btn-view-json" data-id="${item.id}" style="padding: 4px 10px; font-size: 0.75rem;">
          { } JSON
        </button>
      </td>
    `;
    el.dbTableBody.appendChild(tr);
  });

  // Attach modal triggers
  document.querySelectorAll('.btn-view-json').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      const record = state.db.find(r => r.id === id);
      if (record) {
        showJsonModal(record);
      }
    });
  });
}

function showJsonModal(data) {
  el.jsonViewer.textContent = JSON.stringify(data, null, 2);
  el.jsonModal.classList.add('active');
}

function closeJsonModal() {
  el.jsonModal.classList.remove('active');
}

// Spectrum Canvas Rendering
function renderSpectrumChart(abs) {
  const canvas = el.spectrumCanvas;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, width, height);

  const padding = { top: 20, right: 30, bottom: 40, left: 45 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  // Wavelength points: 465, 500, 525, 590, 625 nm
  const wavelengths = [465, 500, 525, 590, 625];
  const colors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
  const minW = 450;
  const maxW = 650;
  const maxAbs = Math.max(0.6, ...abs) * 1.2;

  // Draw Grid & Axes
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.lineWidth = 1;
  ctx.fillStyle = '#6b7280';
  ctx.font = '10px Inter, sans-serif';

  // Y Grid
  for (let i = 0; i <= 4; i++) {
    const yVal = (maxAbs * (4 - i) / 4).toFixed(2);
    const yPos = padding.top + (plotH * i / 4);
    ctx.beginPath();
    ctx.moveTo(padding.left, yPos);
    ctx.lineTo(width - padding.right, yPos);
    ctx.stroke();
    ctx.fillText(yVal, padding.left - 30, yPos + 3);
  }

  // X Coordinates for points
  const points = wavelengths.map((w, idx) => {
    const x = padding.left + ((w - minW) / (maxW - minW)) * plotW;
    const y = padding.top + plotH - ((abs[idx] / maxAbs) * plotH);
    return { x, y, w, a: abs[idx], color: colors[idx] };
  });

  // Smooth Bézier Spectrum Line
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 0; i < points.length - 1; i++) {
    const xc = (points[i].x + points[i + 1].x) / 2;
    const yc = (points[i].y + points[i + 1].y) / 2;
    ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
  }
  ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);

  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 3;
  ctx.shadowColor = 'rgba(56, 189, 248, 0.4)';
  ctx.shadowBlur = 10;
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Gradient Fill under curve
  const fillGrad = ctx.createLinearGradient(0, padding.top, 0, padding.top + plotH);
  fillGrad.addColorStop(0, 'rgba(56, 189, 248, 0.25)');
  fillGrad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');
  ctx.lineTo(points[points.length - 1].x, padding.top + plotH);
  ctx.lineTo(points[0].x, padding.top + plotH);
  ctx.closePath();
  ctx.fillStyle = fillGrad;
  ctx.fill();

  // Draw Peak Points
  points.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 8;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Wavelength label
    ctx.fillStyle = '#9ca3af';
    ctx.fillText(`${p.w}nm`, p.x - 14, padding.top + plotH + 18);
    // Absorbance value label
    ctx.fillStyle = '#f9fafb';
    ctx.font = 'bold 10px monospace';
    ctx.fillText(p.a.toFixed(3), p.x - 12, p.y - 10);
    ctx.font = '10px Inter, sans-serif';
  });
}

// Update UI metrics
function updateMetrics(data) {
  if (data.n !== undefined) {
    el.valN.textContent = data.n.toFixed(1);
    el.valP.textContent = data.p.toFixed(1);
    el.valK.textContent = data.k.toFixed(1);
    el.barN.style.width = `${Math.min(100, (data.n / 60) * 100)}%`;
    el.barP.style.width = `${Math.min(100, (data.p / 40) * 100)}%`;
    el.barK.style.width = `${Math.min(100, (data.k / 200) * 100)}%`;

    const avg = (data.n / 50 + data.p / 30 + data.k / 150) / 3;
    if (avg > 0.8) {
      el.valSoilQuality.textContent = 'ดินอุดมสมบูรณ์สูง (High Quality)';
      el.valSoilQuality.style.color = 'var(--accent-green)';
    } else if (avg > 0.4) {
      el.valSoilQuality.textContent = 'ดินความสมบูรณ์ปานกลาง (Medium)';
      el.valSoilQuality.style.color = 'var(--accent-yellow)';
    } else {
      el.valSoilQuality.textContent = 'ดินขาดธาตุอาหาร (Low / Deficient)';
      el.valSoilQuality.style.color = 'var(--accent-red)';
    }
  }

  if (data.refractive_n !== undefined) {
    el.valRefractive.textContent = data.refractive_n.toFixed(4);
    el.valDensity.textContent = data.density.toFixed(3);
    el.valBrix.textContent = data.brix.toFixed(1);
    el.valTransmittance.textContent = `${data.transmittance.toFixed(1)}%`;
    el.valClarity.textContent = data.clarity;
  }

  if (data.absorbance && data.absorbance.length === 5) {
    renderSpectrumChart(data.absorbance);
  }
}

// Wi-Fi Connection & REST API Sync
async function connectToDevice(ip) {
  el.statusDot.className = 'status-dot';
  el.statusText.textContent = 'กำลังเชื่อมต่อ...';

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2500);

    const res = await fetch(`http://${ip}/api/latest`, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      state.isConnected = true;
      state.isMock = false;
      el.statusDot.className = 'status-dot online';
      el.statusText.textContent = `เชื่อมต่อ Wio Terminal (${ip})`;
      updateMetrics(data);
      addRecordFromDevice(data);
      startPolling(ip);
      return;
    }
  } catch (err) {
    console.warn("Wio Terminal not reachable over Wi-Fi, activating Mock/Demo Mode:", err);
  }

  // Fallback to Mock/Demo Mode
  state.isConnected = false;
  state.isMock = true;
  el.statusDot.className = 'status-dot mock';
  el.statusText.textContent = 'Mock Mode (โหมดจำลองออฟไลน์)';
  updateMetrics(state.currentData);
}

function startPolling(ip) {
  if (state.pollInterval) clearInterval(state.pollInterval);
  state.pollInterval = setInterval(async () => {
    if (!state.isConnected) return;
    try {
      const res = await fetch(`http://${ip}/api/latest`);
      if (res.ok) {
        const data = await res.json();
        updateMetrics(data);
      }
    } catch (e) {
      console.warn("Lost connection to Wio Terminal");
      state.isConnected = false;
      el.statusDot.className = 'status-dot offline';
      el.statusText.textContent = 'การเชื่อมต่อหลุด';
    }
  }, 4000);
}

function addRecordFromDevice(data) {
  const newRec = {
    id: `REC-${Date.now().toString().slice(-6)}`,
    timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
    type: data.type || 'SOIL_NPK',
    sample_name: data.sample_name || (data.type === 'SOIL_NPK' ? 'ตัวอย่างดินภาคสนาม' : 'ตัวอย่างของเหลว'),
    n_mg_kg: data.n,
    p_mg_kg: data.p,
    k_mg_kg: data.k,
    n_refractive: data.refractive_n,
    density_g_cm3: data.density,
    brix_deg: data.brix,
    transmittance_pct: data.transmittance,
    clarity: data.clarity,
    absorbance: data.absorbance,
    operator: 'Wi-Fi Auto-Sync'
  };

  state.db.unshift(newRec);
  saveDatabase();
}

// Remote Trigger Action
async function triggerDeviceAction(endpoint, payload) {
  if (state.isMock) {
    // Generate realistic simulated scan
    if (endpoint === 'scan-soil') {
      const n = (30 + Math.random() * 30).toFixed(1);
      const p = (15 + Math.random() * 20).toFixed(1);
      const k = (90 + Math.random() * 60).toFixed(1);
      const abs = [
        parseFloat((0.35 + Math.random() * 0.2).toFixed(3)),
        parseFloat((0.25 + Math.random() * 0.15).toFixed(3)),
        parseFloat((0.15 + Math.random() * 0.1).toFixed(3)),
        parseFloat((0.08 + Math.random() * 0.05).toFixed(3)),
        parseFloat((0.04 + Math.random() * 0.03).toFixed(3))
      ];

      const simulated = {
        id: `REC-${Date.now().toString().slice(-6)}`,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        type: 'SOIL_NPK',
        mode: 'TINYML_DL',
        sample_name: `ตัวอย่างดินแปลงทดสอบ #${Math.floor(Math.random() * 100)}`,
        n_mg_kg: parseFloat(n),
        p_mg_kg: parseFloat(p),
        k_mg_kg: parseFloat(k),
        soil_quality: 'Optimal (สมบูรณ์)',
        absorbance: abs,
        operator: 'ผู้ควบคุมผ่าน Web'
      };

      state.currentData = { ...state.currentData, ...simulated, n: parseFloat(n), p: parseFloat(p), k: parseFloat(k) };
      state.db.unshift(simulated);
      saveDatabase();
      updateMetrics(state.currentData);
      alert('สแกนตัวอย่างดินสำเร็จ (บันทึกข้อมูลลงฐานข้อมูล JSON เรียบร้อยแล้ว)');
    } else if (endpoint === 'scan-liquid') {
      const brix = parseFloat((4.0 + Math.random() * 12.0).toFixed(1));
      const n = parseFloat((1.3330 + 0.00143 * brix).toFixed(4));
      const rho = parseFloat((0.9982 + 0.00385 * brix).toFixed(3));
      const trans = parseFloat((95 - brix * 2.5).toFixed(1));
      const abs = [
        parseFloat((0.2 + brix * 0.03).toFixed(3)),
        parseFloat((0.15 + brix * 0.02).toFixed(3)),
        parseFloat((0.09 + brix * 0.015).toFixed(3)),
        parseFloat((0.05 + brix * 0.01).toFixed(3)),
        parseFloat((0.02 + brix * 0.005).toFixed(3))
      ];

      const simulated = {
        id: `REC-${Date.now().toString().slice(-6)}`,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        type: 'LIQUID_OPTICS',
        sample_name: `ตัวอย่างสารละลายการเกษตร #${Math.floor(Math.random() * 50)}`,
        n_refractive: n,
        density_g_cm3: rho,
        brix_deg: brix,
        transmittance_pct: trans,
        clarity: brix > 10 ? 'TURBID' : 'CLEAR',
        absorbance: abs,
        operator: 'ผู้ควบคุมผ่าน Web'
      };

      state.currentData = { ...state.currentData, ...simulated, refractive_n: n, density: rho, brix: brix, transmittance: trans, clarity: simulated.clarity };
      state.db.unshift(simulated);
      saveDatabase();
      updateMetrics(state.currentData);
      alert('สแกนสมบัติของเหลวสำเร็จ (บันทึกค่าลงฐานข้อมูล JSON เรียบร้อยแล้ว)');
    } else if (endpoint === 'calibrate') {
      alert('ตั้งค่า Blank Reference เรียบร้อยแล้ว (Offset = 0.000)');
    }
    return;
  }

  // Real HTTP POST to Wio Terminal
  try {
    const res = await fetch(`http://${state.ip}/api/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload || {})
    });
    const result = await res.json();
    alert(`ส่งคำสั่งสำเร็จ: ${result.message || 'OK'}`);
  } catch (err) {
    alert(`เกิดข้อผิดพลาดในการส่งคำสั่ง: ${err.message}`);
  }
}

// Export JSON
function exportJson() {
  const blob = new Blob([JSON.stringify(state.db, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `spectrometer_database_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// Import JSON
function importJson(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const imported = JSON.parse(e.target.result);
      if (Array.isArray(imported)) {
        state.db = imported;
        saveDatabase();
        alert(`นำเข้าฐานข้อมูล JSON สำเร็จ! โหลดข้อมูลทั้งหมด ${imported.length} รายการ`);
      } else {
        alert('โครงสร้างไฟล์ไม่ถูกต้อง ต้องเป็น JSON Array');
      }
    } catch (err) {
      alert(`ไม่สามารถอ่านไฟล์ JSON ได้: ${err.message}`);
    }
  };
  reader.readAsText(file);
}

// Export CSV
function exportCsv() {
  if (state.db.length === 0) {
    alert('ไม่มีข้อมูลในฐานข้อมูล');
    return;
  }

  const headers = ['ID', 'Timestamp', 'Type', 'Sample', 'N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'Refractive_n', 'Density_g_cm3', 'Brix_deg', 'Clarity', 'Operator'];
  const rows = state.db.map(r => [
    r.id,
    r.timestamp,
    r.type,
    `"${r.sample_name || ''}"`,
    r.n_mg_kg || '',
    r.p_mg_kg || '',
    r.k_mg_kg || '',
    r.n_refractive || '',
    r.density_g_cm3 || '',
    r.brix_deg || '',
    r.clarity || '',
    `"${r.operator || ''}"`
  ]);

  const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `spectrometer_data_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// Clear Database
function clearDatabase() {
  if (confirm('คุณต้องการล้างฐานข้อมูลทั้งหมด หรือรีเซ็ตกลับเป็นค่าเริ่มต้น?')) {
    state.db = [...defaultRecords];
    saveDatabase();
    alert('รีเซ็ตฐานข้อมูลเป็นค่ามาตรฐานเสร็จสิ้น');
  }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  initDatabase();
  el.ipInput.value = state.ip;

  // Theme
  document.documentElement.setAttribute('data-theme', state.theme);
  el.themeToggle.addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    el.themeToggle.textContent = state.theme === 'dark' ? '🌙' : '☀️';
    renderSpectrumChart(state.currentData.absorbance);
  });
  el.themeToggle.textContent = state.theme === 'dark' ? '🌙' : '☀️';

  // Connect Button
  el.btnConnect.addEventListener('click', () => {
    const ip = el.ipInput.value.trim();
    if (ip) {
      state.ip = ip;
      localStorage.setItem('wio_ip', ip);
      connectToDevice(ip);
    }
  });

  // Mock Toggle
  el.btnMockToggle.addEventListener('click', () => {
    state.isMock = !state.isMock;
    if (state.isMock) {
      el.statusDot.className = 'status-dot mock';
      el.statusText.textContent = 'Mock Mode (โหมดจำลอง)';
      el.btnMockToggle.textContent = 'สลับเป็น Live Wi-Fi';
    } else {
      el.btnMockToggle.textContent = 'สลับเป็น Mock Demo';
      connectToDevice(state.ip);
    }
  });

  // Remote Actions
  el.btnScanSoil.addEventListener('click', () => triggerDeviceAction('scan-soil'));
  el.btnScanLiquid.addEventListener('click', () => triggerDeviceAction('scan-liquid'));
  el.btnSetBlank.addEventListener('click', () => triggerDeviceAction('calibrate'));
  el.btnCyclePage.addEventListener('click', () => triggerDeviceAction('cycle-page'));

  // Database Tab Filtering
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeTab = btn.getAttribute('data-tab');
      renderTable();
    });
  });

  // Search input
  el.searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    renderTable();
  });

  // Export / Import
  el.btnExportJson.addEventListener('click', exportJson);
  el.btnExportCsv.addEventListener('click', exportCsv);
  el.btnClearDb.addEventListener('click', clearDatabase);
  el.btnImportJson.addEventListener('click', () => el.jsonFileInput.click());
  el.jsonFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      importJson(e.target.files[0]);
    }
  });

  // Modal
  el.btnCloseModal.addEventListener('click', closeJsonModal);
  el.jsonModal.addEventListener('click', (e) => {
    if (e.target === el.jsonModal) closeJsonModal();
  });

  // Initial Connect / Load
  connectToDevice(state.ip);
});
