// Back matter: smart index (native InDesign index, live page references on every question number),
// sources & credits, back cover. Evaluated inside build.jsx after all chapters are laid out.

var BACK = { indexPage: null, creditsPage: null };
var BODY = masterFor(null);
var MAINCH = [];
for (var mi = 0; mi < MAN.chapters.length; mi++) if (!MAN.chapters[mi].appendix) MAINCH.push(MAN.chapters[mi]);
var BK = MAN.book, ST = MAN.stats || {};
var TX = BK.texts || {};
function fmtN(n) { n = String(n); return n.replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
// book-specific wording lives in data/book.json -> texts; {total} {corrected} {new} {chapters} are filled in
function sub(s) { return String(s || "").replace(/\{total\}/g, fmtN((ST.mcq || 0) + (ST.emq || 0))).replace(/\{corrected\}/g, fmtN(ST.corrected || 0)).replace(/\{new\}/g, String(ST.new || 0)).replace(/\{chapters\}/g, String(MAINCH.length)); }
function tx(key, fallback) { return TX[key] !== undefined ? TX[key] : fallback; }
var TOTAL_Q = (ST.mcq || 0) + (ST.emq || 0);


// ---------------------------------------------------------------- index styles
var IX = {
  title: pstyle("IX Title", { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "ExtraCondensed Black", pointSize: pt(54), leading: pt(50),
    fillColor: C.ink, spaceAfter: mm(8), spanColumnType: SpanColumnTypeOptions.SPAN_COLUMNS, spanSplitColumnCount: SpanColumnCountOptions.ALL }),
  sect: pstyle("IX Section", { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(16), leading: pt(18), fillColor: C.gold,
    spaceBefore: mm(3.5), spaceAfter: mm(1), keepWithNext: 2, ruleBelow: true, ruleBelowColor: C.line, ruleBelowWeight: pt(0.5), ruleBelowOffset: mm(1) }),
  l1: pstyle("IX Level 1", { basedOn: BASE, appliedFont: FONT.sans, fontStyle: "Semibold", pointSize: pt(7.6), leading: pt(9.6), fillColor: C.ink,
    leftIndent: mm(4), firstLineIndent: mm(-4), hyphenation: false, keepWithNext: 0 }),
  l2: pstyle("IX Level 2", { basedOn: BASE, appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(7.3), leading: pt(9.2), fillColor: C.ink2,
    leftIndent: mm(8), firstLineIndent: mm(-4), hyphenation: false }),
  num: cstyle("IX Page", { appliedFont: FONT.sans, fontStyle: "Regular", fillColor: C.muted })
};

// ---------------------------------------------------------------- index topics + page references
function buildIndex() {
  // 1. collect page of every question number + index entries
  var E = {};          // l1 -> {pages:[], seen:{}, subs:{l2:{pages:[],seen:{}}}}
  function addRef(node, pg, dest) { if (node.seen[pg]) return; node.seen[pg] = 1; node.pages.push({ p: pg, d: dest }); }
  for (var i = 0; i < MAN.chapters.length; i++) {
    var ch = MAN.chapters[i];
    if (!ch.info || !ch.info.questions) { log("no part info for " + ch.id); continue; }
    var pos = {};
    for (var z = 0; z < ch.info.questions.length; z++) pos[ch.info.questions[z].key] = ch.info.questions[z];
    for (var j = 0; j < ch.questions.length; j++) {
      var q = ch.questions[j], hit = pos[q.key];
      if (!hit || !q.ix || !q.ix.length) continue;
      var pgName = String(hit.page);
      for (var e = 0; e < q.ix.length; e++) {
        var l1 = q.ix[e][0], l2 = q.ix[e][1];
        if (!E[l1]) E[l1] = { pages: [], seen: {}, subs: {} };
        if (l2) {
          if (!E[l1].subs[l2]) E[l1].subs[l2] = { pages: [], seen: {} };
          addRef(E[l1].subs[l2], pgName, hit);
        } else addRef(E[l1], pgName, hit);
      }
    }
  }
  function sk(s) { return s.toLowerCase().replace(/^[^a-z0-9]+/, ""); }
  var keys = []; for (var k in E) keys.push(k);
  var tmp = []; for (var ti = 0; ti < keys.length; ti++) tmp.push(sk(keys[ti]) + "" + keys[ti]);
  tmp.sort(); keys = []; for (var tj = 0; tj < tmp.length; tj++) keys.push(tmp[tj].split("")[1]);
  log("ix: collected " + keys.length);
  // 2. build text with markers around page numbers
  var paras = [], styles = [], LINKS = [], OPEN = "@@", CLOSE = "%%";
  function pagesText(node) {
    node.pages.sort(function (a, b) { return parseInt(a.p, 10) - parseInt(b.p, 10); });
    var out = [];
    for (var i = 0; i < node.pages.length; i++) { out.push(OPEN + node.pages[i].p + CLOSE); LINKS.push(node.pages[i].d); }
    return out.join(", ");
  }
  paras.push("Index"); styles.push(IX.title);
  var lastSect = "";
  for (var n = 0; n < keys.length; n++) {
    var key = keys[n], s0 = sk(key).charAt(0).toUpperCase();
    var sect = /[A-Z]/.test(s0) ? s0 : "#";
    if (sect != lastSect) { paras.push(sect); styles.push(IX.sect); lastSect = sect; }
    var node = E[key];
    paras.push(key + (node.pages.length ? "  " + pagesText(node) : "")); styles.push(IX.l1);
    var sk2 = []; for (var s in node.subs) sk2.push(s);
    sk2.sort();
    for (var m = 0; m < sk2.length; m++) { paras.push(sk2[m] + "  " + pagesText(node.subs[sk2[m]])); styles.push(IX.l2); }
  }
  log("ix: text built " + paras.length);
  // 3. place on pages
  ensureSide("R", BODY);
  var pg = addPage(BODY);
  var tf = pg.textFrames.add({ geometricBounds: textBounds(pg) });
  tf.textFramePreferences.textColumnCount = 3; tf.textFramePreferences.textColumnGutter = mm(5);
  tf.textFramePreferences.insetSpacing = [0, 0, 0, 0];
  var st = tf.parentStory;
  st.contents = paras.join("\r");
  st.texts[0].appliedParagraphStyle = IX.l1;
  for (var p = 0; p < paras.length; p++) if (styles[p] !== IX.l1) st.paragraphs[p].appliedParagraphStyle = styles[p];
  var guard = 0;
  while (tf.overflows && guard++ < 80) {
    var np = addPage(BODY);
    var nf = np.textFrames.add({ geometricBounds: textBounds(np) });
    nf.textFramePreferences.textColumnCount = 3; nf.textFramePreferences.textColumnGutter = mm(5);
    nf.textFramePreferences.insetSpacing = [0, 0, 0, 0];
    tf.nextTextFrame = nf; tf = nf;
  }
  log("ix: placed, frames " + guard);
  // 4. hyperlink every page number to its question, then strip markers
  app.findGrepPreferences = NothingEnum.NOTHING; app.changeGrepPreferences = NothingEnum.NOTHING;
  app.findGrepPreferences.findWhat = "@@[0-9]+%%";
  var found = st.findGrep();
  if (found.length != LINKS.length) log("index link count mismatch " + found.length + "/" + LINKS.length);
  for (var f = 0; f < Math.min(found.length, LINKS.length); f++) {
    var t = found[f];
    t.appliedCharacterStyle = IX.num;
    if (!LINKS[f]) continue;
    try { var hs = doc.hyperlinkTextSources.add(t); doc.hyperlinks.add(hs, doc.hyperlinkURLDestinations.add("https://imb.local/p/" + LINKS[f].page + "/" + LINKS[f].y), { visible: false }); } catch (err) { if (f < 5) log("ix link " + err); }
  }
  app.findGrepPreferences.findWhat = "@@|%%";
  app.changeGrepPreferences.changeTo = "";
  st.changeGrep();
  app.findGrepPreferences = NothingEnum.NOTHING; app.changeGrepPreferences = NothingEnum.NOTHING;
  BACK.indexPage = parseInt(st.paragraphs[0].parentTextFrames[0].parentPage.name, 10);
  log("index entries " + keys.length + " links " + LINKS.length + " pages " + (guard + 1));
}

// ---------------------------------------------------------------- sources & credits
function credits() {
  var pg = addPage(BODY);
  var b = textBounds(pg);
  var k = tframe(pg, [b[0] + 2, b[1], b[0] + 8, b[3]], "SOURCES & CREDITS"); T(k, FONT.disp, "Semibold", 8, 10, C.gold, { tracking: 260 });
  var t = tframe(pg, [b[0] + 10, b[1], b[0] + 34, b[3]], "Sources & credits"); T(t, FONT.disp, "ExtraCondensed Black", 44, 42, C.ink);
  BACK.creditsPage = parseInt(pg.name, 10);
  var body = tframe(pg, [b[0] + 42, b[1], b[2], b[3]], "");
  body.textFramePreferences.textColumnCount = 2; body.textFramePreferences.textColumnGutter = mm(GUT);
  var st = body.parentStory, paras = [];
  function add(s, head) { if (st.characters.length) st.insertionPoints[-1].contents = "\r"; st.insertionPoints[-1].contents = s; paras.push(head); }
  var CR = tx("credits", []);   // [[heading, paragraph], ...] before the photo credits
  for (var cr = 0; cr < CR.length; cr++) { add(sub(CR[cr][0]), true); add(sub(CR[cr][1]), false); }
  add("Photographs", true);
  var cover = MAN.book.cover && MAN.book.cover.credit ? MAN.book.cover.credit : "";
  if (cover) add(cover, false);
  for (var i = 0; i < MAN.chapters.length; i++) {
    var ch = MAN.chapters[i];
    if (ch.divider && ch.divider.credit) add(("0" + ch.order).slice(-2) + " " + ch.title + ": " + ch.divider.credit, false);
  }
  var CR2 = tx("credits_after", []);
  for (var cr2 = 0; cr2 < CR2.length; cr2++) { add(sub(CR2[cr2][0]), true); add(sub(CR2[cr2][1]), false); }
  add("Contact", true);
  add((MAN.book.team || "") + "   " + (MAN.book.telegram || ""), false);
  st.texts[0].appliedParagraphStyle = pstyle("Credits", { basedOn: BASE, appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(8), leading: pt(11), fillColor: C.ink2, spaceAfter: mm(1.8) });
  var hs = pstyle("Credits Head", { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(11), leading: pt(13), fillColor: C.ink, spaceBefore: mm(3), spaceAfter: mm(1), keepWithNext: 2 });
  for (var j = 0; j < paras.length; j++) if (paras[j]) st.paragraphs[j].appliedParagraphStyle = hs;
}

// ---------------------------------------------------------------- back cover (always a left-hand, final page)
function backCover() {
  ensureSide("L", BODY);
  var pg = addPage(null);
  rect(pg, [-BLEED, -BLEED, H + BLEED, W + BLEED], C.ink);
  var img = ROOT + "/assets/web/cover2.jpg";
  var ch0 = MAN.chapters;
  // colour stripe
  var sx = 0, sw = (W + 2 * BLEED) / ch0.length;
  for (var i = 0; i < ch0.length; i++) rect(pg, [H - 14, -BLEED + i * sw, H + BLEED, -BLEED + (i + 1) * sw], acc(ch0[i]));
  var k = tframe(pg, [30, 20, 36, W - 20], MAN.book.title.toUpperCase() + "   /   " + MAN.book.volume.toUpperCase()); T(k, FONT.disp, "Semibold", 8, 10, C.gold, { tracking: 260 });
  var t = tframe(pg, [40, 20, 100, W - 30], sub(tx("back_headline", BK.title))); T(t, FONT.disp, "ExtraCondensed Black", 46, 44, C.white);
  var y = 108;
  var pts = tx("back_points", ["{total} questions with answers and explanations"]);
  for (var pp = 0; pp < pts.length; pp++) pts[pp] = sub(pts[pp]);

  for (var p = 0; p < pts.length; p++) {
    rect(pg, [y + 1.2, 20, y + 4.2, 23], C.gold);
    var b = tframe(pg, [y, 28, y + 12, W - 30], pts[p]); T(b, FONT.serif, "Regular", 12, 15.5, C.white);
    y += 16;
  }
  var chl = tframe(pg, [y + 8, 20, y + 62, W - 30], "");
  var s = [];
  for (var c = 0; c < MAINCH.length; c++) s.push(("0" + MAINCH[c].order).slice(-2) + "  " + MAINCH[c].title);
  chl.contents = s.join("\r");
  T(chl, FONT.disp, "Condensed Semibold", 11, 15, C.white);
  for (var c2 = 0; c2 < MAINCH.length; c2++) { try { chl.parentStory.paragraphs[c2].words[0].fillColor = acc(MAINCH[c2]); } catch (e) {} }
  var au = tframe(pg, [H - 34, 20, H - 20, W - 20], (MAN.book.authors || []).join("   /   ").toUpperCase() + "\r" + (MAN.book.team || "") + "   " + (MAN.book.telegram || "").replace(/^https?:\/\//, ""));
  T(au, FONT.disp, "Semibold", 8, 11, C.white, { tracking: 100 });
}


log("back: credits"); credits();
log("back: index"); buildIndex();
log("back: cover"); backCover();
