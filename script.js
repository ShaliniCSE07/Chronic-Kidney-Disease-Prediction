/* ==========================================================================
   CKD Stage Prediction System - Multi-Page Application Logic
   Shared across index.html, predict.html, and results.html
   ========================================================================== */

// Clinical Explanations for all 7 CKD Stages
const STAGE_EXPLANATIONS = {
  "No CKD": "Normal kidney function. eGFR ≥ 90 mL/min/1.73m² with no persistent markers of kidney damage. Recommendations: Maintain a healthy lifestyle, stay hydrated, and monitor blood pressure periodically.",
  "Stage 1 (Kidney Damage)": "Kidney damage present with normal or high kidney function (eGFR ≥ 90 mL/min/1.73m²). Protein/albumin in urine may be present. Recommendations: Manage blood pressure and blood glucose tightly to prevent progression.",
  "Stage 2 (Mildly Decreased)": "Mild reduction in kidney function (eGFR 60-89 mL/min/1.73m²). Recommendations: Schedule regular kidney health checkups, monitor proteinuria (ACR), and control cardiovascular risk factors.",
  "Stage 3a (Mild-Moderate)": "Mild-to-moderate reduction in kidney function (eGFR 45-59 mL/min/1.73m²). Recommendations: Consult a nephrologist, review medications to avoid nephrotoxic drugs (like NSAIDs), and manage dietary sodium/protein.",
  "Stage 3b (Moderate-Severe)": "Moderate-to-severe reduction in kidney function (eGFR 30-44 mL/min/1.73m²). Recommendations: Active nephrology care, monitor for CKD complications like anemia and mineral bone disorder.",
  "Stage 4 (Severely Decreased)": "Severe reduction in kidney function (eGFR 15-29 mL/min/1.73m²). Recommendations: Urgent nephrologist care, prepare for kidney replacement therapy options (dialysis or kidney transplantation).",
  "Stage 5 (Kidney Failure)": "End-Stage Renal Disease / Kidney failure (eGFR < 15 mL/min/1.73m²). Recommendations: Immediate clinical intervention required. Renal replacement therapy (dialysis or transplant) is necessary to sustain life."
};

// Map Stage Names to Gauge Index (1-7) & Badge CSS Class
const STAGE_MAP = {
  "No CKD": { index: 1, class: "badge-no-ckd" },
  "Stage 1 (Kidney Damage)": { index: 2, class: "badge-stage-1" },
  "Stage 2 (Mildly Decreased)": { index: 3, class: "badge-stage-2" },
  "Stage 3a (Mild-Moderate)": { index: 4, class: "badge-stage-3a" },
  "Stage 3b (Moderate-Severe)": { index: 5, class: "badge-stage-3b" },
  "Stage 4 (Severely Decreased)": { index: 6, class: "badge-stage-4" },
  "Stage 5 (Kidney Failure)": { index: 7, class: "badge-stage-5" }
};

// Preset Data Collections for Instant Testing
const PRESETS = {
  no_ckd: {
    age: 35, gender: "Female", ethnicity: "Non-Hispanic White", education_level: "4",
    poverty_income_ratio: 3.5, bmi: 22.5, weight_kg: 62.0, height_cm: 166.0,
    bp_systolic: 118, bp_diastolic: 75, blood_urea_nitrogen: 12.0, albumin_serum: 4.5,
    phosphorus: 3.2, bicarbonate: 26.0, calcium: 9.6, uric_acid: 4.5,
    urine_creatinine: 130.0, urine_albumin: 6.0, albumin_creatinine_ratio: 4.6,
    diabetes_diagnosed: "2.0", insulin_use: "2.0", diabetes_pills: "2.0",
    ever_smoked: "2.0", current_smoker: "3.0"
  },
  stage2: {
    age: 58, gender: "Male", ethnicity: "Non-Hispanic Black", education_level: "3",
    poverty_income_ratio: 2.1, bmi: 27.5, weight_kg: 82.0, height_cm: 172.0,
    bp_systolic: 132, bp_diastolic: 84, blood_urea_nitrogen: 18.0, albumin_serum: 4.2,
    phosphorus: 3.6, bicarbonate: 24.5, calcium: 9.3, uric_acid: 5.9,
    urine_creatinine: 110.0, urine_albumin: 18.0, albumin_creatinine_ratio: 16.4,
    diabetes_diagnosed: "2.0", insulin_use: "2.0", diabetes_pills: "2.0",
    ever_smoked: "1.0", current_smoker: "3.0"
  },
  stage3a: {
    age: 68, gender: "Female", ethnicity: "Mexican American", education_level: "2",
    poverty_income_ratio: 1.8, bmi: 29.8, weight_kg: 74.0, height_cm: 158.0,
    bp_systolic: 142, bp_diastolic: 88, blood_urea_nitrogen: 26.0, albumin_serum: 3.9,
    phosphorus: 4.1, bicarbonate: 22.0, calcium: 9.0, uric_acid: 6.8,
    urine_creatinine: 95.0, urine_albumin: 45.0, albumin_creatinine_ratio: 47.4,
    diabetes_diagnosed: "1.0", insulin_use: "2.0", diabetes_pills: "1.0",
    ever_smoked: "2.0", current_smoker: "3.0"
  },
  stage4: {
    age: 74, gender: "Male", ethnicity: "Non-Hispanic White", education_level: "3",
    poverty_income_ratio: 1.5, bmi: 31.2, weight_kg: 90.0, height_cm: 170.0,
    bp_systolic: 155, bp_diastolic: 92, blood_urea_nitrogen: 48.0, albumin_serum: 3.4,
    phosphorus: 5.4, bicarbonate: 19.0, calcium: 8.5, uric_acid: 8.2,
    urine_creatinine: 70.0, urine_albumin: 350.0, albumin_creatinine_ratio: 500.0,
    diabetes_diagnosed: "1.0", insulin_use: "1.0", diabetes_pills: "1.0",
    ever_smoked: "1.0", current_smoker: "3.0"
  },
  stage5: {
    age: 79, gender: "Female", ethnicity: "Non-Hispanic Black", education_level: "1",
    poverty_income_ratio: 1.2, bmi: 26.4, weight_kg: 66.0, height_cm: 158.0,
    bp_systolic: 168, bp_diastolic: 98, blood_urea_nitrogen: 85.0, albumin_serum: 2.9,
    phosphorus: 6.8, bicarbonate: 16.0, calcium: 7.8, uric_acid: 9.5,
    urine_creatinine: 45.0, urine_albumin: 1200.0, albumin_creatinine_ratio: 2666.7,
    diabetes_diagnosed: "1.0", insulin_use: "1.0", diabetes_pills: "1.0",
    ever_smoked: "1.0", current_smoker: "3.0"
  }
};

// Page Initialization Logic
document.addEventListener("DOMContentLoaded", () => {
  checkApiHealth();

  // If on Predictor page, check for edit data to pre-fill
  if (document.getElementById("ckd-form")) {
    initPredictorPage();
  }

  // If on Results page, render results from sessionStorage
  if (document.getElementById("active-results-section")) {
    initResultsPage();
  }

  // If on Records page, fetch and render records
  if (document.getElementById("records-container")) {
    initRecordsPage();
  }

  // If on Patient Timeline page, fetch patient data and render charts
  if (document.getElementById("patient-main-content") || document.getElementById("patient-header-section")) {
    initPatientPage();
  }
});


async function checkApiHealth() {
  const badgeText = document.getElementById("api-health-text");
  if (!badgeText) return;
  try {
    const res = await fetch("/health");
    if (res.ok) {
      badgeText.textContent = "Backend API Live";
    } else {
      badgeText.textContent = "API Error";
    }
  } catch (err) {
    badgeText.textContent = "API Offline";
  }
}

// Predictor Page Pre-fill Logic (for Editing & Re-predicting)
function initPredictorPage() {
  const editDataRaw = sessionStorage.getItem("edit_preset_data");
  if (!editDataRaw) return;

  try {
    const record = JSON.parse(editDataRaw);
    fillPredictorForm(record);
    showEditBanner(record.patient_name || "Anonymous Patient");
    sessionStorage.removeItem("edit_preset_data");
  } catch (err) {
    console.error("Failed to parse edit preset data:", err);
  }
}

function fillPredictorForm(data) {
  const fields = [
    'patient_name', 'age', 'gender', 'ethnicity', 'education_level', 
    'poverty_income_ratio', 'bmi', 'weight_kg', 'height_cm', 'bp_systolic', 
    'bp_diastolic', 'blood_urea_nitrogen', 'albumin_serum', 'phosphorus', 
    'bicarbonate', 'calcium', 'uric_acid', 'urine_creatinine', 'urine_albumin', 
    'albumin_creatinine_ratio', 'diabetes_diagnosed', 'insulin_use', 
    'diabetes_pills', 'ever_smoked', 'current_smoker'
  ];

  fields.forEach(field => {
    const el = document.getElementById(field);
    if (el && data[field] !== undefined && data[field] !== null) {
      let val = data[field];
      if (el.tagName === 'SELECT') {
        const strVal = String(val);
        let matched = Array.from(el.options).some(opt => opt.value === strVal);
        if (!matched) {
          const numVal = parseFloat(val);
          Array.from(el.options).some(opt => {
            if (parseFloat(opt.value) === numVal) {
              val = opt.value;
              return true;
            }
            return false;
          });
        }
      }
      el.value = val;
      el.classList.remove("is-invalid");
    }
  });

  const submitBtn = document.getElementById("submit-btn");
  if (submitBtn) submitBtn.scrollIntoView({ behavior: "smooth", block: "center" });
}

function showEditBanner(patientName) {
  const form = document.getElementById("ckd-form");
  if (!form) return;

  const existingBanner = document.getElementById("edit-banner");
  if (existingBanner) existingBanner.remove();

  const banner = document.createElement("div");
  banner.id = "edit-banner";
  banner.className = "edit-mode-banner";
  banner.innerHTML = `
    <div>
      <strong>✏️ Edit & Re-predict Mode:</strong> Pre-filled clinical parameters for <strong>${patientName}</strong>. 
      Submitting this form will log a <em>new prediction record</em> without altering previous history.
    </div>
    <button type="button" class="btn-preset" onclick="this.parentElement.remove()" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">✕ Dismiss</button>
  `;

  form.insertBefore(banner, form.firstChild);
}

// Load Presets on Predictor Form
function loadPreset(key) {
  const data = PRESETS[key];
  if (!data) return;

  fillPredictorForm(data);

  // If edit banner exists, remove it when loading a static preset
  const existingBanner = document.getElementById("edit-banner");
  if (existingBanner) existingBanner.remove();
}

// Handle Form Submission on predict.html
async function handlePrediction(event) {
  event.preventDefault();

  const form = document.getElementById("ckd-form");
  if (!form) return;

  const formData = new FormData(form);
  const payload = {};
  let isValid = true;

  // Clear previous validation errors
  document.querySelectorAll(".invalid-feedback").forEach(el => el.textContent = "");
  document.querySelectorAll(".form-control").forEach(el => el.classList.remove("is-invalid"));

  // Collect and validate all 24 required fields + patient_name
  formData.forEach((value, key) => {
    if (!value || value.trim() === "") {
      showFieldError(key, "This field is required.");
      isValid = false;
    } else {
      if (key === "gender" || key === "ethnicity" || key === "patient_name") {
        payload[key] = value;
      } else {
        payload[key] = parseFloat(value);
      }
    }
  });

  if (!isValid) return;

  // Show Loading Overlay
  const loadingEl = document.getElementById("loading-state");
  if (loadingEl) {
    loadingEl.style.display = "block";
    loadingEl.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (loadingEl) loadingEl.style.display = "none";

    if (response.ok) {
      // Store result & input values in sessionStorage, then redirect to results.html
      sessionStorage.setItem("ckd_prediction_result", JSON.stringify(result));
      sessionStorage.setItem("ckd_prediction_inputs", JSON.stringify(payload));
      window.location.href = "results.html";
    } else {
      alert(`Prediction Error: ${result.error || "Unknown server error"}`);
    }
  } catch (err) {
    if (loadingEl) loadingEl.style.display = "none";
    alert(`Network Error: Failed to connect to Flask API server. ${err.message}`);
  }
}

function showFieldError(fieldId, message) {
  const inputEl = document.getElementById(fieldId);
  const errEl = document.getElementById(`err-${fieldId}`);
  if (inputEl) inputEl.classList.add("is-invalid");
  if (errEl) errEl.textContent = message;
}

// Render Results Page from sessionStorage
function initResultsPage() {
  const rawData = sessionStorage.getItem("ckd_prediction_result");
  const noResultEl = document.getElementById("no-result-state");
  const activeResultEl = document.getElementById("active-results-section");

  if (!rawData) {
    if (noResultEl) noResultEl.style.display = "block";
    if (activeResultEl) activeResultEl.style.display = "none";
    return;
  }

  try {
    const data = JSON.parse(rawData);
    if (noResultEl) noResultEl.style.display = "none";
    if (activeResultEl) activeResultEl.style.display = "block";

    renderResultData(data);
  } catch (err) {
    if (noResultEl) noResultEl.style.display = "block";
    if (activeResultEl) activeResultEl.style.display = "none";
  }
}

function renderResultData(data) {
  const stage = data.predicted_stage;
  const confidencePct = (data.confidence * 100).toFixed(1) + "%";
  const stageInfo = STAGE_MAP[stage] || { index: 1, class: "badge-no-ckd" };
  const patientName = data.patient_name || "Anonymous Patient";

  const resPatientNameEl = document.getElementById("res-patient-name");
  if (resPatientNameEl) {
    resPatientNameEl.textContent = `Results for ${patientName}`;
  }

  // Badge & Confidence
  const badgeEl = document.getElementById("res-stage-badge");
  if (badgeEl) {
    badgeEl.textContent = stage;
    badgeEl.className = `stage-badge-large ${stageInfo.class}`;
  }

  const confEl = document.getElementById("res-confidence-num");
  if (confEl) confEl.textContent = confidencePct;

  // 7-Stage Gauge Segments
  for (let i = 1; i <= 7; i++) {
    const seg = document.getElementById(`g-seg-${i}`);
    if (seg) {
      if (i === stageInfo.index) {
        seg.classList.add("active");
      } else {
        seg.classList.remove("active");
      }
    }
  }

  // Explanation Text
  const expEl = document.getElementById("res-explanation-text");
  if (expEl) {
    expEl.textContent = STAGE_EXPLANATIONS[stage] || "Diagnosis evaluated based on ensemble machine learning probabilities.";
  }

  // Probabilities Rows
  const rowsContainer = document.getElementById("prob-rows-container");
  if (rowsContainer) {
    rowsContainer.innerHTML = "";
    if (data.stage_probabilities) {
      for (const [stgName, probVal] of Object.entries(data.stage_probabilities)) {
        const pct = (probVal * 100).toFixed(1);
        const isPredicted = stgName === stage;
        
        const rowDiv = document.createElement("div");
        rowDiv.className = "prob-row";
        rowDiv.innerHTML = `
          <div class="prob-meta">
            <span style="font-weight: ${isPredicted ? '700' : '400'}; color: ${isPredicted ? '#fff' : 'var(--text-muted)'};">
              ${isPredicted ? '⭐ ' : ''}${stgName}
            </span>
            <span style="font-weight: 700; color: ${isPredicted ? 'var(--primary-cyan)' : 'var(--text-dim)'};">${pct}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill" style="width: ${pct}%; background: ${isPredicted ? 'linear-gradient(90deg, var(--primary-teal), var(--primary-cyan))' : 'rgba(255,255,255,0.15)'};"></div>
          </div>
        `;
        rowsContainer.appendChild(rowDiv);
      }
    }
  }
}

// Clear Stored Prediction and Navigate to Predictor Page
function clearAndNewPrediction() {
  sessionStorage.removeItem("ckd_prediction_result");
  sessionStorage.removeItem("ckd_prediction_inputs");
  window.location.href = "predict.html";
}

// ==========================================
// Records Page Logic (Grouped by Patient)
// ==========================================
let allRecords = [];
// Holds the records loaded on the Patient Timeline page so that editRecord()
// and deleteRecord() can find them even when allRecords[] is empty.
let patientPageRecords = [];

async function initRecordsPage() {
  const container = document.getElementById("records-container");
  const loading = document.getElementById("records-loading-state");
  const empty = document.getElementById("records-empty-state");
  const filter = document.getElementById("stage-filter");
  
  if (!container || !loading || !empty) return;
  
  container.innerHTML = "";
  empty.style.display = "none";
  loading.style.display = "block";
  
  try {
    const res = await fetch("/history");
    if (!res.ok) throw new Error("Failed to fetch history");
    const data = await res.json();
    
    allRecords = data.history || [];
    
    if (filter) filter.value = "All"; // Reset filter
    
    renderRecords();
  } catch (err) {
    console.error(err);
    empty.querySelector("h3").textContent = "Error Loading Records";
    empty.querySelector("p").textContent = "Could not connect to the API. Please try again later.";
    empty.style.display = "block";
  } finally {
    loading.style.display = "none";
  }
}

function filterRecords() {
  renderRecords();
}

function renderRecords() {
  const container = document.getElementById("records-container");
  const empty = document.getElementById("records-empty-state");
  const filter = document.getElementById("stage-filter");
  const searchInput = document.getElementById("patient-search");
  
  if (!container || !empty) return;
  
  container.innerHTML = "";
  
  const filterVal = filter ? filter.value : "All";
  const searchVal = searchInput ? searchInput.value.toLowerCase().trim() : "";
  
  const filteredRecords = allRecords.filter(r => {
    const stageMatch = filterVal === "All" || r.predicted_stage === filterVal;
    const nameMatch = !searchVal || (r.patient_name && r.patient_name.toLowerCase().includes(searchVal));
    return stageMatch && nameMatch;
  });
  
  if (filteredRecords.length === 0) {
    empty.querySelector("h3").textContent = "No records found";
    empty.querySelector("p").textContent = "It looks like there are no predictions matching your criteria.";
    empty.style.display = "block";
    return;
  }
  
  empty.style.display = "none";

  // Group records by patient name
  const patientMap = new Map();
  filteredRecords.forEach(record => {
    const rawName = (record.patient_name || 'Anonymous Patient').trim();
    const key = rawName.toLowerCase();
    
    if (!patientMap.has(key)) {
      patientMap.set(key, {
        name: rawName,
        records: []
      });
    }
    patientMap.get(key).records.push(record);
  });
  
  patientMap.forEach((patientGroup) => {
    const patientName = patientGroup.name;
    const records = patientGroup.records;
    const recordCount = records.length;
    const latestRecord = records[0]; // sorted most recent first from API
    const patientId = latestRecord.patient_id;
    const latestStageInfo = STAGE_MAP[latestRecord.predicted_stage] || { class: "badge-no-ckd" };
    
    // Check if patient has active alerts between most recent and prior visit
    const activeAlertTypes = checkPatientAlerts(records);
    let alertBadgeHTML = "";
    if (activeAlertTypes && activeAlertTypes.length > 0) {
      const alertTitle = `Active Alert: ${activeAlertTypes.join(', ')}`;
      alertBadgeHTML = patientId ? 
        `<a href="patient.html?id=${patientId}" class="badge-alert-warning" title="${alertTitle}">⚠️ Alert (${activeAlertTypes.join(', ')})</a>` : 
        `<span class="badge-alert-warning" title="${alertTitle}">⚠️ Alert (${activeAlertTypes.join(', ')})</span>`;
    }

    const patientHeaderHTML = patientId ? 
      `<a href="patient.html?id=${patientId}" class="patient-name-link">👤 ${patientName}</a>` : 
      `👤 ${patientName}`;

    const card = document.createElement("div");
    card.className = "glass-panel patient-card";
    
    let recordsHTML = "";
    records.forEach((record) => {
      const stageInfo = STAGE_MAP[record.predicted_stage] || { class: "badge-no-ckd" };
      const confPct = (record.confidence * 100).toFixed(1) + "%";
      const dateStr = record.created_at ? new Date(record.created_at).toLocaleString() : 'N/A';

      recordsHTML += `
        <div class="patient-record-item">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
              <div style="color: var(--text-muted); font-size: 0.88rem; margin-bottom: 0.35rem;">🕒 ${dateStr}</div>
              <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <span class="stage-badge-small ${stageInfo.class}" style="padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 700; font-size: 0.8rem;">${record.predicted_stage}</span>
                <span style="color: #fff; font-weight: 500; font-size: 0.9rem;">Confidence: ${confPct}</span>
              </div>
            </div>

            <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
              <button class="btn-preset" onclick="toggleRecordDetails(${record.id})" style="padding: 0.4rem 0.85rem; width: auto; font-size: 0.85rem;">👁️ Details</button>
              <button class="btn-action-edit" onclick="editRecord(${record.id})">✏️ Edit & Re-predict</button>
              <button class="btn-action-delete" onclick="deleteRecord(${record.id})">🗑️ Delete</button>
            </div>
          </div>
          
          <div id="details-${record.id}" style="display: none; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
            <h4 style="color: var(--primary-cyan); margin-bottom: 1rem; font-size: 0.95rem;">Clinical Input Parameters (24 Features)</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.75rem; font-size: 0.88rem;">
              <div><span style="color: var(--text-muted);">Age:</span> ${record.age}</div>
              <div><span style="color: var(--text-muted);">Gender:</span> ${record.gender === '1' || record.gender === 1 || record.gender === 'Male' ? 'Male' : 'Female'}</div>
              <div><span style="color: var(--text-muted);">Ethnicity:</span> ${record.ethnicity}</div>
              <div><span style="color: var(--text-muted);">Edu Level:</span> ${record.education_level}</div>
              <div><span style="color: var(--text-muted);">Poverty Ratio:</span> ${record.poverty_income_ratio}</div>
              <div><span style="color: var(--text-muted);">BMI:</span> ${record.bmi}</div>
              <div><span style="color: var(--text-muted);">Weight (kg):</span> ${record.weight_kg}</div>
              <div><span style="color: var(--text-muted);">Height (cm):</span> ${record.height_cm}</div>
              <div><span style="color: var(--text-muted);">BP Systolic:</span> ${record.bp_systolic}</div>
              <div><span style="color: var(--text-muted);">BP Diastolic:</span> ${record.bp_diastolic}</div>
              <div><span style="color: var(--text-muted);">BUN:</span> ${record.blood_urea_nitrogen}</div>
              <div><span style="color: var(--text-muted);">Serum Albumin:</span> ${record.albumin_serum}</div>
              <div><span style="color: var(--text-muted);">Phosphorus:</span> ${record.phosphorus}</div>
              <div><span style="color: var(--text-muted);">Bicarbonate:</span> ${record.bicarbonate}</div>
              <div><span style="color: var(--text-muted);">Calcium:</span> ${record.calcium}</div>
              <div><span style="color: var(--text-muted);">Uric Acid:</span> ${record.uric_acid}</div>
              <div><span style="color: var(--text-muted);">Urine Creatinine:</span> ${record.urine_creatinine}</div>
              <div><span style="color: var(--text-muted);">Urine Albumin:</span> ${record.urine_albumin}</div>
              <div><span style="color: var(--text-muted);">Urine ACR:</span> ${record.albumin_creatinine_ratio}</div>
              <div><span style="color: var(--text-muted);">Diabetes Dx:</span> ${record.diabetes_diagnosed}</div>
              <div><span style="color: var(--text-muted);">Insulin Use:</span> ${record.insulin_use}</div>
              <div><span style="color: var(--text-muted);">Diabetes Pills:</span> ${record.diabetes_pills}</div>
              <div><span style="color: var(--text-muted);">Ever Smoked:</span> ${record.ever_smoked}</div>
              <div><span style="color: var(--text-muted);">Current Smoker:</span> ${record.current_smoker}</div>
            </div>
          </div>
        </div>
      `;
    });

    card.innerHTML = `
      <div class="patient-card-header">
        <div>
          <h3 style="color: #fff; font-size: 1.3rem; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
            ${patientHeaderHTML}
            ${alertBadgeHTML}
          </h3>
          <span style="background: rgba(13, 148, 136, 0.2); color: var(--primary-cyan); border: 1px solid rgba(6, 182, 212, 0.3); font-size: 0.8rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 12px;">
            📊 ${recordCount} ${recordCount === 1 ? 'Prediction' : 'Predictions Logged'}
          </span>
        </div>
        
        <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
          <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Latest Diagnosis</div>
            <span class="stage-badge-small ${latestStageInfo.class}" style="padding: 0.25rem 0.75rem; border-radius: 14px; font-weight: 700; font-size: 0.8rem;">${latestRecord.predicted_stage}</span>
          </div>
        </div>
      </div>
      <div class="patient-card-records">
        ${recordsHTML}
      </div>
    `;

    container.appendChild(card);
  });
}

const STAGE_NUMERIC = {
  "No CKD": 0,
  "Stage 1 (Kidney Damage)": 1,
  "Stage 2 (Mildly Decreased)": 2,
  "Stage 3a (Mild-Moderate)": 3,
  "Stage 3b (Moderate-Severe)": 4,
  "Stage 4 (Severely Decreased)": 5,
  "Stage 5 (Kidney Failure)": 6
};

function checkPatientAlerts(records) {
  // records sorted most recent first
  if (!records || records.length < 2) return null;
  const curr = records[0];
  const prev = records[1];

  const currStageVal = STAGE_NUMERIC[curr.predicted_stage] !== undefined ? STAGE_NUMERIC[curr.predicted_stage] : 0;
  const prevStageVal = STAGE_NUMERIC[prev.predicted_stage] !== undefined ? STAGE_NUMERIC[prev.predicted_stage] : 0;
  const stageWorsened = currStageVal > prevStageVal;

  const sysDiff = parseFloat(curr.bp_systolic || 0) - parseFloat(prev.bp_systolic || 0);
  const diaDiff = parseFloat(curr.bp_diastolic || 0) - parseFloat(prev.bp_diastolic || 0);
  const bpElevated = sysDiff > 15 || diaDiff > 15;

  const bunDiff = parseFloat(curr.blood_urea_nitrogen || 0) - parseFloat(prev.blood_urea_nitrogen || 0);
  const acrDiff = parseFloat(curr.albumin_creatinine_ratio || 0) - parseFloat(prev.albumin_creatinine_ratio || 0);
  const labElevated = bunDiff > 5 || acrDiff > 30;

  if (stageWorsened || bpElevated || labElevated) {
    const alerts = [];
    if (stageWorsened) alerts.push("Stage Progression");
    if (bpElevated) alerts.push("Blood Pressure");
    if (labElevated) alerts.push("Lab Values");
    return alerts;
  }
  return null;
}


function toggleRecordDetails(id) {
  const el = document.getElementById(`details-${id}`);
  if (el) {
    el.style.display = el.style.display === "none" ? "block" : "none";
  }
}

function editRecord(recordId) {
  // Search allRecords (Records page) first, then fall back to patientPageRecords (Patient page)
  const rec = allRecords.find(r => r.id === recordId) || patientPageRecords.find(r => r.id === recordId);
  if (!rec) {
    alert("Record not found.");
    return;
  }
  sessionStorage.setItem("edit_preset_data", JSON.stringify(rec));
  window.location.href = "predict.html";
}

async function deleteRecord(recordId) {
  // Search allRecords (Records page) first, then fall back to patientPageRecords (Patient page)
  const rec = allRecords.find(r => r.id === recordId) || patientPageRecords.find(r => r.id === recordId);
  const displayName = rec && rec.patient_name ? rec.patient_name : "Anonymous Patient";
  
  if (!confirm(`Are you sure you want to delete prediction record #${recordId} for "${displayName}"?`)) {
    return;
  }

  try {
    const res = await fetch(`/prediction/${recordId}`, {
      method: "DELETE"
    });
    const data = await res.json();
    if (res.ok) {
      allRecords = allRecords.filter(r => r.id !== recordId);
      renderRecords();
    } else {
      alert(`Delete failed: ${data.error || "Server error"}`);
    }
  } catch (err) {
    alert(`Network Error: ${err.message}`);
  }
}

// ==========================================
// Patient Timeline & Trend Charts Page Logic
// ==========================================
async function initPatientPage() {
  const loading = document.getElementById("patient-loading-state");
  const errorState = document.getElementById("patient-error-state");
  const mainContent = document.getElementById("patient-main-content");
  const headerName = document.getElementById("patient-title-name");
  const metaBadges = document.getElementById("patient-meta-badges");
  const alertsContainer = document.getElementById("patient-alerts-container");

  if (!mainContent) return;

  const urlParams = new URLSearchParams(window.location.search);
  const patientId = urlParams.get("id");

  if (!patientId) {
    if (loading) loading.style.display = "none";
    if (errorState) {
      errorState.style.display = "block";
      document.getElementById("error-state-title").textContent = "Invalid Patient ID";
      document.getElementById("error-state-msg").textContent = "No patient ID parameter was specified in the URL.";
    }
    return;
  }

  try {
    const res = await fetch(`/patient/${patientId}`);
    if (!res.ok) {
      if (loading) loading.style.display = "none";
      if (errorState) {
        errorState.style.display = "block";
        document.getElementById("error-state-title").textContent = "Patient Not Found";
        document.getElementById("error-state-msg").textContent = `Patient ID #${patientId} does not exist or has no recorded clinical predictions.`;
      }
      return;
    }

    const data = await res.json();
    const patient = data.patient || {};
    const predictions = data.predictions || []; // sorted ASC (oldest to newest) from API
    const alerts = data.alerts || [];

    if (loading) loading.style.display = "none";
    if (mainContent) mainContent.style.display = "block";

    // Header Info
    if (headerName) headerName.textContent = patient.name || "Anonymous Patient";
    if (metaBadges) {
      const latest = predictions.length > 0 ? predictions[predictions.length - 1] : null;
      const latestStage = latest ? latest.predicted_stage : "N/A";
      const latestStageInfo = STAGE_MAP[latestStage] || { class: "badge-no-ckd" };
      metaBadges.innerHTML = `
        <span style="background: rgba(13, 148, 136, 0.2); color: var(--primary-cyan); border: 1px solid rgba(6, 182, 212, 0.3); font-size: 0.85rem; font-weight: 600; padding: 0.3rem 0.8rem; border-radius: 16px;">
          🆔 Patient ID: #${patientId}
        </span>
        <span style="background: rgba(255, 255, 255, 0.05); color: #fff; border: 1px solid var(--border-color); font-size: 0.85rem; font-weight: 600; padding: 0.3rem 0.8rem; border-radius: 16px;">
          📊 ${predictions.length} ${predictions.length === 1 ? 'Visit Record' : 'Visit Records'}
        </span>
        ${latest ? `<span class="stage-badge-small ${latestStageInfo.class}" style="padding: 0.35rem 0.85rem; border-radius: 16px; font-weight: 700; font-size: 0.85rem;">Latest: ${latestStage}</span>` : ''}
      `;
    }

    // Render Alerts
    if (alertsContainer) {
      alertsContainer.innerHTML = "";
      if (alerts.length > 0) {
        alerts.forEach(alert => {
          let bannerClass = "alert-banner-stage";
          let icon = "🚨";
          if (alert.type.includes("Blood Pressure")) {
            bannerClass = "alert-banner-bp";
            icon = "⚠️";
          } else if (alert.type.includes("Lab Value")) {
            bannerClass = "alert-banner-lab";
            icon = "🧪";
          }
          const banner = document.createElement("div");
          banner.className = `alert-banner ${bannerClass}`;
          banner.innerHTML = `
            <div class="alert-banner-icon">${icon}</div>
            <div>
              <div class="alert-banner-title">${alert.type}</div>
              <div class="alert-banner-msg">${alert.message}</div>
            </div>
          `;
          alertsContainer.appendChild(banner);
        });
      }
    }

    // Render Plotly Charts
    if (predictions.length > 0) {
      renderStageTrendChart(predictions);
      renderVitalsTrendChart(predictions);
    }

    // Render Timeline Records (oldest at bottom, most recent at top)
    renderPatientTimelineRecords(predictions);

  } catch (err) {
    console.error("Error loading patient details:", err);
    if (loading) loading.style.display = "none";
    if (errorState) {
      errorState.style.display = "block";
      document.getElementById("error-state-title").textContent = "Failed to Load Patient";
      document.getElementById("error-state-msg").textContent = `An error occurred: ${err.message}`;
    }
  }
}

function renderStageTrendChart(predictions) {
  const chartEl = document.getElementById("stage-trend-chart");
  if (!chartEl || typeof Plotly === "undefined") return;

  const dates = predictions.map((p, idx) => {
    return p.created_at ? new Date(p.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : `Visit ${idx + 1}`;
  });

  const numericStages = predictions.map(p => STAGE_NUMERIC[p.predicted_stage] !== undefined ? STAGE_NUMERIC[p.predicted_stage] : 0);
  const stageHoverTexts = predictions.map(p => `${p.predicted_stage}<br>Confidence: ${(p.confidence * 100).toFixed(1)}%`);

  const trace = {
    x: dates,
    y: numericStages,
    text: stageHoverTexts,
    hoverinfo: "x+text",
    mode: 'lines+markers',
    line: { shape: 'vh', color: '#06b6d4', width: 3 },
    marker: { size: 10, color: '#0d9488', symbol: 'circle', line: { color: '#ffffff', width: 2 } },
    type: 'scatter'
  };

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
    margin: { l: 150, r: 40, t: 30, b: 60 },
    xaxis: {
      title: { text: 'Visit Date / Time', font: { color: '#94a3b8', size: 12 } },
      tickfont: { color: '#f8fafc', size: 11 },
      gridcolor: 'rgba(255, 255, 255, 0.08)',
      showgrid: true
    },
    yaxis: {
      title: { text: 'CKD Severity Scale', font: { color: '#94a3b8', size: 12 } },
      tickvals: [0, 1, 2, 3, 4, 5, 6],
      ticktext: ['No CKD (0)', 'Stage 1 (1)', 'Stage 2 (2)', 'Stage 3a (3)', 'Stage 3b (4)', 'Stage 4 (5)', 'Stage 5 (6)'],
      tickfont: { color: '#f8fafc', size: 11 },
      gridcolor: 'rgba(255, 255, 255, 0.08)',
      range: [-0.5, 6.5]
    },
    autosize: true
  };

  const config = { responsive: true, displayModeBar: false };
  Plotly.newPlot('stage-trend-chart', [trace], layout, config);
}

function renderVitalsTrendChart(predictions) {
  const chartEl = document.getElementById("vitals-trend-chart");
  if (!chartEl || typeof Plotly === "undefined") return;

  const dates = predictions.map((p, idx) => {
    return p.created_at ? new Date(p.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : `Visit ${idx + 1}`;
  });

  const sysBP = predictions.map(p => parseFloat(p.bp_systolic || 0));
  const diaBP = predictions.map(p => parseFloat(p.bp_diastolic || 0));
  const bunVals = predictions.map(p => parseFloat(p.blood_urea_nitrogen || 0));

  const traceSys = {
    x: dates,
    y: sysBP,
    name: 'Systolic BP (mmHg)',
    mode: 'lines+markers',
    line: { color: '#f43f5e', width: 2.5 },
    marker: { size: 8 }
  };

  const traceDia = {
    x: dates,
    y: diaBP,
    name: 'Diastolic BP (mmHg)',
    mode: 'lines+markers',
    line: { color: '#f59e0b', width: 2.5 },
    marker: { size: 8 }
  };

  const traceBUN = {
    x: dates,
    y: bunVals,
    name: 'BUN (mg/dL)',
    yaxis: 'y2',
    mode: 'lines+markers',
    line: { color: '#06b6d4', width: 2.5, dash: 'dot' },
    marker: { size: 8 }
  };

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(15, 23, 42, 0.5)',
    margin: { l: 60, r: 60, t: 30, b: 60 },
    legend: { font: { color: '#f8fafc' }, orientation: 'h', y: 1.12 },
    xaxis: {
      title: { text: 'Visit Date / Time', font: { color: '#94a3b8', size: 12 } },
      tickfont: { color: '#f8fafc', size: 11 },
      gridcolor: 'rgba(255, 255, 255, 0.08)'
    },
    yaxis: {
      title: { text: 'Blood Pressure (mmHg)', font: { color: '#f43f5e', size: 12 } },
      tickfont: { color: '#f8fafc', size: 11 },
      gridcolor: 'rgba(255, 255, 255, 0.08)'
    },
    yaxis2: {
      title: { text: 'Blood Urea Nitrogen (mg/dL)', font: { color: '#06b6d4', size: 12 } },
      tickfont: { color: '#06b6d4', size: 11 },
      overlaying: 'y',
      side: 'right',
      showgrid: false
    },
    autosize: true
  };

  const config = { responsive: true, displayModeBar: false };
  Plotly.newPlot('vitals-trend-chart', [traceSys, traceDia, traceBUN], layout, config);
}

function renderPatientTimelineRecords(predictions) {
  const container = document.getElementById("patient-timeline-records");
  if (!container) return;

  // Cache predictions so editRecord() and deleteRecord() can find them from this page
  patientPageRecords = predictions;

  container.innerHTML = "";

  // Predictions are ordered oldest to newest, so reverse to show most recent at top
  const sortedRecords = [...predictions].reverse();

  sortedRecords.forEach((record, index) => {
    const stageInfo = STAGE_MAP[record.predicted_stage] || { class: "badge-no-ckd" };
    const confPct = (record.confidence * 100).toFixed(1) + "%";
    const dateStr = record.created_at ? new Date(record.created_at).toLocaleString() : 'N/A';
    const visitNum = sortedRecords.length - index;

    const card = document.createElement("div");
    card.className = "glass-panel patient-record-item";
    card.style.padding = "1.5rem";
    card.style.borderRadius = "var(--radius-md)";

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem;">
            <span style="background: rgba(6, 182, 212, 0.15); color: var(--primary-cyan); font-weight: 700; font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 10px;">
              Visit #${visitNum}
            </span>
            <span style="color: var(--text-muted); font-size: 0.88rem;">🕒 ${dateStr}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
            <span class="stage-badge-small ${stageInfo.class}" style="padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">${record.predicted_stage}</span>
            <span style="color: #fff; font-weight: 500; font-size: 0.9rem;">Confidence: ${confPct}</span>
          </div>
        </div>

        <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
          <button class="btn-preset" onclick="toggleRecordDetails('pat-${record.id}')" style="padding: 0.4rem 0.85rem; width: auto; font-size: 0.85rem;">👁️ Details</button>
          <button class="btn-action-edit" onclick="editRecord(${record.id})">✏️ Edit & Re-predict</button>
          <button class="btn-action-delete" onclick="deleteRecord(${record.id})">🗑️ Delete</button>
        </div>
      </div>
      
      <div id="details-pat-${record.id}" style="display: none; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <h4 style="color: var(--primary-cyan); margin-bottom: 1rem; font-size: 0.95rem;">Clinical Input Parameters (24 Features)</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 0.75rem; font-size: 0.88rem;">
          <div><span style="color: var(--text-muted);">Age:</span> ${record.age}</div>
          <div><span style="color: var(--text-muted);">Gender:</span> ${record.gender === '1' || record.gender === 1 || record.gender === 'Male' ? 'Male' : 'Female'}</div>
          <div><span style="color: var(--text-muted);">Ethnicity:</span> ${record.ethnicity}</div>
          <div><span style="color: var(--text-muted);">Edu Level:</span> ${record.education_level}</div>
          <div><span style="color: var(--text-muted);">Poverty Ratio:</span> ${record.poverty_income_ratio}</div>
          <div><span style="color: var(--text-muted);">BMI:</span> ${record.bmi}</div>
          <div><span style="color: var(--text-muted);">Weight (kg):</span> ${record.weight_kg}</div>
          <div><span style="color: var(--text-muted);">Height (cm):</span> ${record.height_cm}</div>
          <div><span style="color: var(--text-muted);">BP Systolic:</span> ${record.bp_systolic}</div>
          <div><span style="color: var(--text-muted);">BP Diastolic:</span> ${record.bp_diastolic}</div>
          <div><span style="color: var(--text-muted);">BUN:</span> ${record.blood_urea_nitrogen}</div>
          <div><span style="color: var(--text-muted);">Serum Albumin:</span> ${record.albumin_serum}</div>
          <div><span style="color: var(--text-muted);">Phosphorus:</span> ${record.phosphorus}</div>
          <div><span style="color: var(--text-muted);">Bicarbonate:</span> ${record.bicarbonate}</div>
          <div><span style="color: var(--text-muted);">Calcium:</span> ${record.calcium}</div>
          <div><span style="color: var(--text-muted);">Uric Acid:</span> ${record.uric_acid}</div>
          <div><span style="color: var(--text-muted);">Urine Creatinine:</span> ${record.urine_creatinine}</div>
          <div><span style="color: var(--text-muted);">Urine Albumin:</span> ${record.urine_albumin}</div>
          <div><span style="color: var(--text-muted);">Urine ACR:</span> ${record.albumin_creatinine_ratio}</div>
          <div><span style="color: var(--text-muted);">Diabetes Dx:</span> ${record.diabetes_diagnosed}</div>
          <div><span style="color: var(--text-muted);">Insulin Use:</span> ${record.insulin_use}</div>
          <div><span style="color: var(--text-muted);">Diabetes Pills:</span> ${record.diabetes_pills}</div>
          <div><span style="color: var(--text-muted);">Ever Smoked:</span> ${record.ever_smoked}</div>
          <div><span style="color: var(--text-muted);">Current Smoker:</span> ${record.current_smoker}</div>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}


