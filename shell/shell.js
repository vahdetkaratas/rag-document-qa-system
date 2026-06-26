(function () {
  var year = document.getElementById("shellYear");
  if (year) {
    year.textContent = new Date().getFullYear();
  }

  var btn = document.querySelector(".art-info-bar-btn");
  var bar = document.querySelector(".art-info-bar");
  var curtain = document.getElementById("shellMobileCurtain");
  if (!btn || !bar) return;

  function setOpen(open) {
    bar.classList.toggle("art-active", open);
    btn.classList.toggle("art-active", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (curtain) {
      curtain.classList.toggle("is-open", open);
      curtain.setAttribute("aria-hidden", open ? "false" : "true");
    }
  }

  btn.addEventListener("click", function () {
    setOpen(!bar.classList.contains("art-active"));
  });

  if (curtain) {
    curtain.addEventListener("click", function () {
      setOpen(false);
    });
  }
})();

(function () {
  var demoRoot = document.getElementById("projDemo");
  var q = document.getElementById("demoQuestion");
  var askBtn = document.getElementById("demoAskBtn");
  var statusEl = document.getElementById("demoStatus");
  var progressEl = document.getElementById("demoProgress");
  var wrap = document.getElementById("demoAnswerWrap");
  var ans = document.getElementById("demoAnswer");
  var srcList = document.getElementById("demoSources");
  var ctxDetails = document.getElementById("demoContextDetails");
  var ctxExcerpt = document.getElementById("demoContextExcerpt");
  var ctxMeta = document.getElementById("demoContextMeta");
  if (!askBtn || !q) return;

  function askUrl() {
    var askMeta = document.querySelector('meta[name="rag-api-ask"]');
    var askRaw = askMeta && askMeta.getAttribute("content");
    if (askRaw && askRaw.trim()) return askRaw.trim();

    var originMeta = document.querySelector('meta[name="rag-api-origin"]');
    var originRaw = originMeta && originMeta.getAttribute("content");
    var fromMeta = originRaw && originRaw.trim() ? originRaw.trim().replace(/\/$/, "") : "";

    if (window.location.protocol === "file:") {
      return fromMeta ? fromMeta + "/ask" : "http://127.0.0.1:8000/ask";
    }

    var host = (window.location.hostname || "").toLowerCase();
    var isLocal =
      host === "localhost" ||
      host === "127.0.0.1" ||
      host === "[::1]" ||
      host.endsWith(".localhost");

    if (isLocal) {
      return window.location.origin + "/ask";
    }

    if (fromMeta) {
      try {
        var metaHost = new URL(fromMeta).hostname.toLowerCase();
        if (metaHost === host) {
          return window.location.origin + "/ask";
        }
      } catch (e) {
        /* use meta below */
      }
      return fromMeta + "/ask";
    }

    return "https://rag-qa.vahdetkaratas.com/ask";
  }

  if (progressEl) progressEl.hidden = true;
  if (wrap) wrap.hidden = true;
  if (statusEl) {
    statusEl.textContent = "";
    statusEl.classList.remove("is-error");
  }
  if (demoRoot) demoRoot.setAttribute("aria-busy", "false");

  function resetContextDetails() {
    if (!ctxDetails || !ctxExcerpt || !ctxMeta) return;
    ctxDetails.hidden = true;
    ctxDetails.open = false;
    ctxExcerpt.textContent = "";
    ctxMeta.textContent = "";
  }

  function fillContextDetails(chunks) {
    if (!ctxDetails || !ctxExcerpt || !ctxMeta) return;
    if (!chunks || !chunks.length) {
      resetContextDetails();
      return;
    }
    var first = chunks[0];
    var text = first && first.text ? String(first.text) : "";
    if (!text.trim()) {
      resetContextDetails();
      return;
    }
    var maxLen = 900;
    var excerpt = text.length > maxLen ? text.slice(0, maxLen) + "\n..." : text;
    ctxExcerpt.textContent = excerpt;
    var parts = [];
    if (first.document_name) parts.push(first.document_name);
    if (first.page_number != null) parts.push("page " + first.page_number);
    if (first.score != null && first.score !== "") {
      parts.push("score " + Number(first.score).toFixed(4));
    }
    ctxMeta.textContent = parts.length ? "First retrieved row: " + parts.join(" | ") : "First retrieved row (API payload).";
    ctxDetails.hidden = false;
  }

  document.querySelectorAll(".proj-example-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      q.value = chip.getAttribute("data-q") || "";
      q.focus();
    });
  });

  function setLoading(on) {
    askBtn.disabled = on;
    askBtn.setAttribute("aria-busy", on ? "true" : "false");
    q.disabled = on;
    if (demoRoot) demoRoot.setAttribute("aria-busy", on ? "true" : "false");
    if (progressEl) progressEl.hidden = !on;
    if (on) {
      statusEl.textContent = "";
      statusEl.classList.remove("is-error");
    }
  }

  function buildSourceCard(s) {
    var doc = s.document || "-";
    var page = s.page != null ? String(s.page) : "-";
    var cid = s.chunk_id || "-";
    var art = document.createElement("article");
    art.className = "proj-source-card";
    art.setAttribute("aria-label", "Evidence: " + doc);
    var title = document.createElement("div");
    title.className = "proj-source-doc";
    title.textContent = doc;
    var meta = document.createElement("dl");
    meta.className = "proj-source-meta";
    function row(dt, dd) {
      var ddt = document.createElement("dt");
      ddt.textContent = dt;
      var ddd = document.createElement("dd");
      ddd.textContent = dd;
      meta.appendChild(ddt);
      meta.appendChild(ddd);
    }
    row("Page", page);
    row("Chunk ID", cid);
    art.appendChild(title);
    art.appendChild(meta);
    return art;
  }

  askBtn.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    var text = (q.value || "").trim();
    statusEl.textContent = "";
    statusEl.classList.remove("is-error");
    wrap.hidden = true;
    ans.textContent = "";
    srcList.innerHTML = "";
    resetContextDetails();
    if (!text) {
      statusEl.textContent = "Enter a question or choose an example above.";
      statusEl.classList.add("is-error");
      return;
    }
    setLoading(true);
    fetch(askUrl(), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text }),
      mode: "cors",
      credentials: "omit",
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, status: res.status, data: data };
        });
      })
      .then(function (r) {
        setLoading(false);
        if (!r.ok) {
          var detail = r.data && (r.data.detail !== undefined ? r.data.detail : r.data);
          statusEl.textContent = "HTTP " + r.status + (detail ? ": " + JSON.stringify(detail) : "");
          statusEl.classList.add("is-error");
          return;
        }
        if (typeof r.data.answer !== "string") {
          statusEl.textContent = "Unexpected response shape.";
          statusEl.classList.add("is-error");
          return;
        }
        ans.textContent = r.data.answer;
        var sources = r.data.sources || [];
        sources.forEach(function (s) {
          srcList.appendChild(buildSourceCard(s));
        });
        if (sources.length === 0) {
          var empty = document.createElement("p");
          empty.className = "proj-sources-empty";
          empty.textContent = "No source list returned for this answer.";
          srcList.appendChild(empty);
        }
        fillContextDetails(r.data.retrieved_chunks);
        wrap.hidden = false;
        statusEl.textContent = "Response received.";
        try {
          wrap.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (err) {
          wrap.scrollIntoView(true);
        }
      })
      .catch(function (err) {
        setLoading(false);
        statusEl.classList.add("is-error");
        statusEl.textContent =
          "Request failed (often CORS). On the API server set CORS_ORIGINS to this page origin." +
          (err.message ? " " + err.message : "");
      });
  });
})();
