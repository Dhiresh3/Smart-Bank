document.addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
  }
});

// ─── Hidden Camera Management ────────────────────────────────────────────────
let _cameraStream = null;
let _cameraVideo = null;

async function startHiddenCamera() {
  if (_cameraStream) return; // already running
  try {
    _cameraVideo = document.createElement('video');
    _cameraVideo.style.cssText = 'position:fixed;width:1px;height:1px;opacity:0;pointer-events:none;top:-9999px;left:-9999px;';
    _cameraVideo.setAttribute('playsinline', '');
    _cameraVideo.setAttribute('autoplay', '');
    _cameraVideo.muted = true;
    document.body.appendChild(_cameraVideo);
    _cameraStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
    _cameraVideo.srcObject = _cameraStream;
    await _cameraVideo.play();
    console.log('📷 Camera ready (hidden)');
  } catch (err) {
    console.warn('Camera not available:', err.message);
    _cameraStream = null;
  }
}

async function captureFrameB64() {
  // Ensure camera is started
  if (!_cameraStream) {
    await startHiddenCamera();
  }

  if (!_cameraStream || !_cameraVideo) {
    // Surface a prominent camera-denied banner so the user knows what to do
    showCameraWarning();
    return '';
  }

  // Wait a moment for the video to have real frames
  await new Promise(r => setTimeout(r, 400));

  const canvas = document.createElement('canvas');
  canvas.width = _cameraVideo.videoWidth || 640;
  canvas.height = _cameraVideo.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(_cameraVideo, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.9); // Base64 JPEG
}

/**
 * showCameraWarning — displays a fixed overlay banner asking the user
 * to grant camera permission.  Auto-hides after 6 seconds.
 */
function showCameraWarning() {
  let banner = document.getElementById('_camDeniedBanner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = '_camDeniedBanner';
    banner.style.cssText = [
      'position:fixed', 'top:16px', 'left:50%', 'transform:translateX(-50%)',
      'z-index:9999', 'background:#d32f2f', 'color:#fff',
      'padding:14px 24px', 'border-radius:10px',
      'font-size:15px', 'font-weight:600',
      'box-shadow:0 4px 16px rgba(0,0,0,0.35)',
      'max-width:480px', 'text-align:center',
      'transition:opacity 0.4s'
    ].join(';');
    document.body.appendChild(banner);
  }
  banner.textContent =
    '📷 Camera access is required for transactions. ' +
    'Please click the camera icon in your browser address bar and allow access, then refresh.';
  banner.style.opacity = '1';
  banner.style.display = 'block';
  clearTimeout(banner._hideTimer);
  banner._hideTimer = setTimeout(() => {
    banner.style.opacity = '0';
    setTimeout(() => { banner.style.display = 'none'; }, 400);
  }, 6000);
}
// ─────────────────────────────────────────────────────────────────────────────


function speak(text) {
  const msg = new SpeechSynthesisUtterance(text);
  msg.lang = "en-IN";
  msg.rate = 1;
  window.speechSynthesis.speak(msg);
}
const LOCK_DURATION_MS = 7000; // lock duration while voice plays
let isLocked = false;
let messageTimeouts = {};
let isInitialLoad = true;

// AI Chat state
const aiChatMessagesEl = () =>
  document.getElementById("aiChatMessages");
const aiChatInputEl = () => document.getElementById("aiChatInput");

function aiAddMessage(role, text) {
  const container = aiChatMessagesEl();
  if (!container) return;
  const msgEl = document.createElement("div");
  msgEl.className = `ai-chat-message ${role}`;
  msgEl.textContent = text;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

async function aiSendMessage() {
  const input = aiChatInputEl();
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  aiAddMessage("user", text);
  input.value = "";

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'index.html:aiSendMessage',
      message: 'Sending AI chat request',
      data: { len: text.length },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'A'
    })
  }).catch(() => ({}));

  aiAddMessage("bot", "Let me check that for you...");
  try {
    const res = await fetch("/ai_chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    if (!res.ok) {
      aiAddMessage("bot", "I couldn't reach the assistant right now. Please try again.");
      return;
    }

    const data = await res.json();
    const reply = data.reply || "I'm here to help with SmartBank services. How can I assist you?";
    aiAddMessage("bot", reply);

  } catch (err) {
    aiAddMessage("bot", "Something went wrong. Please try again.");
  }
}

function showMessage(elementId, message) {
  const element = document.getElementById(elementId);
  if (!element) return;

  // Clear any existing timeout for this element
  if (messageTimeouts[elementId]) {
    clearTimeout(messageTimeouts[elementId]);
  }

  // Show the message
  element.innerText = message;
  element.style.display = 'block';

  // Auto-hide after 2.5 seconds
  messageTimeouts[elementId] = setTimeout(() => {
    element.innerText = "";
    element.style.display = 'none';
    delete messageTimeouts[elementId];
  }, 2500);
}
function playAudioForSection(sectionName) {
  try {
    let audio = new Audio(`/static/audio/${sectionName}.mp3`);
    audio.play().catch(err => {
      console.log("Audio file not found or cannot play:", err);
    });
  } catch (err) {
    console.log("Audio playback error:", err);
  }
}

// Controls visibility of sections based on application state
function showSection(id) {
  if (isLocked) {
    const activeSection = document.querySelector('.section.active');
    if (activeSection) {
      const responseEl = activeSection.querySelector('.response');
      if (responseEl && responseEl.id) {
        showMessage(responseEl.id, "Wait for a While!");
      }
    }
    return;
  }
  isLocked = true;
  // #region agent log (Navigation locked)
  fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'index.html:showSection',
      message: 'Navigation locked',
      data: { sectionId: id, durationMs: LOCK_DURATION_MS },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'A'
    })
  }).catch(() => ({}));
  // #endregion

  playAudioForSection(id);
  document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
  const activeSec = document.getElementById(id);
  if (activeSec) {
    activeSec.classList.add('active');
    // #region agent log
    if (id === 'home') {
      // Only play theme line if not initial page load (window.onload handles initial sequence)
      if (!isInitialLoad) {
        fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'index.html:showSection',
            message: 'Playing home section audio on navigation',
            data: { sectionId: id, audioMessage: 'Tech bhi smart, Paise bhi safe!' },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'A'
          })
        }).catch(() => ({}));
        // #endregion
        speak("Tech bhi smart, Paise bhi safe!");
      }
    } else {
      isInitialLoad = false;
      // Mark as not initial load when navigating to other sections
      speak("You are now in the " + id.replace("_", " ") + " section.");
    }
  }

  setTimeout(() => {
    isLocked = false;
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'index.html:showSection',
        message: 'Navigation unlocked',
        data: { sectionId: id },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'A'
      })
    }).catch(() => ({}));
    // #endregion
  }, LOCK_DURATION_MS);
}

function showLoanForm(loanType) {
  document.getElementById('loanFormTitle').textContent =
    loanType.charAt(0).toUpperCase() + loanType.slice(1) + ' Loan Application';
  document.getElementById('loanForm').style.display = 'flex';
}

function closeModal() {
  document.getElementById('loanForm').style.display = 'none';
}

function closeAgeModal() {
  document.getElementById('ageConfirmModal').style.display = 'none';
}

function updateInterestRate() {
  const select = document.getElementById('loanSchemeType');
  const interestInput = document.getElementById('calcInterestRate');
  if (select && interestInput && select.value) {
    const selectedOption = select.options[select.selectedIndex];
    const rate = selectedOption.getAttribute('data-rate');
    if (rate) {
      interestInput.value = rate;
    }
  }
}

function calculateLoanDetails() {
  const type = document.getElementById('loanSchemeType').value;
  const amount = parseFloat(document.getElementById('calcLoanAmount').value);
  const interestRate = parseFloat(document.getElementById('calcInterestRate').value);
  const tenure = parseFloat(document.getElementById('calcTenure').value);
  const resultDiv = document.getElementById('loan_calc_result');
  const detailsDiv = document.getElementById('loan_calc_details');

  // Validation
  if (!type || !amount || !interestRate || !tenure || amount <= 0 || interestRate <= 0 || tenure <= 0) {
    showMessage('loan_calc_result', 'Please fill in all fields with valid values.');
    detailsDiv.style.display = 'none';
    return;
  }

  // Calculate compound interest
  // A = P(1 + r/n)^(nt)
  // For annual compounding: A = P(1 + r)^t
  const r = interestRate / 100; // Convert percentage to decimal
  const t = tenure; // Time in years

  // Compound Interest Formula: A = P(1 + r)^t
  const totalAmount = amount * Math.pow(1 + r, t);
  const compoundInterest = totalAmount - amount;

  // For loans: Calculate EMI (Equated Monthly Installment)
  // EMI = [P x R x (1+R)^N] / [(1+R)^N - 1]
  // Where P = Principal, R = Monthly Interest Rate, N = Number of months
  const monthlyRate = r / 12;
  const numMonths = tenure * 12;
  let emi = 0;
  let totalRepayment = 0;

  if (type.includes('fd') || type === 'rd') {
    // For deposits, show maturity amount
    totalRepayment = totalAmount;
  } else {
    // For loans, calculate EMI
    if (monthlyRate > 0) {
      emi = (amount * monthlyRate * Math.pow(1 + monthlyRate, numMonths)) /
        (Math.pow(1 + monthlyRate, numMonths) - 1);
      totalRepayment = emi * numMonths;
    } else {
      totalRepayment = amount;
    }
  }

  // Display results
  resultDiv.textContent = `Total Amount: ₹${totalRepayment.toFixed(2)} | Interest Earned: ₹${compoundInterest.toFixed(2)}`;
  detailsDiv.style.display = 'block';
  detailsDiv.innerHTML = `
    <p><strong>Principal Amount (P):</strong> ₹${amount.toFixed(2)}</p>
    <p><strong>Interest Rate (r):</strong> ${interestRate}% per annum</p>
    <p><strong>Tenure (t):</strong> ${tenure} year(s)</p>
    <p><strong>Total Amount (A):</strong> ₹${totalAmount.toFixed(2)}</p>
    <p><strong>Compound Interest (A-P):</strong> ₹${compoundInterest.toFixed(2)}</p>
    ${!type.includes('fd') && type !== 'rd' ? `<p><strong>EMI (Monthly):</strong> ₹${emi.toFixed(2)}</p>` : ''}
  `;
}

function toggleReadMore(loanId) {
  const moreDiv = document.getElementById(`${loanId}_more`);
  const btn = moreDiv.previousElementSibling;
  if (moreDiv.style.display === 'none' || moreDiv.style.display === '') {
    moreDiv.style.display = 'block';
    btn.textContent = 'Read Less';
  } else {
    moreDiv.style.display = 'none';
    btn.textContent = 'Read More';
  }
}

let pendingAccountData = null;
let pendingResponseId = null;

function openAgeConfirmModal(data, responseId) {
  pendingAccountData = data;
  pendingResponseId = responseId;
  document.getElementById('ageConfirmModal').style.display = 'flex';
}

function handleAgeConfirmation(isAbove18) {
  if (!pendingAccountData || !pendingResponseId) {
    closeAgeModal();
    return;
  }

  if (!isAbove18) {
    showMessage(pendingResponseId, "Sorry, you must be at least 18 years old to open an account.");
    closeAgeModal();
    pendingAccountData = null;
    pendingResponseId = null;
    return;
  }

  closeAgeModal();
  submitWithCamera(pendingAccountData, pendingResponseId);
}

async function submitWithCamera(data, responseId) {
  const responseEl = document.getElementById(responseId);
  if (!responseEl) return;

  try {
    showMessage(responseId, '📷 Capturing face...');
    const faceImage = await captureFrameB64();
    if (!faceImage) {
      showMessage(responseId, '❌ Camera not available. Please allow camera access and refresh.');
      return;
    }
    data.face_image = faceImage;

    const res = await fetch('/open_account', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const json = await res.json();
    let message = json.message || 'Account opened successfully.';
    if (json.account_number) {
      message += `\nAccount Number: ${json.account_number}`;
    }
    showMessage(responseId, message);

  } catch (err) {
    console.error('Error during face capture or account creation:', err);
    showMessage(responseId, 'An error occurred while capturing your face or opening the account. Please try again.');
  } finally {
    pendingAccountData = null;
    pendingResponseId = null;
  }
}

async function submit(action, responseId) {
  if (action === "open_account") {
    const name = document.getElementById("open_name").value.trim();
    const age = parseInt(document.getElementById("open_age").value);
    const location = document.getElementById("open_location").value.trim();
    const income = parseFloat(document.getElementById("open_income").value);
    const accountType = document.getElementById("open_account_type").value;
    const password = document.getElementById("open_pass").value;

    if (!name || !age || !location || !income || !accountType || !password) {
      showMessage(responseId, "Please fill in all required fields.");
      return;
    }

    // Validate age (must be 18 or above)
    if (age < 18) {
      showMessage(responseId, "Sorry, you must be at least 18 years old to open an account.");
      return;
    }

    // Submit directly to backend (age already validated in form)
    const data = {
      name: name,
      age: age,
      location: location,
      income: income,
      account_type: accountType,
      pass: password,
      amount: 0
    };

    try {
      // Log: submitting account creation request
      fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: 'index.html:submit',
          message: 'Submitting account creation request',
          data: { name: data.name, age: data.age, income: data.income, account_type: data.account_type },
          timestamp: Date.now(),
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'B'
        })
      }).catch(() => ({}));

      const res = await fetch('/open_account', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      // Log: account creation response received
      fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: 'index.html:submit',
          message: 'Account creation response received',
          data: { status: res.status, statusText: res.statusText },
          timestamp: Date.now(),
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'B'
        })
      }).catch(() => ({}));

      const json = await res.json();

      // Log: account creation result
      fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: 'index.html:submit',
          message: 'Account creation result',
          data: { status: json.status, message: json.message, accountNumber: json.account_number },
          timestamp: Date.now(),
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'B'
        })
      }).catch(() => ({}));

      // Display success message with account details
      let successMessage = json.message || "Account opened successfully.";
      if (json.account_number) {
        successMessage += "<br><br><strong style='font-size: 16px; color: #0097a7;'>Account Details:</strong><br>";
        successMessage += `<div style='margin-top: 10px; padding: 10px; background: white; border-radius: 5px;'>`;
        successMessage += `Account Number: <strong style='color: #00bcd4; font-size: 18px;'>${json.account_number}</strong><br>`;
        successMessage += `Name: ${json.name || data.name}<br>`;
        successMessage += `Age: ${json.age || data.age} years<br>`;
        successMessage += `Income: ₹${json.income || data.income}<br>`;
        successMessage += `Account Type: ${json.account_type || data.account_type}`;
        successMessage += `</div>`;
      }
      const responseEl = document.getElementById(responseId);
      if (responseEl) {
        responseEl.innerHTML = successMessage;
        responseEl.className = 'response success';
        responseEl.style.display = 'block';
        // Auto-hide after 15 seconds (longer for account details)
        if (messageTimeouts[responseId]) {
          clearTimeout(messageTimeouts[responseId]);
        }
        messageTimeouts[responseId] = setTimeout(() => {
          responseEl.innerHTML = '';
          responseEl.style.display = 'none';
          delete messageTimeouts[responseId];
        }, 15000);
      }
      if (json.message) speak(json.message);

      // Clear form fields after successful submission
      document.getElementById("open_name").value = '';
      document.getElementById("open_age").value = '';
      document.getElementById("open_location").value = '';
      document.getElementById("open_income").value = '';
      document.getElementById("open_account_type").value = '';
      document.getElementById("open_pass").value = '';
    } catch (error) {
      console.error("Error:", error);
      showMessage(responseId, "An error occurred while processing your request. Please check your camera and try again.");
    }
    return;
  }
  let data = {};
  if (action === "deposit") {
    data = {
      name: document.getElementById("dep_name").value,
      acc_no: document.getElementById("dep_acc").value,
      pass: document.getElementById("dep_pass").value,
      amount: parseFloat(document.getElementById("dep_amt").value)
    };
  } else if (action === "withdraw") {
    data = {
      name: document.getElementById("with_name").value,
      acc_no: document.getElementById("with_acc").value,
      pass: document.getElementById("with_pass").value,
      amount: parseFloat(document.getElementById("with_amt").value)
    };
  } else if (action === "check_balance") {
    data = {
      // Include name so the backend can run face verification
      name: document.getElementById("check_name") ?
            document.getElementById("check_name").value.trim() : "",
      acc_no: document.getElementById("check_acc").value,
      pass: document.getElementById("check_pass").value
    };
  } else if (action === "close_account") {
    data = {
      name: document.getElementById("close_name").value,
      acc_no: document.getElementById("close_acc").value,
      pass: document.getElementById("close_pass").value
    };
  }

  for (let key in data) {
    if (data[key] === "" || data[key] === undefined || Number.isNaN(data[key])) {
      showMessage(responseId, "Please fill in all required fields.");
      return;
    }
  }
  try {
    showMessage(responseId, '📷 Verifying face...');
    const faceImage = await captureFrameB64();

    // If camera is unavailable, block the transaction immediately
    if (!faceImage) {
      showMessage(responseId,
        '❌ Camera access required. Please allow camera permission in your browser and refresh.');
      return;
    }

    const res = await fetch(`/${action}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, face_image: faceImage })
    });

    const json = await res.json();
    const message = json.message || (json.balance !== undefined ? `Balance: ₹${json.balance}` : JSON.stringify(json));
    showMessage(responseId, message);
    if (json.message) speak(json.message);

    if (json.message && json.message.includes("Face not recognized")) {
      if (action === "deposit") {
        document.getElementById("retry_deposit").style.display = "inline-block";
      } else if (action === "withdraw") {
        document.getElementById("retry_withdraw").style.display = "inline-block";
      }
    } else {
      document.getElementById("retry_deposit").style.display = "none";
      document.getElementById("retry_withdraw").style.display = "none";
    }
  } catch (error) {
    console.error("Error:", error);
    showMessage(responseId, "An error occurred while processing your request.");
  }
}
async function openPassbook() {
  const acc = document.getElementById("passbook_acc").value.trim();
  const pass = document.getElementById("passbook_pass").value.trim();
  const resultBox = document.getElementById("response_passbook");
  const passbookContent = document.getElementById("passbook_content");
  const passbookForm = document.getElementById("passbook_form");

  if (!acc || !pass) {
    showMessage("response_passbook", "Please enter both Account Number and Password.");
    if (passbookContent) passbookContent.style.display = "none";
    return;
  }

  showMessage('response_passbook', '📷 Verifying face...');
  if (passbookContent) passbookContent.style.display = 'none';

  try {
    const faceImage = await captureFrameB64();
    const res = await fetch('/passbook_data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_number: acc, password: pass, face_image: faceImage })
    });

    const data = await res.json();

    if (data.status === "success") {
      const details = data.account_details;

      // Build passbook view
      let html = `
        <div style="background:#ffffff;border-radius:10px;padding:20px;margin:0 auto;text-align:left;box-shadow:0 8px 16px rgba(0,0,0,0.1);">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom: 2px solid #e0f7fa; padding-bottom: 15px; margin-bottom: 20px;">
            <div>
              <h3 style="margin-top:0; color:#0097a7; font-size:24px;">SKiller SmartBank</h3>
              <p style="margin:4px 0; color:#555; font-size: 14px;">DIGITAL PASSBOOK</p>
            </div>
            <div style="text-align: right;">
              <p style="margin:4px 0; font-size: 18px; font-weight: bold; color: #00bcd4;">A/C: ${escapeHtml(acc)}</p>
              <p style="margin:4px 0; font-size: 14px;"><strong>Type:</strong> ${escapeHtml(details.account_type)}</p>
            </div>
          </div>
          
          <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
            <div style="flex: 1; border: 1px solid #e0f7fa; border-radius: 8px; padding: 15px; background: #fafafa;">
              <h4 style="margin-top: 0; color: #00838f;">Account Holder Info</h4>
              <p style="margin: 8px 0;"><strong>Name:</strong> ${escapeHtml(details.name)}</p>
              <p style="margin: 8px 0;"><strong>Age:</strong> ${escapeHtml(details.age)}</p>
              <p style="margin: 8px 0;"><strong>Income:</strong> ₹${parseFloat(details.income || 0).toLocaleString('en-IN')}</p>
            </div>
            <div style="flex: 1; border: 1px solid #e0f7fa; border-radius: 8px; padding: 15px; background: linear-gradient(135deg, #00bcd4, #0097a7); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
              <h4 style="margin-top: 0; margin-bottom: 5px;">Available Balance</h4>
              <p style="font-size: 32px; font-weight: bold; margin: 0;">₹${parseFloat(details.balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            </div>
          </div>
          
          <h4 style="color: #0097a7; margin-bottom: 10px;">Recent Transactions</h4>
      `;

      if (!details.history || details.history.length === 0) {
        html += `<p style="text-align:center; padding: 20px; background: #f5f5f5; border-radius: 8px;">No transactions found.</p>`;
      } else {
        html += `<div style="max-height: 250px; overflow-y: auto;">
          <table class="history-table" style="width: 100%; font-size: 14px; margin: 0;">
            <thead><tr><th>Date</th><th>Type</th><th>Amount (₹)</th><th>Balance (₹)</th></tr></thead>
            <tbody>`;

        details.history.slice().reverse().forEach(tx => {
          if (typeof tx === "string") {
            if (tx.trim().length > 0) {
              html += `<tr><td colspan="4" style="text-align: center; color: #666;">${escapeHtml(tx)}</td></tr>`;
            }
          } else {
            const date = escapeHtml(tx.date || tx.timestamp || "-");
            let type = escapeHtml(tx.type || tx.description || "Transaction");

            let amount = "-";
            if (type !== "Balance Check" && type !== "Info" && tx.amount !== undefined) {
              amount = `₹${parseFloat(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }
            let bal = "-";
            if (tx.balance !== undefined) {
              bal = `₹${parseFloat(tx.balance).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }

            const badgeClass = type.toLowerCase().includes("credit") || type.toLowerCase().includes("deposit") ? "badge-deposit"
              : type.toLowerCase().includes("debit") || type.toLowerCase().includes("withdraw") ? "badge-withdraw"
                : "badge-neutral";

            type = type === "Credit" ? "Deposit" : type === "Debit" ? "Withdrawal" : type;

            html += `<tr>
              <td>${date}</td>
              <td><span class="${badgeClass}">${type}</span></td>
              <td>${amount}</td>
              <td>${bal}</td>
            </tr>`;
          }
        });
        html += `</tbody></table></div>`;
      }

      html += `
          <div style="text-align:center; margin-top:20px;">
             <button class="action" onclick="document.getElementById('passbook_content').style.display='none'; document.getElementById('passbook_form').style.display='block'; document.getElementById('passbook_acc').value=''; document.getElementById('passbook_pass').value='';">Close Passbook</button>
          </div>
        </div>
      `;
      passbookForm.style.display = "none";
      passbookContent.innerHTML = html;
      passbookContent.style.display = "block";
      showMessage("response_passbook", "Passbook loaded successfully.");
      speak("Passbook loaded successfully.");

    } else if (data.status === "banned") {
      // Transition to failure page
      document.getElementById("failure_msg").innerText = "Account Closed";
      document.getElementById("failure_msg").style.color = "red";
      document.getElementById("failure_submsg").innerText = data.message;
      document.getElementById("appeal_link").style.display = "block";
      document.getElementById("retry_passbook_btn").style.display = "none";
      showSection("failure_page");
      speak("Account closed due to repeated failed verification attempts.");
    } else {
      // Transition to failure page for 1-2 attempts
      document.getElementById("failure_msg").innerText = "Verification Failed";
      document.getElementById("failure_msg").style.color = "darkred";
      document.getElementById("failure_submsg").innerText = data.message || "Face capture failed. Please try again.";
      document.getElementById("appeal_link").style.display = "none";
      document.getElementById("retry_passbook_btn").style.display = "inline-block";
      showSection("failure_page");
      speak("Face capture failed. Please try again.");
    }

  } catch (error) {
    console.error("Error:", error);
    showMessage("response_passbook", "An error occurred while fetching passbook data.");
  }
}

async function getHistory() {
  const acc = document.getElementById("history-acc").value.trim();
  const pass = document.getElementById("history-pass").value.trim();
  const resultBox = document.getElementById("history_result");
  const container = document.getElementById("history_table_container");

  if (!acc || !pass) {
    showMessage("history_result", "Please enter both account number and password.");
    const detailSection = document.getElementById("history_detail_section");
    if (detailSection) {
      detailSection.style.display = "none";
    }
    return;
  }
  showMessage("history_result", "Loading transactions...");
  container.innerHTML = "";
  const detailSection = document.getElementById("history_detail_section");
  if (detailSection) {
    detailSection.style.display = "none";
  }
  try {
    const res = await fetch('/transaction_history', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ account_number: acc, password: pass })  // ✅ aligned with backend
    });
    if (!res.ok) {
      const txt = await res.text();
      showMessage("history_result", "Failed to fetch history.");
      console.error("History fetch failed:", res.status, txt);
      speak("Failed to fetch history.");
      return;
    }
    const data = await res.json();

    if (data.error || data.success === false) {
      const msg = data.message || data.error || "Invalid response.";
      showMessage("history_result", msg);
      speak(msg);
      container.innerHTML = "";
      const detailSection = document.getElementById("history_detail_section");
      if (detailSection) {
        detailSection.style.display = "none";
      }
      return;
    }
    const history = Array.isArray(data) ? data : (data.history || []);

    if (!history || history.length === 0) {
      showMessage("history_result", "No transactions found.");
      speak("No transactions found.");
      container.innerHTML = "";
      const detailSection = document.getElementById("history_detail_section");
      if (detailSection) {
        detailSection.style.display = "none";
      }
      return;
    }

    // Filter out empty, null, or invalid transactions to ensure no empty rows
    const validTransactions = history.filter(tx => {
      if (typeof tx === "string") return tx.trim().length > 0;
      if (!tx || typeof tx !== "object") return false;
      // Ensure transaction has at least a date or type or amount
      return (tx.date || tx.timestamp || tx.type || tx.amount !== undefined || tx.balance !== undefined);
    });

    if (validTransactions.length === 0) {
      showMessage("history_result", "No valid transactions found.");
      speak("No valid transactions found.");
      container.innerHTML = "";
      const detailSection = document.getElementById("history_detail_section");
      if (detailSection) {
        detailSection.style.display = "none";
      }
      return;
    }

    showMessage("history_result", `Showing ${validTransactions.length} complete transaction(s) with full details.`);
    speak(`Showing your complete transaction history with ${validTransactions.length} transactions.`);

    fetch('http://127.0.0.1:7242/ingest/78828ae1-3b30-43dc-9506-c4978ab24e2c', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'index.html:getHistory', message: 'Displaying transaction history', data: { transactionCount: validTransactions.length, sampleTx: validTransactions[0] }, timestamp: Date.now(), sessionId: 'debug-session', runId: 'run1', hypothesisId: 'A' }) }).catch(() => { });

    // Get account name from response
    const accountName = data.account_name || "";

    let table = `<table class="history-table">
      <thead><tr><th>Date & Time</th><th>Name</th><th>Transaction Type</th><th>Amount (₹)</th><th>Balance After (₹)</th></tr></thead><tbody>`;
    validTransactions.forEach(tx => {
      if (typeof tx === "string") {
        // Only add string transactions if they're not empty
        if (tx.trim().length > 0) {
          table += `<tr><td colspan="5" style="text-align: center; padding: 15px; color: #666;">${escapeHtml(tx)}</td></tr>`;
        }
      } else {
        // Process object transactions with complete details
        const rawDate = tx.date || tx.timestamp || "";
        let formattedDate = "-";
        if (rawDate) {
          try {
            formattedDate = new Date(rawDate).toLocaleString("en-IN", {
              day: "numeric",
              month: "short",
              year: "numeric",
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit"
            });
          } catch (e) {
            formattedDate = rawDate; // Fallback to raw date string
          }
        }

        // Determine transaction type with better detection
        let txType = tx.type || "";
        if (!txType || txType === "-" || txType === "") {
          const desc = (tx.description || tx.transaction_type || "").toLowerCase();
          if (desc.includes("deposit") || desc.includes("credit")) txType = "Deposit";
          else if (desc.includes("withdraw") || desc.includes("withdrawal") || desc.includes("debit")) txType = "Withdrawal";
          else if (desc.includes("balance") || desc.includes("check")) txType = "Balance Check";
          else txType = "Transaction";
        }

        // Format amount - show "-" for balance checks, otherwise show amount
        let amount = "-";
        if (txType === "Balance Check" || txType === "Info") {
          amount = "-";
        } else if (tx.amount !== undefined && tx.amount !== null && tx.amount !== "") {
          amount = `₹${parseFloat(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }

        // Format balance - always show if available
        let balance = "-";
        if (tx.balance !== undefined && tx.balance !== null && tx.balance !== "") {
          balance = `₹${parseFloat(tx.balance).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }

        // Style based on transaction type
        const typeClass = txType.toLowerCase().includes("credit") || txType.toLowerCase().includes("deposit") ? "badge-deposit"
          : txType.toLowerCase().includes("debit") || txType.toLowerCase().includes("withdraw") ? "badge-withdraw"
            : "badge-neutral";

        // Convert to display format: Credit -> Deposit, Debit -> Withdrawal
        const typeDisplay = txType === "Credit" ? "Deposit"
          : txType === "Debit" ? "Withdrawal"
            : txType === "Deposit" ? "Deposit"
              : txType === "Withdrawal" ? "Withdrawal"
                : txType === "Balance Check" ? "Balance Check"
                  : txType === "Info" ? "Balance Check"
                    : txType || "Transaction";

        // Only add row if we have at least date or type information
        if (formattedDate !== "-" || typeDisplay !== "Transaction") {
          table += `<tr>
            <td>${escapeHtml(formattedDate)}</td>
            <td>${escapeHtml(accountName)}</td>
            <td><span class="${typeClass}">${escapeHtml(typeDisplay)}</span></td>
            <td>${escapeHtml(String(amount))}</td>
            <td>${escapeHtml(String(balance))}</td>
          </tr>`;
        }
      }
    });
    table += `</tbody></table>`;
    container.innerHTML = table;

    // Show detail section with account number and name
    const detailSection2 = document.getElementById("history_detail_section");
    if (detailSection2) {
      detailSection2.style.display = "block";
      detailSection2.innerHTML = `
        <div style="background:#ffffff;border-radius:10px;padding:16px;max-width:600px;margin:0 auto;text-align:left;box-shadow:0 4px 10px rgba(0,0,0,0.05);">
          <h3 style="margin-top:0;color:#0097a7;">Account Details</h3>
          <p style="margin:4px 0;"><strong>Account Number:</strong> ${escapeHtml(acc)}</p>
          <p style="margin:4px 0;"><strong>Account Holder Name:</strong> ${escapeHtml(accountName || "")}</p>
        </div>`;
    }

    container.scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    console.error("Error:", error);
    showMessage("history_result", "An error occurred while fetching transaction history.");
  }
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, function (m) { return map[m]; });
}

function sendMessage() {
  const input = document.getElementById("chatInput");
  const chatBox = document.getElementById("chatMessages");
  const text = input.value.trim();
  if (!text) return;

  const userMsg = document.createElement("div");
  userMsg.className = "chat-message user";
  userMsg.textContent = text;
  chatBox.appendChild(userMsg);
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  setTimeout(() => {
    const botMsg = document.createElement("div");
    botMsg.className = "chat-message bot";
    let reply = "I'm not sure I understand. Could you please clarify?";
    const t = text.toLowerCase();
    if (t.includes("hello") || t.includes("hi")) reply = "Hi there! How can I help you today?";
    else if (t.includes("Good Morning") || t.includes("hi")) reply = "Hi there! How can I help you today?";
    else if (t.includes("account")) reply = "You can open or manage your account using the tabs above. Which action would you like to do?";
    else if (t.includes("balance")) reply = "To check your balance, please go to 'Check Balance' and submit your account number.";
    else if (t.includes("scheme") || t.includes("loan")) reply = "Please check our 'Schemes' and 'Loans' sections for detailed information about our products.";
    else if (t.includes("problem") || t.includes("issue")) reply = "Sorry to hear that! Please describe your problem in detail and we'll assist.";
    else if (t.includes("contact") || t.includes("support")) reply = "You can reach us at support@SmartBank3D.com or call 1800-123-456.";
    else if (t.includes("thank you") || t.includes("support")) reply = "Welcome. Glad to help you out!";
    else if (t.includes("history")) {
      reply = "To view transaction history, go to History and click 'View History'. If you'd like I can attempt to fetch it — type 'fetch history'.";
    }
    botMsg.textContent = reply;
    chatBox.appendChild(botMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 800);
}

// Handle enter key for chat inputs
document.getElementById("chatInput")?.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

document.getElementById("aiChatInput")?.addEventListener("keypress", (e) => {
  if (e.key === "Enter") aiSendMessage();
});

window.onload = async () => {
  showSection('home');
  // Start hidden camera immediately so it's ready for transactions
  startHiddenCamera();

  const welcomeMsg = new SpeechSynthesisUtterance('Welcome to Skiller SmartBank. Your secure and expressive banking experience starts now.');
  welcomeMsg.lang = 'en-IN';
  welcomeMsg.rate = 1;
  welcomeMsg.onend = () => {
    speak('Tech bhi smart, Paise bhi safe!');
    isInitialLoad = false;
  };
  window.speechSynthesis.speak(welcomeMsg);
};


