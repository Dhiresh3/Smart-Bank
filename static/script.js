/* ═══════════════════════════════════════════════════════
   WildLens AI — Frontend Logic
   Handles drag-drop, file path input, API calls, and
   animated chart rendering.
   ═══════════════════════════════════════════════════════ */

const dropZone        = document.getElementById("drop-zone");
const dropContent     = document.getElementById("drop-zone-content");
const previewImg      = document.getElementById("preview-img");
const fileInput       = document.getElementById("file-input");
const filepathInput   = document.getElementById("filepath-input");
const predictBtn      = document.getElementById("predict-btn");
const btnText         = document.querySelector(".btn-text");
const btnIcon         = document.querySelector(".btn-icon");
const btnLoading      = document.getElementById("btn-loading");
const clearBtn        = document.getElementById("clear-btn");
const resultsSection  = document.getElementById("results-section");
const animalNameEl    = document.getElementById("animal-name");
const ringFill        = document.getElementById("ring-fill");
const ringText        = document.getElementById("ring-text");
const chartContainer  = document.getElementById("chart-container");
const resultsGrid     = document.getElementById("results-grid");

let selectedFile = null;

// ─── Animal Emoji Map ───
const animalEmoji = {
    bear: "🐻", butterfly: "🦋", cat: "🐱", chicken: "🐔",
    cow: "🐄", deer: "🦌", dog: "🐶", dolphin: "🐬",
    elephant: "🐘", horse: "🐴", lion: "🦁", leopard: "🐆",
    monkey: "🐒", panda: "🐼", penguin: "🐧", sheep: "🐑",
    snake: "🐍", spider: "🕷️", squirrel: "🐿️", tiger: "🐯",
    whale: "🐋", wolf: "🐺", zebra: "🦓", cheetah: "🐆",
};

function getEmoji(name) {
    return animalEmoji[name.toLowerCase()] || "🐾";
}

// ─── Drag & Drop ───
dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
});

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
});

function handleFile(file) {
    if (!file.type.startsWith("image/")) {
        showError("Please select a valid image file.");
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImg.src = e.target.result;
        previewImg.classList.remove("hidden");
        dropContent.classList.add("hidden");
    };
    reader.readAsDataURL(file);
    predictBtn.disabled = false;
    filepathInput.value = "";
    removeError();
}

// ─── File Path Input ───
filepathInput.addEventListener("input", () => {
    if (filepathInput.value.trim()) {
        predictBtn.disabled = false;
        selectedFile = null;
        previewImg.classList.add("hidden");
        dropContent.classList.remove("hidden");
    } else if (!selectedFile) {
        predictBtn.disabled = true;
    }
    removeError();
});

// ─── Predict ───
predictBtn.addEventListener("click", async () => {
    const formData = new FormData();

    if (selectedFile) {
        formData.append("image", selectedFile);
    } else if (filepathInput.value.trim()) {
        formData.append("filepath", filepathInput.value.trim());
    } else {
        showError("Please upload an image or enter a file path.");
        return;
    }

    // Show loading state
    btnText.classList.add("hidden");
    btnIcon.classList.add("hidden");
    btnLoading.classList.remove("hidden");
    predictBtn.disabled = true;
    removeError();

    try {
        const resp = await fetch("/predict", { method: "POST", body: formData });
        const data = await resp.json();

        if (data.error) {
            if (data.unknown_image) {
                // Image is not a recognised animal — show a friendly warning banner
                showError(data.error, true);
            } else {
                showError(data.error);
            }
            resetButton();
            // Hide any old results
            resultsSection.classList.add("hidden");
            return;
        }

        // If image came from filepath, show preview
        if (data.image_url && !selectedFile) {
            previewImg.src = data.image_url;
            previewImg.classList.remove("hidden");
            dropContent.classList.add("hidden");
        }

        displayResults(data);
        clearBtn.classList.remove("hidden");

    } catch (err) {
        showError("Connection error. Is the server running?");
    }

    resetButton();
});

function resetButton() {
    btnText.classList.remove("hidden");
    btnIcon.classList.remove("hidden");
    btnLoading.classList.add("hidden");
    predictBtn.disabled = false;
}

// ─── Clear ───
clearBtn.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    filepathInput.value = "";
    previewImg.src = "";
    previewImg.classList.add("hidden");
    dropContent.classList.remove("hidden");
    resultsSection.classList.add("hidden");
    clearBtn.classList.add("hidden");
    predictBtn.disabled = true;
    removeError();
});

// ─── Display Results ───
function displayResults(data) {
    resultsSection.classList.remove("hidden");

    // Scroll results into view on mobile
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);

    // ── Top prediction ──
    const emoji = getEmoji(data.prediction);
    animalNameEl.textContent = `${emoji} ${data.prediction}`;
    animalNameEl.style.animation = "none";
    animalNameEl.offsetHeight; // trigger reflow
    animalNameEl.style.animation = "scaleIn 0.5s ease-out";

    // ── Confidence ring ──
    const circumference = 2 * Math.PI * 45; // r=45
    const offset = circumference - (data.confidence / 100) * circumference;
    ringFill.style.strokeDasharray = circumference;
    ringFill.style.strokeDashoffset = circumference;

    // Color based on confidence
    if (data.confidence >= 70) {
        ringFill.style.stroke = "#3ddc84";
    } else if (data.confidence >= 40) {
        ringFill.style.stroke = "#ffa726";
    } else {
        ringFill.style.stroke = "#ef5350";
    }

    setTimeout(() => {
        ringFill.style.strokeDashoffset = offset;
    }, 100);

    // Animate ring text
    animateCounter(ringText, 0, data.confidence, 1200);

    // ── Top 5 Chart ──
    chartContainer.innerHTML = "";
    data.top5.forEach((item, i) => {
        const row = document.createElement("div");
        row.className = "chart-bar-row";
        row.style.animation = `fadeSlideUp 0.5s ease-out ${i * 0.1}s both`;

        const maxConf = data.top5[0].confidence;
        const barWidth = maxConf > 0 ? (item.confidence / maxConf) * 100 : 0;

        row.innerHTML = `
            <span class="chart-label">${getEmoji(item.class)} ${item.class}</span>
            <div class="chart-bar-wrap">
                <div class="chart-bar-fill rank-${i + 1}" style="width: 0%"></div>
            </div>
            <span class="chart-value">${item.confidence.toFixed(1)}%</span>
        `;
        chartContainer.appendChild(row);

        // Animate bar width
        setTimeout(() => {
            row.querySelector(".chart-bar-fill").style.width = `${barWidth}%`;
        }, 200 + i * 100);
    });

    // ── All Classes Grid ──
    resultsGrid.innerHTML = "";
    data.all.forEach((item) => {
        const card = document.createElement("div");
        card.className = `result-card${item.class === data.prediction ? " top-match" : ""}`;
        card.innerHTML = `
            <div class="class-name">${getEmoji(item.class)} ${item.class}</div>
            <div class="class-conf">${item.confidence.toFixed(2)}%</div>
        `;
        resultsGrid.appendChild(card);
    });

    // Speak the prediction automatically
    speakPrediction(data.prediction, data.confidence);
}

// ─── Voice / Text-to-Speech ───
function speakPrediction(animalName, confidence) {
    if (!('speechSynthesis' in window)) return; // Browser doesn't support TTS
    
    // Stop any currently speaking voice
    window.speechSynthesis.cancel();
    
    const text = `The predicted animal is ${animalName}, with ${confidence.toFixed(1)} percent confidence.`;
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Tweaks to make it sound natural
    utterance.rate = 0.95;
    
    window.speechSynthesis.speak(utterance);
}

// ─── Counter Animation ───
function animateCounter(el, from, to, duration) {
    const start = performance.now();
    function step(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        const current = from + (to - from) * eased;
        el.textContent = `${current.toFixed(1)}%`;
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// ─── Error Handling ───
/**
 * showError(msg, isUnknown)
 *  isUnknown = true  → amber "unrecognised image" banner
 *  isUnknown = false → standard red error
 */
function showError(msg, isUnknown = false) {
    removeError();
    const div = document.createElement("div");
    div.id = "error-msg";

    if (isUnknown) {
        div.className = "error-msg error-unknown";
        div.innerHTML = `
            <span class="error-icon">🚫</span>
            <div class="error-body">
                <strong>Unrecognised Image</strong>
                <p>${msg}</p>
            </div>`;
    } else {
        div.className = "error-msg";
        div.textContent = `⚠️ ${msg}`;
    }

    document.getElementById("upload-section").appendChild(div);
}

function removeError() {
    const el = document.getElementById("error-msg");
    if (el) el.remove();
}
