(function () {
  "use strict";

  if (window.__salespilotWidgetLoaded) {
    return;
  }
  window.__salespilotWidgetLoaded = true;

  var script = document.currentScript;
  var prefix = "salespilot-widget-";

  function trimSlash(value) {
    return String(value || "").trim().replace(/\/+$/, "");
  }

  function getScriptOrigin() {
    try {
      return new URL(script && script.src ? script.src : window.location.href).origin;
    } catch (error) {
      return window.location.origin;
    }
  }

  function normalizeBaseUrl(value) {
    var raw = trimSlash(value) || getScriptOrigin();
    try {
      return new URL(raw, window.location.href).origin;
    } catch (error) {
      return getScriptOrigin();
    }
  }

  function toHostname(value) {
    var raw = String(value || "").trim().toLowerCase();
    if (!raw) return "";
    try {
      var parsed = raw.indexOf("://") >= 0 ? new URL(raw) : new URL("https://" + raw);
      return parsed.hostname;
    } catch (error) {
      return raw.split("/")[0].split(":")[0];
    }
  }

  function parseAllowedDomains(value) {
    var seen = {};
    return String(value || "")
      .split(/[,\s，;；]+/)
      .map(toHostname)
      .filter(function (host) {
        if (!host || seen[host]) return false;
        seen[host] = true;
        return true;
      });
  }

  function isAllowedHost(allowedDomains) {
    if (!allowedDomains.length) return true;
    return allowedDomains.indexOf(window.location.hostname.toLowerCase()) >= 0;
  }

  function normalizeBrandColor(value) {
    var color = String(value || "").trim();
    return /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(color) ? color : "#2563EB";
  }

  try {
    var apiBase = normalizeBaseUrl(script && script.getAttribute("data-api-base"));
    var apiOrigin = new URL(apiBase).origin;
    var position = script && script.getAttribute("data-position") === "left" ? "left" : "right";
    var brandColor = normalizeBrandColor(script && script.getAttribute("data-brand-color"));
    var allowedDomains = parseAllowedDomains(script && script.getAttribute("data-allowed-domains"));

    if (!isAllowedHost(allowedDomains)) {
      console.warn("[SalesPilot Widget] 当前域名不在允许嵌入域名中，客服组件未显示。");
      return;
    }

    var host = document.createElement("div");
    host.id = prefix + "root";
    document.body.appendChild(host);

    var root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;
    var style = document.createElement("style");
    style.textContent = [
      ":host{all:initial;font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;}",
      "." + prefix + "button{position:fixed;z-index:2147483000;bottom:24px;" + position + ":24px;display:flex;align-items:center;gap:8px;border:0;border-radius:999px;background:" + brandColor + ";color:#fff;padding:13px 18px;box-shadow:0 14px 34px rgba(15,23,42,.24);font-size:14px;font-weight:700;line-height:1;cursor:pointer;transition:transform .18s ease,box-shadow .18s ease,opacity .18s ease;}",
      "." + prefix + "button:hover{transform:translateY(-1px);box-shadow:0 18px 42px rgba(15,23,42,.30);opacity:.92;}",
      "." + prefix + "button svg{width:18px;height:18px;display:block;}",
      "." + prefix + "panel{position:fixed;z-index:2147483001;bottom:86px;" + position + ":24px;width:380px;height:620px;max-height:calc(100vh - 112px);border:1px solid rgba(148,163,184,.35);border-radius:20px;background:#fff;box-shadow:0 24px 64px rgba(15,23,42,.28);overflow:hidden;display:none;}",
      "." + prefix + "panel." + prefix + "open{display:block;}",
      "." + prefix + "close{position:absolute;right:14px;top:14px;z-index:2;width:34px;height:34px;border:1px solid " + brandColor + ";border-radius:999px;background:#fff;color:" + brandColor + ";display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 12px rgba(15,23,42,.08);transition:background .18s ease,opacity .18s ease;}",
      "." + prefix + "close:hover{background:#f8fafc;opacity:.82;}",
      "." + prefix + "close svg{width:16px;height:16px;}",
      "." + prefix + "iframe{width:100%;height:100%;border:0;display:block;background:#fff;}",
      "@media (max-width: 480px) {." + prefix + "button{bottom:16px;" + position + ":16px;padding:12px 15px;}." + prefix + "panel{bottom:76px;" + position + ":12px;width:calc(100vw - 24px);height:min(680px, calc(100vh - 92px));border-radius:18px;}}",
    ].join("\n");

    var button = document.createElement("button");
    button.className = prefix + "button";
    button.type = "button";
    button.setAttribute("aria-label", "打开在线咨询");
    button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 18.5V20a1 1 0 0 0 1.55.83L9.3 19H16a5 5 0 0 0 5-5V8a5 5 0 0 0-5-5H8a5 5 0 0 0-5 5v6a5 5 0 0 0 2 4.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 10h8M8 14h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>在线咨询</span>';

    var panel = document.createElement("div");
    panel.className = prefix + "panel";
    var closeButton = document.createElement("button");
    closeButton.className = prefix + "close";
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "关闭在线咨询");
    closeButton.innerHTML = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
    var iframe = document.createElement("iframe");
    iframe.className = prefix + "iframe";
    iframe.title = "在线咨询";
    iframe.src = apiBase + "/embed/chat";
    iframe.setAttribute("allow", "clipboard-write");
    panel.appendChild(closeButton);
    panel.appendChild(iframe);

    root.appendChild(style);
    root.appendChild(panel);
    root.appendChild(button);

    button.addEventListener("click", function () {
      panel.classList.toggle(prefix + "open");
    });

    closeButton.addEventListener("click", function () {
      panel.classList.remove(prefix + "open");
    });

    window.addEventListener("message", function (event) {
      if (event.origin !== apiOrigin) return;
      if (!iframe || !iframe.isConnected || !iframe.contentWindow) return;
      if (event.source !== iframe.contentWindow) return;
      if (event.data !== "salespilot:close") return;
      panel.classList.remove(prefix + "open");
    });
  } catch (error) {
    window.__salespilotWidgetLoaded = false;
    console.warn("[SalesPilot Widget] 客服组件加载失败。");
  }
})();
