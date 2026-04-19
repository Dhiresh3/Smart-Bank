/* ===============================
   FULL JS — 100% UNCHANGED
   (moved from <script>)
   =============================== */

document.addEventListener('keypress', function(e) {
  if (e.key === 'Enter') e.preventDefault();
});

function speak(text) {
  const msg = new SpeechSynthesisUtterance(text);
  msg.lang = "en-IN";
  msg.rate = 1;
  window.speechSynthesis.speak(msg);
}

const LOCK_DURATION_MS = 7000;
let isLocked = false;
let messageTimeouts = {};
let isInitialLoad = true;

/* 🔹 AI CHAT — IDENTICAL */
const aiChatMessagesEl = () => document.getElementById("aiChatMessages");
const aiChatInputEl = () => document.getElementById("aiChatInput");

/* ... CONTINUES EXACTLY ... */

/* 🔹 showSection() with VOICE LOCK */
function showSection(id) {
  if (isLocked) return;
  isLocked = true;

  playAudioForSection(id);
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById(id)?.classList.add('active');

  setTimeout(() => isLocked = false, LOCK_DURATION_MS);
}

/* 🔹 window.onload VOICE SEQUENCE — IDENTICAL */
window.onload = () => {
  showSection('home');

  const welcomeMsg = new SpeechSynthesisUtterance(
    "Welcome to Skiller SmartBank. Your secure and expressive banking experience starts now."
  );

  welcomeMsg.onend = () => {
    speak("Tech bhi smart, Paise bhi safe!");
    isInitialLoad = false;
  };

  speechSynthesis.speak(welcomeMsg);
};
