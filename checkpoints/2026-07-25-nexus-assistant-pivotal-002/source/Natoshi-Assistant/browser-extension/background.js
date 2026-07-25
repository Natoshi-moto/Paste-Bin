"use strict";

const firefoxApi = globalThis.browser;
const api = firefoxApi ?? globalThis.chrome;
const HOST_NAME = "org.nexus_assistant.browser";

function sendNative(message) {
  if (firefoxApi) {
    return firefoxApi.runtime.sendNativeMessage(HOST_NAME, message);
  }
  return new Promise((resolve, reject) => {
    api.runtime.sendNativeMessage(HOST_NAME, message, (response) => {
      const error = api.runtime.lastError;
      if (error) {
        reject(new Error(error.message));
        return;
      }
      resolve(response);
    });
  });
}

function currentTab() {
  return api.tabs.query({ active: true, currentWindow: true }).then(
    (tabs) => tabs[0] ?? null,
  );
}

async function selectedText(tabId) {
  const results = await api.scripting.executeScript({
    target: { tabId },
    func: () => String(globalThis.getSelection?.() ?? "").slice(0, 20000),
  });
  return String(results?.[0]?.result ?? "");
}

async function visiblePageExcerpt(tabId) {
  const results = await api.scripting.executeScript({
    target: { tabId },
    func: () => String(document.body?.innerText ?? "").slice(0, 50000),
  });
  return String(results?.[0]?.result ?? "");
}

async function captureSelectionFromTab(tab) {
  if (!tab?.id || !tab.url) {
    throw new Error("No active browser tab.");
  }
  const text = await selectedText(tab.id);
  if (!text.trim()) {
    throw new Error("Select text on the page first.");
  }
  return sendNative({
    schema: "nexus.browser.request/v1",
    operation: "capture.selection",
    title: tab.title ?? "Browser selection",
    url: tab.url,
    text,
  });
}

async function capturePageFromTab(tab) {
  if (!tab?.id || !tab.url) {
    throw new Error("No active browser tab.");
  }
  const text = await visiblePageExcerpt(tab.id);
  if (!text.trim()) {
    throw new Error("The active page has no readable text.");
  }
  return sendNative({
    schema: "nexus.browser.request/v1",
    operation: "capture.page",
    title: tab.title ?? "Browser page",
    url: tab.url,
    text,
  });
}

api.runtime.onInstalled.addListener(() => {
  api.contextMenus.create({
    id: "nexus-capture-selection",
    title: "Park selection in NEXUS Evidence",
    contexts: ["selection"],
  });
  api.contextMenus.create({
    id: "nexus-capture-page",
    title: "Park visible page excerpt in NEXUS Evidence",
    contexts: ["page"],
  });
});

api.contextMenus.onClicked.addListener((info, tab) => {
  const task =
    info.menuItemId === "nexus-capture-selection"
      ? captureSelectionFromTab(tab)
      : info.menuItemId === "nexus-capture-page"
        ? capturePageFromTab(tab)
        : null;
  task?.catch(() => undefined);
});

api.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  (async () => {
    if (!message || typeof message !== "object") {
      throw new Error("Malformed extension message.");
    }
    if (message.operation === "capture.selection") {
      return captureSelectionFromTab(await currentTab());
    }
    if (message.operation === "capture.page") {
      return capturePageFromTab(await currentTab());
    }
    if (message.operation === "voice.transcript") {
      return sendNative({
        schema: "nexus.browser.request/v1",
        operation: "voice.transcript",
        text: String(message.text ?? "").slice(0, 20000),
      });
    }
    if (message.operation === "context.attached") {
      return sendNative({
        schema: "nexus.browser.request/v1",
        operation: "context.attached",
      });
    }
    if (message.operation === "ping") {
      return sendNative({
        schema: "nexus.browser.request/v1",
        operation: "ping",
      });
    }
    if (message.operation === "chatgpt.open") {
      const tab = await api.tabs.create({ url: "https://chatgpt.com/" });
      return {
        status: "OPENED_AFTER_EXPLICIT_CLICK",
        tab_id: tab?.id ?? null,
      };
    }
    throw new Error("Unsupported extension operation.");
  })()
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) =>
      sendResponse({ ok: false, error: String(error?.message ?? error) }),
    );
  return true;
});
