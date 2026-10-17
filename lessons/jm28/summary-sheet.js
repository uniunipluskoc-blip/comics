(function () {
window.renderJM28Summary = function renderJM28Summary() {
  return (
    '<section class="jm28-sheet" aria-label="Special lines in a triangle">' +
    '  <div class="jm28-sheet-banner">' +
    bulbSvg() +
    '    <div class="jm28-ribbon">' +
    '      <h2>Special Lines in a Triangle</h2>' +
    '      <p>三角形的特殊線</p>' +
    "    </div>" +
    bulbSvg() +
    "  </div>" +
    '  <p class="jm28-quote">“ Four lines every triangle uses: median, altitude, angle bisector, and perpendicular bisector. ”</p>' +
    '  <div class="jm28-sheet-grid">' +
    card(
      "median",
      "Median",
      "中線",
      medianSvg(),
      "Joins a vertex to the midpoint of the opposite side.",
      "連頂點與對邊中點。",
      ""
    ) +
    card(
      "altitude",
      "Altitude",
      "高線",
      altitudeSvg(),
      "From a vertex, perpendicular to the opposite side.",
      "由頂點垂直於對邊。",
      ""
    ) +
    card(
      "bisector",
      "Angle bisector",
      "角平分線",
      bisectorSvg(),
      "A ray from a vertex that splits the angle in half.",
      "由頂點出發，把該角分成兩個相等的角。",
      ""
    ) +
    card(
      "perp",
      "Perpendicular bisector",
      "垂直平分線",
      perpSvg(),
      "Through the midpoint of a side, at right angles to that side.",
      "經過一邊的中點，並且垂直於該邊。",
      "Need not pass through the opposite vertex. 不必經過對角頂點。"
    ) +
    "  </div>" +
    '  <span class="jm28-star jm28-star-a" aria-hidden="true"></span>' +
    '  <span class="jm28-star jm28-star-b" aria-hidden="true"></span>' +
    '  <span class="jm28-check jm28-check-a" aria-hidden="true"></span>' +
    '  <span class="jm28-check jm28-check-b" aria-hidden="true"></span>' +
    "</section>"
  );
};

function card(kind, title, zhTitle, svg, en, zh, note) {
  var extra = "";
  if (kind === "median") extra = '<span class="jm28-clip" aria-hidden="true"></span>';
  if (kind === "bisector") extra = '<span class="jm28-tape" aria-hidden="true"></span>';
  var noteHtml = note ? '<p class="jm28-note">' + note + "</p>" : "";
  return (
    '<article class="jm28-card jm28-card-' +
    kind +
    '">' +
    extra +
    '  <div class="jm28-card-top">' +
    "    <h3>" +
    title +
    "<span>" +
    zhTitle +
    "</span></h3>" +
    svg +
    "  </div>" +
    "  <p>" +
    en +
    "</p>" +
    '  <p class="zh">' +
    zh +
    "</p>" +
    noteHtml +
    "</article>"
  );
}

function bulbSvg() {
  return (
    '<svg class="jm28-bulb" viewBox="0 0 36 46" aria-hidden="true">' +
    '<path d="M18 3a11 11 0 0 0-7 19.2c.8 1.1 1.3 2.2 1.3 3.3V28h11.4v-2.5c0-1.1.5-2.2 1.3-3.3A11 11 0 0 0 18 3z" fill="#ffe9a8" stroke="#2b2b2b" stroke-width="1.8"/>' +
    '<path d="M14 31.5h8M15 34.5h6M16.2 37.5h3.6" fill="none" stroke="#2b2b2b" stroke-width="1.8" stroke-linecap="round"/>' +
    "</svg>"
  );
}

function medianSvg() {
  return (
    '<svg class="jm28-diagram" viewBox="0 0 220 148" role="img" aria-label="Median from A to the midpoint M of BC">' +
    '<polygon points="110,22 28,118 192,118" fill="none" stroke="#2b2b2b" stroke-width="2.2" stroke-linejoin="round"/>' +
    '<line class="jm28-mark jm28-mark-median" x1="110" y1="22" x2="110" y2="118"/>' +
    '<line class="jm28-tick" x1="69" y1="110" x2="69" y2="126"/>' +
    '<line class="jm28-tick" x1="151" y1="110" x2="151" y2="126"/>' +
    '<text x="102" y="16">A</text>' +
    '<text x="10" y="132">B</text>' +
    '<text x="186" y="132">C</text>' +
    '<text x="116" y="108">M</text>' +
    "</svg>"
  );
}

function altitudeSvg() {
  return (
    '<svg class="jm28-diagram" viewBox="0 0 220 148" role="img" aria-label="Altitude from A meeting BC at a right angle at D">' +
    '<polygon points="78,20 22,118 198,118" fill="none" stroke="#2b2b2b" stroke-width="2.2" stroke-linejoin="round"/>' +
    '<line class="jm28-mark jm28-mark-altitude" x1="78" y1="20" x2="78" y2="118"/>' +
    '<path class="jm28-right" d="M66 118 L66 106 L78 106"/>' +
    '<text x="70" y="14">A</text>' +
    '<text x="6" y="132">B</text>' +
    '<text x="190" y="132">C</text>' +
    '<text x="84" y="136">D</text>' +
    "</svg>"
  );
}

function bisectorSvg() {
  return (
    '<svg class="jm28-diagram" viewBox="0 0 220 148" role="img" aria-label="Angle bisector from A to E, splitting angle BAC into two equal angles">' +
    '<polygon points="100,20 24,118 196,118" fill="none" stroke="#2b2b2b" stroke-width="2.2" stroke-linejoin="round"/>' +
    '<line class="jm28-mark jm28-mark-bisector" x1="100" y1="20" x2="105.7" y2="118"/>' +
    '<path class="jm28-arc" d="M84.1 47.8 A32 32 0 0 0 97.4 51.9"/>' +
    '<path class="jm28-arc" d="M87.9 43 A26 26 0 0 0 97 45.8"/>' +
    '<path class="jm28-arc" d="M106.3 51.4 A32 32 0 0 0 119 45.8"/>' +
    '<path class="jm28-arc" d="M106 45.3 A26 26 0 0 0 114.7 41.5"/>' +
    '<text x="92" y="14">A</text>' +
    '<text x="8" y="132">B</text>' +
    '<text x="188" y="132">C</text>' +
    '<text x="112" y="136">E</text>' +
    "</svg>"
  );
}

function perpSvg() {
  return (
    '<svg class="jm28-diagram" viewBox="0 0 220 148" role="img" aria-label="Perpendicular bisector of BC through midpoint M, missing vertex A">' +
    '<polygon points="158,22 24,112 196,112" fill="none" stroke="#2b2b2b" stroke-width="2.2" stroke-linejoin="round"/>' +
    '<line class="jm28-mark jm28-mark-perp" x1="110" y1="36" x2="110" y2="132"/>' +
    '<line class="jm28-tick" x1="67" y1="104" x2="67" y2="120"/>' +
    '<line class="jm28-tick" x1="153" y1="104" x2="153" y2="120"/>' +
    '<path class="jm28-right" d="M98 112 L98 100 L110 100"/>' +
    '<text x="162" y="18">A</text>' +
    '<text x="8" y="128">B</text>' +
    '<text x="188" y="128">C</text>' +
    '<text x="116" y="128">M</text>' +
    "</svg>"
  );
}
})();
