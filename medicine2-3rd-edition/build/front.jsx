// Front matter: cover, colophon, title page, contents (2 pp), how to use, at a glance.
// Evaluated inside build.jsx (shares doc, C, FONT, helpers, MAN). Contents page numbers are
// filled later by fillContents() once chapter destinations exist.

var FRONT = { contents: null, tiles: [] };
var MAINCH = [];
for (var i = 0; i < MAN.chapters.length; i++) if (!MAN.chapters[i].appendix) MAINCH.push(MAN.chapters[i]);
var BK = MAN.book, ST = MAN.stats || {};
var TX = BK.texts || {};
function fmtN(n) { n = String(n); return n.replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
// book-specific wording lives in data/book.json -> texts; {total} {corrected} {new} {chapters} are filled in
function sub(s) { return String(s || "").replace(/\{total\}/g, fmtN((ST.mcq || 0) + (ST.emq || 0))).replace(/\{corrected\}/g, fmtN(ST.corrected || 0)).replace(/\{new\}/g, String(ST.new || 0)).replace(/\{chapters\}/g, String(MAINCH.length)); }
function tx(key, fallback) { return TX[key] !== undefined ? TX[key] : fallback; }
var TOTAL_Q = (ST.mcq || 0) + (ST.emq || 0);

// ---------------------------------------------------------------- p1 cover
(function cover() {
  var pg = doc.pages[0];
  rect(pg, [-BLEED, -BLEED, H + BLEED, W + BLEED], C.ink);
  var img = BK.cover && BK.cover.image ? ROOT + "/assets/" + BK.cover.image : null;
  if (img && File(img).exists) { var ph = placeImage(pg, img, [-BLEED, -BLEED, H + BLEED, W + BLEED]); ph.transparencySettings.blendingSettings.opacity = 92; }
  // top kicker
  var k = tframe(pg, [16, 16, 21, W - 16], (BK.team || "").toUpperCase() + "   /   " + BK.volume.toUpperCase() + "   /   " + BK.edition.toUpperCase());
  T(k, FONT.disp, "Semibold", 7.5, 9, C.gold, { tracking: 260 });
  var gl = pg.graphicLines.add({ geometricBounds: [mm(24), mm(16), mm(24), mm(46)] }); gl.strokeColor = C.gold; gl.strokeWeight = pt(2.5);
  // title stack
  // cover title: up to 3 stacked words, the last one in gold (texts.cover_lines)
  var CL = tx("cover_lines", String(BK.title).toUpperCase().split(" ").slice(0, 3));
  for (var li = 0; li < CL.length && li < 3; li++) {
    var tl = tframe(pg, [34 + li * 36, 13, 72 + li * 36, W - 10], CL[li]);
    T(tl, FONT.disp, "ExtraCondensed Black", 118, 100, li == CL.length - 1 ? C.gold : C.white, { tracking: -10 });
  }
  var subt = tframe(pg, [148, 16, 170, 150], sub(tx("tagline", "")));
  T(subt, FONT.serif, "Light", 12.5, 16, C.white);
  // stats row
  var stats = [[fmtN(TOTAL_Q), "questions"], [String(MAINCH.length), tx("chapters_word", "chapters")], [String(ST.new || 0), tx("new_word", "new questions")], [fmtN((ST.corrected || 0)), "corrected"]];
  var x = 16, sw = 42;
  for (var s = 0; s < stats.length; s++) {
    x = 16 + s * sw;
    var r = pg.graphicLines.add({ geometricBounds: [mm(180), mm(x), mm(180), mm(x + sw - 6)] });
    r.strokeColor = s == 0 ? C.gold : C.white; r.strokeWeight = pt(s == 0 ? 2 : 0.6); if (s) r.strokeTint = 60;
    var n = tframe(pg, [183, x, 196, x + sw], stats[s][0]); T(n, FONT.disp, "Condensed Bold", 30, 30, s == 0 ? C.gold : C.white);
    var l = tframe(pg, [197, x, 201, x + sw], stats[s][1].toUpperCase()); T(l, FONT.disp, "Semibold", 6.5, 8, C.white, { tracking: 180 });
  }
  // chapter colour band
  var by = 222, bh = 34, bw = (W - 32) / MAINCH.length;
  for (var c = 0; c < MAINCH.length; c++) {
    var ch = MAINCH[c], bx = 16 + c * bw;
    rect(pg, [by, bx, by + bh, bx + bw - 1.2], acc(ch));
    var num = tframe(pg, [by + 2.5, bx + 2.5, by + 12, bx + bw - 3], ("0" + ch.order).slice(-2));
    T(num, FONT.disp, "Condensed Bold", 16, 16, C.white);
    var nm = tframe(pg, [by + 17, bx + 2.5, by + bh - 2, bx + bw - 3], ch.short.toUpperCase());
    T(nm, FONT.disp, "Condensed Bold", 7.2, 8.2, C.white, { tracking: 20, hyphenation: false });
    nm.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
  }
  // authors
  var au = tframe(pg, [H - 30, 16, H - 22, W - 16], (BK.authors || []).join("   /   ").toUpperCase());
  T(au, FONT.disp, "Condensed Bold", 11, 13, C.white, { tracking: 80 });
  var tg = tframe(pg, [H - 20, 16, H - 15, W - 16], (BK.telegram || "").replace(/^https?:\/\//, ""));
  T(tg, FONT.sans, "Regular", 7, 9, C.white);
  tg.parentStory.texts[0].fillTint = 70;
  if (BK.telegram) { try { var hs = doc.hyperlinkTextSources.add(tg.parentStory.texts[0]); doc.hyperlinks.add(hs, doc.hyperlinkURLDestinations.add(BK.telegram), { visible: false }); } catch (e) { log("tg link " + e); } }
})();

// ---------------------------------------------------------------- p2 colophon (inside cover)
(function colophon() {
  var pg = addPage(null);
  var x0 = M.outside, x1 = W - M.inside;
  var t = tframe(pg, [150, x0, H - 20, x1 - 40], "");
  var st = t.parentStory;
  var lines = [
    [BK.title + " / " + BK.volume, "h"],
    [BK.edition + ". Prepared by " + (BK.authors || []).join(" and ") + (BK.team ? " for the " + BK.team : "") + ".", "p"]
  ];
  var CO = tx("colophon", []);   // [[heading, paragraph], ...]
  for (var ci = 0; ci < CO.length; ci++) { lines.push([sub(CO[ci][0]), "h"]); lines.push([sub(CO[ci][1]), "p"]); }
  for (var i = 0; i < lines.length; i++) {
    st.insertionPoints[-1].contents = lines[i][0] + (i < lines.length - 1 ? "\r" : "");
  }
  st.texts[0].appliedParagraphStyle = pstyle("Colophon", { basedOn: BASE, appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(7.4), leading: pt(10), fillColor: C.ink2, spaceAfter: mm(1.6) });
  var ch = pstyle("Colophon Head", { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(7), leading: pt(9), tracking: 120, capitalization: Capitalization.ALL_CAPS, fillColor: C.muted, spaceBefore: mm(2.2) });
  for (var j = 0; j < lines.length; j++) if (lines[j][1] == "h") st.paragraphs[j].appliedParagraphStyle = ch;
  t.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
})();

// ---------------------------------------------------------------- p3 title page
(function titlePage() {
  var pg = addPage(null);
  var x0 = M.inside, x1 = W - M.outside;
  var k = tframe(pg, [60, x0, 66, x1], BK.volume.toUpperCase() + "   /   " + BK.edition.toUpperCase());
  T(k, FONT.disp, "Semibold", 8, 10, C.muted, { tracking: 240 });
  var t = tframe(pg, [70, x0 - 1, 130, x1], tx("title_page", BK.title).replace(/\n/g, "\r"));
  T(t, FONT.disp, "ExtraCondensed Black", 72, 64, C.ink);
  var y = 136;
  for (var c = 0; c < MAINCH.length; c++) {
    var ch = MAINCH[c], w = (x1 - x0) / MAINCH.length;
    rect(pg, [y, x0 + c * w, y + 3, x0 + (c + 1) * w - 0.8], acc(ch));
  }
  var d = tframe(pg, [y + 9, x0, y + 40, x1 - 30], sub(tx("description", "{total} questions with answers and explanations.")));
  T(d, FONT.serif, "Light", 13, 18, C.ink2);
  var a = tframe(pg, [H - 60, x0, H - 40, x1], (BK.authors || []).join("\r"));
  T(a, FONT.disp, "Condensed Bold", 16, 18, C.ink);
  var tm = tframe(pg, [H - 36, x0, H - 30, x1], (BK.team || "").toUpperCase());
  T(tm, FONT.disp, "Semibold", 8, 10, C.gold, { tracking: 240 });
})();

// ---------------------------------------------------------------- p4–p5 contents (filled later)
(function contents() {
  var L = addPage(null), R = addPage(null);
  var xl0 = M.outside, xl1 = W - M.inside, xr0 = M.inside, xr1 = W - M.outside;
  var k = tframe(L, [22, xl0, 28, xl1], "CONTENTS"); T(k, FONT.disp, "Semibold", 8, 10, C.gold, { tracking: 260 });
  var t = tframe(L, [30, xl0, 58, xl1], "What's inside"); T(t, FONT.disp, "ExtraCondensed Black", 54, 50, C.ink);
  var rl = L.graphicLines.add({ geometricBounds: [mm(62), mm(xl0), mm(62), mm(xl0 + 28)] }); rl.strokeColor = C.ink; rl.strokeWeight = pt(3);
  var f1 = L.textFrames.add({ geometricBounds: [mm(70), mm(xl0), mm(H - 22), mm(xl1)] });
  var f2 = R.textFrames.add({ geometricBounds: [mm(22), mm(xr0), mm(H - 22), mm(xr1)] });
  f1.textFramePreferences.insetSpacing = [0, 0, 0, 0]; f2.textFramePreferences.insetSpacing = [0, 0, 0, 0];
  f1.textFramePreferences.textColumnCount = 2; f1.textFramePreferences.textColumnGutter = mm(7);
  f2.textFramePreferences.textColumnCount = 2; f2.textFramePreferences.textColumnGutter = mm(7);
  f1.nextTextFrame = f2;
  FRONT.contents = f1;
})();

// ---------------------------------------------------------------- p6 how to use
(function howTo() {
  var pg = addPage(null);
  var x0 = M.outside, x1 = W - M.inside;
  var k = tframe(pg, [22, x0, 28, x1], "BEFORE YOU START"); T(k, FONT.disp, "Semibold", 8, 10, C.gold, { tracking: 260 });
  var t = tframe(pg, [30, x0, 58, x1], "How to use this book"); T(t, FONT.disp, "ExtraCondensed Black", 44, 42, C.ink);
  var items = tx("how_to_use", null) || [
    ["Colour-coded systems", "Each system has its own colour, thumb tab and number on the page edge, so you can find a chapter from the closed book. The chapter opener lists every question set in that chapter with live page numbers."],
    ["Question sets", "Questions are grouped by source (exam papers, textbook self-assessment banks and new questions written for this edition). Every set has at most 25 questions, followed immediately by its answers, so you can test yourself in short sessions."],
    ["Linked questions and answers", "In the PDF, tap a question number to jump to its answer, and tap the answer number to return. Page numbers in the contents, chapter openers and index are links too."],
    ["Answers that teach", "Each answer gives the key, the correct option and an explanation of why it is right and why the tempting alternatives are wrong, updated to current UK and international guidance."],
    ["EMQs", "Extended matching questions share one option list per theme. Each option may be used once, more than once or not at all, just as in the exam."],
    ["Smart index", "The index at the back lists every clinical topic, with sub-entries such as diagnosis, investigation and management, and page references to every question on that topic."]
  ];
  var y = 68;
  for (var i = 0; i < items.length; i++) {
    var n = tframe(pg, [y, x0, y + 12, x0 + 14], ("0" + (i + 1)).slice(-2)); T(n, FONT.disp, "Condensed Bold", 22, 22, C.gold);
    var h = tframe(pg, [y + 0.5, x0 + 18, y + 6.5, x1], sub(items[i][0])); T(h, FONT.disp, "Condensed Bold", 13, 14, C.ink);
    var b = tframe(pg, [y + 7.5, x0 + 18, y + 32, x1], sub(items[i][1])); T(b, FONT.serif, "Regular", 9.6, 13.4, C.ink2);
    b.textFramePreferences.autoSizingReferencePoint = AutoSizingReferenceEnum.TOP_CENTER_POINT;
    b.textFramePreferences.autoSizingType = AutoSizingTypeEnum.HEIGHT_ONLY;
    y = b.geometricBounds[2] + 7;
  }
})();

// ---------------------------------------------------------------- p7 at a glance (tiles; page numbers later)
(function glance() {
  var pg = addPage(null);
  var x0 = M.inside, x1 = W - M.outside;
  var k = tframe(pg, [22, x0, 28, x1], tx("glance_kicker", "THE BANK AT A GLANCE")); T(k, FONT.disp, "Semibold", 8, 10, C.gold, { tracking: 260 });
  var t = tframe(pg, [30, x0, 58, x1], fmtN(TOTAL_Q) + " questions"); T(t, FONT.disp, "ExtraCondensed Black", 54, 50, C.ink);
  var all = MAN.chapters, cols = 2, gw = (x1 - x0 - 6) / cols, gh = 44, y0 = 68;
  for (var i = 0; i < all.length; i++) {
    var ch = all[i], cx = x0 + (i % cols) * (gw + 6), cy = y0 + Math.floor(i / cols) * (gh + 4.5);
    var A = acc(ch);
    rect(pg, [cy, cx, cy + gh, cx + gw], A, 10);
    rect(pg, [cy, cx, cy + gh, cx + 2.2], A);
    var n = tframe(pg, [cy + 3, cx + 6, cy + 17, cx + 30], ("0" + ch.order).slice(-2)); T(n, FONT.disp, "ExtraCondensed Black", 34, 34, A);
    var nm = tframe(pg, [cy + 4, cx + 30, cy + 18, cx + gw - 4], ch.title); T(nm, FONT.disp, "Condensed Bold", 12.5, 13.5, C.ink, { hyphenation: false });
    var pr = tframe(pg, [cy + 19, cx + 30, cy + 23, cx + gw - 4], ch.part.toUpperCase()); T(pr, FONT.disp, "Semibold", 6, 7.5, C.muted, { tracking: 120 });
    var s = tframe(pg, [cy + 27, cx + 6, cy + 40, cx + gw - 4], ch.n_mcq + " MCQs   /   " + ch.n_emq + " EMQ items   /   " + ch.banks.length + " sets");
    T(s, FONT.sans, "Semibold", 8.5, 11, C.ink2);
    var pgref = tframe(pg, [cy + 27, cx + gw - 30, cy + 33, cx + gw - 4], "");
    FRONT.tiles.push({ ch: ch, frame: pgref });
  }
})();

// page links across documents: URL https://imb.local/p/<page>[/<y mm>] — the merge tool turns
// these into internal links of the combined PDF.
function pageLink(textObj, page, y) {
  if (!page) return;
  try {
    var url = "https://imb.local/p/" + page + (y ? "/" + y : "");
    var d = doc.hyperlinkURLDestinations.add(url);
    doc.hyperlinks.add(doc.hyperlinkTextSources.add(textObj), d, { visible: false });
  } catch (e) { log("page link " + e); }
}
function fillContents() {
  var st = FRONT.contents.parentStory;
  var COLW = (W - M.inside - M.outside - 7) / 2;
  var sCh = pstyle("Cont Chapter", { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(13), leading: pt(15),
    fillColor: C.ink, spaceBefore: mm(4.5), spaceAfter: mm(1), keepWithNext: 2, hyphenation: false });
  sCh.tabStops.everyItem().remove();
  sCh.tabStops.add({ position: mm(10), alignment: TabStopAlignment.LEFT_ALIGN });
  sCh.tabStops.add({ position: mm(COLW), alignment: TabStopAlignment.RIGHT_ALIGN });
  var sPart = pstyle("Cont Part", { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(6.5), leading: pt(8), tracking: 140,
    capitalization: Capitalization.ALL_CAPS, fillColor: C.muted, leftIndent: mm(10), spaceAfter: mm(1.5), keepWithNext: 2 });
  var sBank = pstyle("Cont Bank", { basedOn: BASE, appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(7.8), leading: pt(10.2), fillColor: C.ink2,
    leftIndent: mm(10), hyphenation: false });
  sBank.tabStops.everyItem().remove();
  sBank.tabStops.add({ position: mm(COLW - 11), alignment: TabStopAlignment.RIGHT_ALIGN, leader: " ." });
  sBank.tabStops.add({ position: mm(COLW), alignment: TabStopAlignment.RIGHT_ALIGN });
  var links = [], colours = [];
  function addPara(text, style, page, color) {
    if (st.characters.length) st.insertionPoints[-1].contents = "\r";
    st.insertionPoints[-1].contents = text + (page ? String(page) : "");
    var idx = st.paragraphs.length - 1;
    st.paragraphs[idx].appliedParagraphStyle = style;
    if (page) links.push({ i: idx, page: page });
    if (color) colours.push({ i: idx, c: color });
  }
  for (var i = 0; i < MAN.chapters.length; i++) {
    var ch = MAN.chapters[i], inf = ch.info;
    addPara(("0" + ch.order).slice(-2) + "\t" + ch.title + "\t", sCh, inf ? inf.start : null, acc(ch));
    addPara(ch.part + "   /   " + (ch.n_mcq + ch.n_emq) + " questions", sPart, null, null);
    var banks = inf && inf.banks ? inf.banks : ch.banks;
    for (var b = 0; b < banks.length; b++) addPara(banks[b].title + "\t" + banks[b].count + " Q\t", sBank, banks[b].page, null);
  }
  if (BACKINFO) {
    if (BACKINFO.indexPage) addPara("IX\tIndex\t", sCh, BACKINFO.indexPage, C.gold);
    if (BACKINFO.creditsPage) addPara("CR\tSources & credits\t", sCh, BACKINFO.creditsPage, C.gold);
  }
  for (var k = 0; k < colours.length; k++) { try { st.paragraphs[colours[k].i].words[0].fillColor = colours[k].c; } catch (e) {} }
  for (var l = 0; l < links.length; l++) { try { var w = st.paragraphs[links[l].i].words[-1]; pageLink(w, links[l].page); } catch (e) { log("cont link " + e); } }
  // at-a-glance tiles
  for (var t = 0; t < FRONT.tiles.length; t++) {
    var tl = FRONT.tiles[t], pgNo = tl.ch.info ? tl.ch.info.start : null;
    tl.frame.parentStory.contents = pgNo ? "p. " + pgNo : "";
    T(tl.frame, FONT.disp, "Condensed Bold", 11, 12, acc(tl.ch), { justification: Justification.RIGHT_ALIGN });
    if (pgNo) pageLink(tl.frame.parentStory.texts[0], pgNo);
  }
  if (FRONT.contents.parentStory.overflows) log("CONTENTS OVERSET");
}
