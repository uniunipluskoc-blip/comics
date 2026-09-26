window.JM25FactorDuel = (function () {
  var MAX_BOMBS = 3;
  var MIN_TURNS = 5;
  var MAX_TURNS = 100;

  var running = false;
  var locked = false;
  var totalTurns = 10;
  var turn = 0;
  var bombs = 0;
  var question = null;
  var hand = [];
  var recent = [];
  var listeners = [];
  var drag = null;
  var dealing = false;
  var DEAL_STAGGER_MS = 130;
  var DEAL_FLY_MS = 480;

  function t(key) {
    return window.I18n && window.I18n.t ? window.I18n.t(key) : key;
  }

  function lang() {
    return window.I18n && window.I18n.lang === "zh" ? "zh" : "en";
  }

  function el(id) {
    return document.getElementById(id);
  }

  function bank() {
    if (typeof window.getJM25GameQuestions === "function") {
      return window.getJM25GameQuestions("all");
    }
    return [];
  }

  function pickQuestion() {
    var pool = bank().filter(function (q) {
      return recent.indexOf(q.id) < 0;
    });
    if (!pool.length) {
      recent = [];
      pool = bank();
    }
    var q = pool[Math.floor(Math.random() * pool.length)];
    recent.push(q.id);
    if (recent.length > 24) recent = recent.slice(-24);
    return q;
  }

  function shuffle(list) {
    var arr = list.slice();
    var i;
    for (i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
    }
    return arr;
  }

  function formatMath(text) {
    if (window.formatJM25GameMath) return window.formatJM25GameMath(text);
    return text;
  }

  function qText(q) {
    var raw = lang() === "zh" ? q.questionZh : q.questionEn;
    return formatMath(raw);
  }

  function cText(c) {
    var raw = lang() === "zh" ? c.textZh : c.textEn;
    return formatMath(raw);
  }

  function setFeedback(msg, kind) {
    var node = el("duel-feedback");
    if (!node) return;
    node.textContent = msg || "";
    node.classList.toggle("is-ok", kind === "ok");
    node.classList.toggle("is-bad", kind === "bad");
  }

  function updateHud() {
    setText("hud-progress", turn + " / " + totalTurns);
    setText("hud-bombs", bombs + " / " + MAX_BOMBS);
  }

  function setText(id, value) {
    var node = el(id);
    if (node) node.textContent = value;
  }

  function cardHtml(text, extraClass, attrs) {
    return (
      '<div class="duel-card' +
      (extraClass ? " " + extraClass : "") +
      '" ' +
      (attrs || "") +
      ">" +
      text +
      "</div>"
    );
  }

  function renderBombs() {
    var rack = el("duel-bomb-rack");
    if (!rack) return;
    var i;
    var html = "";
    for (i = 0; i < MAX_BOMBS; i++) {
      html +=
        '<div class="duel-bomb-slot' +
        (i < bombs ? " is-filled" : "") +
        '">' +
        (i < bombs ? "💣" : "") +
        "</div>";
    }
    rack.innerHTML = html;
  }

  function setOverlay(visible, title, msg, showReview) {
    var overlay = el("game-overlay");
    if (!overlay) return;
    overlay.classList.toggle("is-visible", visible);
    var setup = overlay.querySelector(".duel-setup-card");
    if (setup) setup.style.display = visible ? "" : "none";
    var turnsLabel = overlay.querySelector(".duel-turns-label");
    var turnsRange = el("duel-turns");
    var turnsOut = el("duel-turns-out");
    var hideSetupFields = showReview || running;
    if (turnsLabel) turnsLabel.hidden = hideSetupFields;
    if (turnsRange) turnsRange.hidden = hideSetupFields;
    if (turnsOut) turnsOut.hidden = hideSetupFields;
    if (title) setText("overlay-title", title);
    if (msg) setText("overlay-msg", msg);
    var review = el("btn-review-comics");
    if (review) review.hidden = !showReview;
  }

  function clearZones() {
    var qs = el("duel-question-slot");
    var as = el("duel-answer-slot");
    if (qs) qs.innerHTML = "";
    if (as) as.innerHTML = "";
  }

  function flyCard(fromEl, toEl, text, className, onDone) {
    var stage = document.querySelector("#jm25-factor-duel-game .duel-stage");
    if (!stage || !toEl) {
      toEl.innerHTML = cardHtml(text, "is-settled " + (className || ""));
      if (onDone) onDone();
      return;
    }
    var ghost = document.createElement("div");
    ghost.className = "duel-card duel-fly " + (className || "");
    ghost.innerHTML = text;
    stage.appendChild(ghost);
    var fr = fromEl ? fromEl.getBoundingClientRect() : el("duel-ai").getBoundingClientRect();
    var tr = toEl.getBoundingClientRect();
    var sr = stage.getBoundingClientRect();
    ghost.style.left = fr.left - sr.left + "px";
    ghost.style.top = fr.top - sr.top + "px";
    ghost.style.width = Math.max(fr.width, 120) + "px";
    requestAnimationFrame(function () {
      ghost.style.left = tr.left - sr.left + (tr.width - ghost.offsetWidth) / 2 + "px";
      ghost.style.top = tr.top - sr.top + (tr.height - ghost.offsetHeight) / 2 + "px";
      ghost.classList.add("is-moving");
    });
    setTimeout(function () {
      ghost.remove();
      toEl.innerHTML = cardHtml(text, "is-settled " + (className || ""));
      if (onDone) onDone();
    }, 520);
  }

  function flyDealToHand(fromEl, anchorEl, text, cardIndex, onDone) {
    var stage = document.querySelector("#jm25-factor-duel-game .duel-stage");
    if (!stage || !anchorEl) {
      if (onDone) onDone();
      return;
    }
    var ghost = document.createElement("div");
    ghost.className = "duel-card duel-fly duel-answer-card is-deal-fly";
    ghost.innerHTML = text;
    stage.appendChild(ghost);
    var fr = fromEl ? fromEl.getBoundingClientRect() : anchorEl.getBoundingClientRect();
    var tr = anchorEl.getBoundingClientRect();
    var sr = stage.getBoundingClientRect();
    var tilts = [-7, -2, 3, 8];
    var tilt = tilts[cardIndex] || 0;
    ghost.style.left = fr.left - sr.left + "px";
    ghost.style.top = fr.top - sr.top + "px";
    ghost.style.width = Math.max(fr.width, 100) + "px";
    ghost.style.transform = "rotate(-12deg) scale(0.88)";
    requestAnimationFrame(function () {
      ghost.style.left = tr.left - sr.left + (tr.width - ghost.offsetWidth) / 2 + "px";
      ghost.style.top = tr.top - sr.top + (tr.height - ghost.offsetHeight) / 2 + "px";
      ghost.style.transform = "rotate(" + tilt + "deg) scale(1)";
      ghost.classList.add("is-moving");
    });
    setTimeout(function () {
      ghost.remove();
      if (onDone) onDone(tilt);
    }, DEAL_FLY_MS);
  }

  function dealHand() {
    if (!question) return;
    hand = shuffle(question.choices).map(function (c, idx) {
      return { id: idx, correct: !!c.correct, text: cText(c) };
    });
    var handEl = el("duel-hand");
    var pile = el("duel-draw-pile");
    if (!handEl) return;
    handEl.innerHTML = "";
    handEl.classList.add("is-dealing");
    locked = true;
    dealing = true;
    if (pile) pile.classList.add("is-active");

    function finishDeal() {
      if (pile) pile.classList.remove("is-active");
      handEl.classList.remove("is-dealing");
      handEl.classList.add("is-dealt-ready");
      setTimeout(function () {
        handEl.classList.remove("is-dealt-ready");
      }, 400);
      dealing = false;
      locked = false;
      bindHandCards();
    }

    function dealOne(i) {
      if (i >= hand.length) {
        finishDeal();
        return;
      }
      var anchor = document.createElement("div");
      anchor.className = "duel-hand-anchor";
      anchor.setAttribute("aria-hidden", "true");
      handEl.appendChild(anchor);
      var from = pile || handEl;
      flyDealToHand(from, anchor, hand[i].text, i, function (tilt) {
        var wrap = document.createElement("div");
        wrap.innerHTML = cardHtml(
          hand[i].text,
          "duel-answer-card is-dealt",
          'data-hand="' + i + '" draggable="false"'
        );
        var card = wrap.firstElementChild;
        if (card && tilt) {
          card.style.setProperty("--deal-tilt", tilt + "deg");
        }
        if (anchor.parentNode) anchor.replaceWith(card);
        setTimeout(function () {
          dealOne(i + 1);
        }, DEAL_STAGGER_MS);
      });
    }

    dealOne(0);
  }

  function bindHandCards() {
    document.querySelectorAll("#duel-hand .duel-answer-card").forEach(function (node) {
      node.addEventListener("pointerdown", onPointerDown);
    });
  }

  function onPointerDown(evt) {
    if (!running || locked || dealing || !question) return;
    var card = evt.currentTarget;
    drag = {
      el: card,
      idx: parseInt(card.getAttribute("data-hand"), 10),
      startX: evt.clientX,
      startY: evt.clientY,
      moved: false,
    };
    card.setPointerCapture(evt.pointerId);
    card.addEventListener("pointermove", onPointerMove);
    card.addEventListener("pointerup", onPointerUp);
    card.addEventListener("pointercancel", onPointerUp);
  }

  function onPointerMove(evt) {
    if (!drag) return;
    drag.moved = true;
    var card = drag.el;
    card.classList.add("is-dragging");
    card.style.position = "fixed";
    card.style.zIndex = "40";
    card.style.left = evt.clientX - card.offsetWidth / 2 + "px";
    card.style.top = evt.clientY - card.offsetHeight / 2 + "px";
    var zone = el("duel-answer-zone");
    if (zone) zone.classList.toggle("is-hover", pointIn(evt, zone));
  }

  function onPointerUp(evt) {
    if (!drag) return;
    var card = drag.el;
    var idx = drag.idx;
    var choice = hand[idx];
    var moved = drag.moved;
    card.removeEventListener("pointermove", onPointerMove);
    card.removeEventListener("pointerup", onPointerUp);
    card.removeEventListener("pointercancel", onPointerUp);
    card.classList.remove("is-dragging");
    card.style.position = "";
    card.style.zIndex = "";
    card.style.left = "";
    card.style.top = "";
    var zone = el("duel-answer-zone");
    if (zone) zone.classList.remove("is-hover");
    drag = null;
    if (!choice) return;
    if (zone && (moved || pointIn(evt, zone)) && pointIn(evt, zone)) {
      resolveDrop(choice, card);
      return;
    }
    card.classList.add("is-return");
    setTimeout(function () {
      card.classList.remove("is-return");
    }, 320);
  }

  function pointIn(evt, node) {
    var r = node.getBoundingClientRect();
    return evt.clientX >= r.left && evt.clientX <= r.right && evt.clientY >= r.top && evt.clientY <= r.bottom;
  }

  function resolveDrop(choice, cardEl) {
    locked = true;
    var slot = el("duel-answer-slot");
    if (choice.correct) {
      flyCard(cardEl, slot, choice.text, "is-correct", function () {
        setFeedback(t("game.duel.correct"), "ok");
        turn += 1;
        updateHud();
        if (turn >= totalTurns) {
          win();
          return;
        }
        setTimeout(beginAiTurn, 700);
      });
      el("duel-hand").innerHTML = "";
      return;
    }
    bombs += 1;
    updateHud();
    renderBombs();
    setFeedback(t("game.duel.wrong"), "bad");
    var rack = el("duel-bomb-rack");
    cardEl.classList.add("is-bombing");
    flyCard(cardEl, rack.children[bombs - 1] || rack, "💣", "is-bomb", function () {
      el("duel-hand").innerHTML = "";
      if (bombs >= MAX_BOMBS) {
        explode();
        return;
      }
      turn += 1;
      updateHud();
      if (turn >= totalTurns) {
        win();
        return;
      }
      setTimeout(beginAiTurn, 900);
    });
  }

  function explode() {
    var stage = document.querySelector("#jm25-factor-duel-game .duel-stage");
    if (stage) {
      stage.classList.add("is-exploding");
      setTimeout(function () {
        stage.classList.remove("is-exploding");
      }, 900);
    }
    running = false;
    locked = true;
    setOverlay(true, t("game.over"), t("game.duel.explode"), true);
  }

  function win() {
    running = false;
    locked = true;
    setOverlay(true, t("game.duel.winTitle"), t("game.duel.winMsg"), true);
  }

  function beginAiTurn() {
    locked = true;
    clearZones();
    question = pickQuestion();
    if (!question) {
      setFeedback(t("game.duel.noBank"), "bad");
      return;
    }
    var slot = el("duel-question-slot");
    var ai = el("duel-ai");
    flyCard(ai, slot, qText(question), "is-question", function () {
      dealHand();
    });
  }

  function startRound() {
    var range = el("duel-turns");
    totalTurns = range ? parseInt(range.value, 10) : 10;
    if (totalTurns < MIN_TURNS) totalTurns = MIN_TURNS;
    if (totalTurns > MAX_TURNS) totalTurns = MAX_TURNS;
    turn = 0;
    bombs = 0;
    recent = [];
    running = true;
    locked = false;
    setOverlay(false);
    setFeedback("", "");
    updateHud();
    renderBombs();
    clearZones();
    el("duel-hand").innerHTML = "";
    beginAiTurn();
  }

  function bind(target, type, fn) {
    if (!target) return;
    target.addEventListener(type, fn);
    listeners.push({ target: target, type: type, fn: fn });
  }

  function unbindAll() {
    listeners.forEach(function (entry) {
      entry.target.removeEventListener(entry.type, entry.fn);
    });
    listeners = [];
  }

  function init() {
    destroy();
    if (!el("jm25-factor-duel-game")) return;
    running = false;
    locked = false;
    turn = 0;
    bombs = 0;
    renderBombs();
    updateHud();
    clearZones();
    var handEl = el("duel-hand");
    if (handEl) handEl.innerHTML = "";
    setOverlay(true, t("game.ready"), t("game.readyMsg.jm25.duel"), false);
    var range = el("duel-turns");
    var out = el("duel-turns-out");
    if (range && out) {
      out.textContent = range.value;
      bind(range, "input", function () {
        out.textContent = range.value;
      });
    }
    bind(el("btn-start"), "click", startRound);
    bind(el("btn-review-comics"), "click", function () {
      location.hash = "comics";
    });
  }

  function destroy() {
    unbindAll();
    drag = null;
    dealing = false;
    running = false;
    locked = false;
    question = null;
    hand = [];
  }

  function onShow() {
    renderBombs();
    updateHud();
  }

  return { init: init, destroy: destroy, onShow: onShow };
})();
