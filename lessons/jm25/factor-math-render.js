window.renderFactorStepMath = function renderFactorStepMath(step, lang) {
  var isZh = lang === "zh";

  function buildCrossGridHtml(viz) {
    var tl = viz.topLeft;
    var tr = viz.topRight;
    var bl = viz.bottomLeft;
    var br = viz.bottomRight;
    var row1 = "(" + tl + " + " + tr + ")";
    var row2 = "(" + bl + " + " + br + ")";
    var row1Label = isZh ? "第 1 行" : "Row 1";
    var row2Label = isZh ? "第 2 行" : "Row 2";
    var crossNote = isZh ? "對角相乘 → 相加 = 中項" : "Cross multiply diagonals → add for middle term";

    return (
      '<div class="math-viz math-viz--cross">' +
      '<p class="math-cross-caption">' +
      crossNote +
      "</p>" +
      '<div class="math-cross-grid2">' +
      '<div class="math-cross-grid2-table">' +
      '<div class="math-cross-grid2-cell">' +
      tl +
      "</div>" +
      '<div class="math-cross-grid2-cell">' +
      tr +
      "</div>" +
      '<div class="math-cross-grid2-cell">' +
      bl +
      "</div>" +
      '<div class="math-cross-grid2-cell">' +
      br +
      "</div>" +
      '<svg class="math-cross-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">' +
      '<line class="math-cross-diag math-cross-diag--tl-br" x1="25" y1="25" x2="75" y2="75"></line>' +
      '<line class="math-cross-diag math-cross-diag--bl-tr" x1="25" y1="75" x2="75" y2="25"></line>' +
      "</svg>" +
      '<span class="math-cross-diag-label math-cross-diag-label--tl-br">' +
      tl +
      " × " +
      br +
      "</span>" +
      '<span class="math-cross-diag-label math-cross-diag-label--bl-tr">' +
      bl +
      " × " +
      tr +
      "</span>" +
      "</div>" +
      '<div class="math-cross-row-labels">' +
      '<div class="math-cross-row-label">' +
      '<span class="math-cross-row-tag">' +
      row1Label +
      "</span>" +
      "<span>" +
      row1 +
      "</span>" +
      "</div>" +
      '<div class="math-cross-row-label">' +
      '<span class="math-cross-row-tag">' +
      row2Label +
      "</span>" +
      "<span>" +
      row2 +
      "</span>" +
      "</div>" +
      "</div>" +
      "</div>" +
      "</div>"
    );
  }

  var viz = step.mathViz;
  if (!viz) {
    var text = isZh ? step.mathZh : step.mathEn;
    if (!text) return "";
    return '<pre class="sci-step-math sci-step-math--mono">' + text + "</pre>";
  }

  if (viz.type === "annotated-expr") {
    var exprCells = "";
    var arrowCells = "";
    var noteCells = "";
    viz.terms.forEach(function (term) {
      var mid = term.middle ? " math-cell--mid" : "";
      exprCells +=
        '<span class="math-cell' + mid + '"><span class="math-expr-term">' + term.text + "</span></span>";
      if (term.annotate) {
        arrowCells += '<span class="math-cell' + mid + '"><span class="math-pointer">↑</span></span>';
        noteCells += '<span class="math-cell' + mid + '"><span class="math-note">' + term.annotate + "</span></span>";
      } else {
        arrowCells += '<span class="math-cell' + mid + '"></span>';
        noteCells += '<span class="math-cell' + mid + '"></span>';
      }
    });
    return (
      '<div class="math-viz math-viz--annotate">' +
      '<div class="math-annotate-row">' +
      exprCells +
      "</div>" +
      '<div class="math-annotate-row math-annotate-row--pointer">' +
      arrowCells +
      "</div>" +
      '<div class="math-annotate-row math-annotate-row--note">' +
      noteCells +
      "</div>" +
      "</div>"
    );
  }

  if (viz.type === "cross-grid") {
    return buildCrossGridHtml(viz);
  }

  if (viz.type === "cross-rows") {
    return buildCrossGridHtml({
      topLeft: viz.row1Left,
      topRight: viz.row1Right,
      bottomLeft: viz.row2Left,
      bottomRight: viz.row2Right,
    });
  }

  if (viz.type === "cross-sum") {
    var sumLabel = isZh ? viz.sumLabelZh || "和" : viz.sumLabelEn || "Sum";
    var rows = viz.products
      .map(function (p, i) {
        var diagClass = i === 0 ? " math-sum-row--diag-a" : " math-sum-row--diag-b";
        return (
          '<div class="math-sum-row' +
          diagClass +
          '">' +
          "<span>" +
          p.left +
          "</span>" +
          '<span class="math-sum-eq">=</span>' +
          "<span>" +
          p.right +
          "</span>" +
          "</div>"
        );
      })
      .join("");
    return (
      '<div class="math-viz math-viz--sum">' +
      rows +
      '<div class="math-sum-divider"></div>' +
      '<div class="math-sum-row math-sum-row--total">' +
      "<span>" +
      sumLabel +
      "</span>" +
      '<span class="math-sum-eq">=</span>' +
      "<span>" +
      viz.sumValue +
      (viz.ok ? " ✓" : "") +
      "</span>" +
      "</div>" +
      (viz.extra
        ? viz.extra
            .map(function (line) {
              return '<div class="math-sum-row math-sum-row--extra">' + line + "</div>";
            })
            .join("")
        : "") +
      "</div>"
    );
  }

  if (viz.type === "bracket-rows") {
    var rowHtml = viz.rows
      .map(function (row, i) {
        var label = isZh ? "第 " + (i + 1) + " 行" : "Row " + (i + 1);
        return '<div class="math-bracket-row"><span class="math-bracket-label">' + label + ":</span> " + row + "</div>";
      })
      .join("");
    return (
      '<div class="math-viz math-viz--brackets">' +
      rowHtml +
      (viz.result ? '<div class="math-bracket-result">' + viz.result + "</div>" : "") +
      "</div>"
    );
  }

  if (viz.type === "lines") {
    var lines = isZh && viz.linesZh ? viz.linesZh : viz.lines;
    return (
      '<div class="math-viz math-viz--lines">' +
      lines
        .map(function (line) {
          return '<div class="math-line">' + line + "</div>";
        })
        .join("") +
      "</div>"
    );
  }

  if (viz.type === "line") {
    var lineText = isZh && viz.textZh ? viz.textZh : viz.text;
    return '<div class="math-viz math-viz--line">' + lineText + "</div>";
  }

  return "";
};
