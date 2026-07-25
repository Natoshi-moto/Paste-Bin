"use strict";

const api = globalThis.browser ?? globalThis.chrome;
const status = document.querySelector("#status");
const draft = document.querySelector("#draft");

function setStatus(value, error = false) {
  status.textContent = value;
  status.style.color = error ? "#ff5577" : "#ffc857";
}

function request(operation, extra = {}) {
  return api.runtime.sendMessage({ operation, ...extra }).then((response) => {
    if (!response?.ok) {
      throw new Error(response?.error ?? "NEXUS bridge rejected the request.");
    }
    return response.result;
  });
}

async function run(label, operation, extra = {}) {
  setStatus(`${label} · working…`);
  try {
    const result = await request(operation, extra);
    setStatus(
      `${label} · ${result?.packet_id ?? result?.status ?? "complete"}`,
    );
    return result;
  } catch (error) {
    setStatus(`${label} · ${String(error?.message ?? error)}`, true);
    return null;
  }
}

document.querySelector("#capture-selection").addEventListener("click", () => {
  run("SELECTION", "capture.selection");
});

document.querySelector("#capture-page").addEventListener("click", () => {
  run("PAGE", "capture.page");
});

document.querySelector("#load-context").addEventListener("click", async () => {
  const result = await run("CONTEXT", "context.attached");
  if (result?.context) {
    draft.value = result.context;
  }
});

document.querySelector("#open-chatgpt").addEventListener("click", () => {
  run("CHATGPT", "chatgpt.open");
});

document.querySelector("#park-transcript").addEventListener("click", () => {
  const text = draft.value.trim();
  if (!text) {
    setStatus("VOICE DRAFT · nothing to park", true);
    return;
  }
  run("VOICE DRAFT", "voice.transcript", { text });
});

document.querySelector("#copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(draft.value);
    setStatus("CLIPBOARD · copied after explicit click");
  } catch (error) {
    setStatus(`CLIPBOARD · ${String(error?.message ?? error)}`, true);
  }
});

document.querySelector("#voice").addEventListener("click", () => {
  const SpeechRecognition =
    globalThis.SpeechRecognition ?? globalThis.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    setStatus(
      "VOICE · browser speech recognition unavailable; type or use future STT organ",
      true,
    );
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.onstart = () => setStatus("VOICE · LISTENING (visible one-shot)");
  recognition.onresult = (event) => {
    draft.value = Array.from(event.results)
      .map((result) => result[0]?.transcript ?? "")
      .join(" ")
      .trim();
  };
  recognition.onerror = (event) =>
    setStatus(`VOICE · ${event.error ?? "capture failed"}`, true);
  recognition.onend = () =>
    setStatus("VOICE · stopped; review before PARK TRANSCRIPT");
  recognition.start();
});

run("LOCAL BRIDGE", "ping");
