// Small progressive enhancements. Every page works without this file.
(() => {
  "use strict";

  // Load the YouTube player only when someone asks for it, so the page stays light
  // and no third-party request happens on load.
  for (const button of document.querySelectorAll("[data-youtube]")) {
    button.addEventListener("click", () => {
      const id = button.getAttribute("data-youtube");
      const iframe = document.createElement("iframe");
      iframe.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?autoplay=1&rel=0`;
      iframe.title = button.getAttribute("aria-label") || "Video";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      iframe.allowFullscreen = true;
      button.replaceChildren(iframe);
      button.removeAttribute("aria-label");
      button.style.cursor = "default";
    }, { once: true });
  }

  // Section dots: mark the last section heading above 40% of the viewport.
  // Computed on scroll rather than with an observer, so jumps and fast scrolls stay correct.
  const dots = [...document.querySelectorAll(".dots a[href^='#']")];
  const sections = dots
    .map((a) => document.getElementById(a.hash.slice(1)))
    .filter(Boolean);
  const markSection = () => {
    const line = window.innerHeight * 0.4;
    let current = null;
    for (const s of sections) if (s.getBoundingClientRect().top <= line) current = s;
    for (const a of dots) {
      const active = current !== null && a.hash === `#${current.id}`;
      a.classList.toggle("is-active", active);
      if (active) a.setAttribute("aria-current", "location");
      else a.removeAttribute("aria-current");
    }
  };

  // Reading progress along the top edge.
  const bar = document.querySelector(".progress");
  if (bar) {
    let queued = false;
    const update = () => {
      queued = false;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? Math.min(1, window.scrollY / max) : 0})`;
    };
    window.addEventListener("scroll", () => {
      if (!queued) { queued = true; requestAnimationFrame(() => { update(); markSection(); }); }
    }, { passive: true });
    update();
  }
  if (!bar) window.addEventListener("scroll", markSection, { passive: true });
  window.addEventListener("resize", markSection);
  markSection();

  // Minimal Cypher highlighting. Works on text only, so nothing in the source is
  // ever interpreted as HTML.
  const KEYWORDS = /\b(MATCH|OPTIONAL|WHERE|WITH|RETURN|ORDER|BY|DESC|ASC|LIMIT|MERGE|CREATE|SET|DELETE|DETACH|UNWIND|AS|AND|OR|NOT|IN|IS|NULL|CALL|YIELD|ON|DISTINCT|FOREACH|CASE|WHEN|THEN|ELSE|END|count|size|any|toLower|CONTAINS|INDEX|FOR|VECTOR|FULLTEXT|OPTIONS|true|false)\b/;
  const TOKEN = new RegExp([
    "(\\/\\/[^\\n]*)",                 // comment
    "('(?:[^'\\\\]|\\\\.)*')",         // string
    "(\\$[A-Za-z_]\\w*)",              // parameter
    "(:[A-Z][A-Za-z_]*(?=[\\s){|]))",  // label like :Memory
    "(\\[[a-z]*:[A-Z_]+[^\\]]*\\])",   // relationship like [:SHARED_IN {active:true}]
    "(\\b\\d+(?:\\.\\d+)?\\b)",        // number
    `(${KEYWORDS.source})`,
  ].join("|"), "g");

  const span = (cls, text) => {
    const el = document.createElement("span");
    el.className = cls;
    el.textContent = text;
    return el;
  };

  for (const code of document.querySelectorAll("code.language-cypher")) {
    const source = code.textContent;
    const out = document.createDocumentFragment();
    let last = 0;
    for (const m of source.matchAll(TOKEN)) {
      if (m.index > last) out.append(source.slice(last, m.index));
      const [text, com, str, param, label, rel, num] = m;
      if (com) out.append(span("tok-com", text));
      else if (str) out.append(span("tok-str", text));
      else if (param) out.append(span("tok-param", text));
      else if (label) out.append(span("tok-label", text));
      else if (rel) out.append(span("tok-rel", text));
      else if (num) out.append(span("tok-num", text));
      else out.append(span("tok-kw", text));
      last = m.index + text.length;
    }
    out.append(source.slice(last));
    code.replaceChildren(out);
  }
})();
