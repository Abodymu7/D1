// Question-bank book — InDesign layout engine.
// Reads build/out/manifest.json (written by gen.py) and lays out the whole book.
// Run through run.py (which injects OPTS) — never edit the generated INDD by hand if you
// want the tool to be able to rebuild it; edit data/*.json instead.
#target indesign

var ROOT = OPTS.root;                       // injected
var MAN = eval('(' + readText(ROOT + "/build/out/manifest.json") + ')');
var OUTDIR = OPTS.outdir;
var LOG = [];
function log(s) { LOG.push(s); try { var lf = File(OPTS.outdir + "/build_progress.txt"); lf.encoding = "UTF-8"; lf.open("a"); lf.writeln(new Date().toTimeString().substr(0, 8) + " " + s); lf.close(); } catch (e) {} }
function readText(p) { var f = File(p); f.encoding = "UTF-8"; f.open("r"); var t = f.read(); f.close(); return t; }
function writeText(p, t) { var f = File(p); f.encoding = "UTF-8"; f.open("w"); f.write(t); f.close(); }

app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
app.scriptPreferences.enableRedraw = false;
app.scriptPreferences.measurementUnit = AutoEnum.AUTO_VALUE;

// ------------------------------------------------------------------ geometry (mm)
var W = 210, H = 297, BLEED = 3;
var M = { top: 21, bottom: 20, inside: 19, outside: 17 };
var GUT = 6;
var FONT = {
  disp: "Acumin Variable Concept", serif: "Source Serif Variable", sans: "Source Sans Variable"
};

// ------------------------------------------------------------------ document
while (app.documents.length) app.documents[0].close(SaveOptions.NO);
var doc = app.documents.add(false);
with (doc.documentPreferences) {
  pageWidth = W + "mm"; pageHeight = H + "mm"; facingPages = true; pagesPerDocument = 1;
  documentBleedTopOffset = BLEED + "mm"; documentBleedUniformSize = true;
  startPageNumber = 1; allowPageShuffle = false;
}
doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS;
doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
doc.viewPreferences.rulerOrigin = RulerOrigin.PAGE_ORIGIN;
doc.textPreferences.typographersQuotes = true;
doc.textPreferences.smartTextReflow = false;
doc.gridPreferences.baselineGridShown = false;
doc.documentPreferences.intent = DocumentIntentOptions.PRINT_INTENT;
doc.hyphenationExceptions;  // noop

// ------------------------------------------------------------------ colours
function hex2rgb(h) { return [parseInt(h.substr(0, 2), 16), parseInt(h.substr(2, 2), 16), parseInt(h.substr(4, 2), 16)]; }
function swatch(name, hex) {
  var c = doc.colors.itemByName(name);
  if (c.isValid) return c;
  return doc.colors.add({ name: name, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: hex2rgb(hex) });
}
var C = {
  ink: swatch("IMB Ink", "0E1726"), ink2: swatch("IMB Ink 2", "1B2A41"), muted: swatch("IMB Muted", "667085"),
  line: swatch("IMB Line", "D0D5DD"), mist: swatch("IMB Mist", "F2F4F7"), paper: doc.swatches.itemByName("Paper"),
  gold: swatch("IMB Gold", "E8B64C"), white: swatch("IMB White", "FFFFFF")
};
var NONE = "None";
function acc(ch) { return swatch("IMB " + ch.id, ch.color); }

// ------------------------------------------------------------------ helpers
function pt(n) { return n + "pt"; }
function mm(n) { return n + "mm"; }
function font(fam, style) { return fam + "\t" + style; }
function setFont(o, fam, style) { o.appliedFont = fam; o.fontStyle = style; }

function pstyle(name, props) {
  var s = doc.paragraphStyles.itemByName(name);
  if (!s.isValid) s = doc.paragraphStyles.add({ name: name });
  s.properties = props;
  return s;
}
function cstyle(name, props) {
  var s = doc.characterStyles.itemByName(name);
  if (!s.isValid) s = doc.characterStyles.add({ name: name });
  s.properties = props;
  return s;
}
function rect(page, b, fill, tint, stroke) {
  var r = page.rectangles.add({ geometricBounds: [mm(b[0]), mm(b[1]), mm(b[2]), mm(b[3])] });
  r.fillColor = fill || NONE; if (tint !== undefined && tint !== null) r.fillTint = tint;
  r.strokeColor = stroke || NONE; if (!stroke) r.strokeWeight = 0;
  return r;
}
function tframe(page, b, text, props) {
  var t = page.textFrames.add({ geometricBounds: [mm(b[0]), mm(b[1]), mm(b[2]), mm(b[3])] });
  t.textFramePreferences.insetSpacing = [0, 0, 0, 0];
  t.contents = text || "";
  if (props) t.parentStory.texts[0].properties = props;
  return t;
}
// style a whole frame's text
function T(t, fam, style, size, lead, color, extra) {
  var tx = t.parentStory.texts[0];
  tx.appliedParagraphStyle = doc.paragraphStyles.itemByName("[Basic Paragraph]");
  tx.appliedCharacterStyle = doc.characterStyles.itemByName("[None]");
  setFont(tx, fam, style); tx.pointSize = pt(size); tx.leading = pt(lead || size * 1.2);
  tx.fillColor = color || C.ink;
  if (extra) tx.properties = extra;
  return tx;
}
function sideX(page) { return page.side == PageSideOptions.LEFT_HAND ? "L" : "R"; }
function innerLeft(page) { return sideX(page) == "L" ? M.outside : M.inside; }
function textBounds(page) {
  var l = innerLeft(page);
  return [M.top, l, H - M.bottom, W - (sideX(page) == "L" ? M.inside : M.outside)];
}
function placeImage(page, file, b, fitMode) {
  var r = rect(page, b);
  try { r.place(File(file)); } catch (e) { log("place failed " + file + " " + e); return r; }
  r.fit(fitMode || FitOptions.FILL_PROPORTIONALLY);
  if (!fitMode || fitMode == FitOptions.FILL_PROPORTIONALLY) r.fit(FitOptions.CENTER_CONTENT);
  return r;
}

// ------------------------------------------------------------------ styles
var BASE = pstyle("IMB Base", {
  appliedFont: FONT.serif, fontStyle: "Regular", pointSize: pt(9), leading: pt(12), fillColor: C.ink,
  hyphenation: true, hyphenateWordsLongerThan: 6, hyphenateCapitalizedWords: false, hyphenateLastWord: false,
  justification: Justification.LEFT_ALIGN, kerningMethod: "Optical", composer: "Adobe Paragraph Composer",
  spaceBefore: 0, spaceAfter: 0
});
cstyle("Bold", { fontStyle: "Bold" });
cstyle("Italic", { fontStyle: "Italic" });

function chapterStyles(ch) {
  var A = acc(ch), s = "-" + ch.id;
  cstyle("QNum" + s, { appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(10.5), fillColor: A });
  cstyle("OptL" + s, { appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(8.2), fillColor: A });
  cstyle("ANum" + s, { appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(9.5), fillColor: C.ink });
  cstyle("ALetter" + s, { appliedFont: FONT.disp, fontStyle: "Bold", pointSize: pt(8), fillColor: C.white,
    underline: true, underlineColor: A, underlineWeight: pt(9.4), underlineOffset: pt(-2.9), underlineTint: 100 });
  cstyle("AOpt" + s, { appliedFont: FONT.sans, fontStyle: "Semibold", fillColor: A });
  cstyle("Kicker" + s, { appliedFont: FONT.disp, fontStyle: "Semibold", fillColor: A });

  var span = { spanColumnType: SpanColumnTypeOptions.SPAN_COLUMNS, spanSplitColumnCount: SpanColumnCountOptions.ALL };
  var p = function (n, props) { if (!props.basedOn) props.basedOn = BASE; return pstyle(n + s, props); };
  var bk = p("BankKicker", { appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(7), leading: pt(9), tracking: 140,
    fillColor: A, spaceBefore: mm(9), keepWithNext: 2, hyphenation: false, startParagraph: StartParagraph.ANYWHERE });
  bk.properties = span;
  var bh = p("BankHead", { appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(24), leading: pt(25),
    fillColor: C.ink, spaceAfter: mm(5.5), keepWithNext: 2, hyphenation: false,
    ruleBelow: true, ruleBelowColor: A, ruleBelowWeight: pt(2.2), ruleBelowOffset: mm(2.4), ruleBelowWidth: RuleWidth.COLUMN_WIDTH,
    ruleBelowRightIndent: mm(150) });
  bh.properties = span;
  p("SetHead", { appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(7.5), leading: pt(9), tracking: 120, capitalization: Capitalization.ALL_CAPS,
    fillColor: A, spaceBefore: mm(3), spaceAfter: mm(1), keepWithNext: 2, hyphenation: false });
  var q = p("Q", { appliedFont: FONT.serif, fontStyle: "Regular", pointSize: pt(8.9), leading: pt(11.8), leftIndent: mm(7.5),
    firstLineIndent: mm(-7.5), spaceBefore: mm(3.4), spaceAfter: mm(1), keepWithNext: 2, keepFirstLines: 2, keepLastLines: 2 });
  q.tabStops.add({ position: mm(7.5), alignment: TabStopAlignment.LEFT_ALIGN });
  var ql = p("QLast", { basedOn: q, spaceAfter: mm(3), keepWithNext: 0 });
  var o = p("Opt", { appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(8.5), leading: pt(10.6), leftIndent: mm(12.5),
    firstLineIndent: mm(-5), spaceAfter: mm(0.35), keepWithNext: 1, hyphenation: false, fillColor: C.ink2 });
  o.tabStops.add({ position: mm(12.5), alignment: TabStopAlignment.LEFT_ALIGN });
  p("OptLast", { basedOn: o, keepWithNext: 0, spaceAfter: mm(1.2) });
  p("QImage", { justification: Justification.LEFT_ALIGN, leftIndent: mm(7.5), spaceBefore: mm(1), spaceAfter: mm(1.2), keepWithNext: 1, leading: pt(10) });
  var et = p("EmqTheme", { appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(10), leading: pt(12), fillColor: C.white,
    spaceBefore: mm(6), spaceAfter: mm(2.2), keepWithNext: 3, hyphenation: false, leftIndent: mm(15), firstLineIndent: mm(-15),
    paragraphShadingOn: true, paragraphShadingColor: A, paragraphShadingTint: 100,
    paragraphShadingTopOffset: mm(1.6), paragraphShadingBottomOffset: mm(1.4), paragraphShadingLeftOffset: mm(2), paragraphShadingRightOffset: mm(2),
    paragraphShadingTopOrigin: ParagraphShadingTopOriginEnum.ASCENT_TOP_ORIGIN, paragraphShadingBottomOrigin: ParagraphShadingBottomOriginEnum.DESCENT_BOTTOM_ORIGIN,
    paragraphShadingWidth: ParagraphShadingWidthEnum.COLUMN_WIDTH });
  et.tabStops.add({ position: mm(15), alignment: TabStopAlignment.LEFT_ALIGN });
  var eo = p("EmqOpt", { appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(8.4), leading: pt(10.8), leftIndent: mm(8),
    firstLineIndent: mm(-6), keepWithNext: 1, hyphenation: false, spaceAfter: 0,
    paragraphShadingOn: true, paragraphShadingColor: A, paragraphShadingTint: 9,
    paragraphShadingTopOffset: mm(0.9), paragraphShadingBottomOffset: mm(0.9), paragraphShadingLeftOffset: mm(2), paragraphShadingRightOffset: mm(2),
    paragraphShadingTopOrigin: ParagraphShadingTopOriginEnum.ASCENT_TOP_ORIGIN, paragraphShadingBottomOrigin: ParagraphShadingBottomOriginEnum.DESCENT_BOTTOM_ORIGIN,
    paragraphShadingWidth: ParagraphShadingWidthEnum.COLUMN_WIDTH });
  eo.tabStops.add({ position: mm(8), alignment: TabStopAlignment.LEFT_ALIGN });
  p("EmqOptLast", { basedOn: eo, keepWithNext: 1, spaceAfter: mm(2.6) });
  p("EmqLead", { appliedFont: FONT.serif, fontStyle: "Italic", pointSize: pt(8), leading: pt(10), fillColor: C.muted, spaceAfter: mm(0.5), keepWithNext: 2 });
  var ah = p("AnsHead", { appliedFont: FONT.disp, fontStyle: "Condensed Bold", pointSize: pt(14), leading: pt(16), fillColor: A,
    spaceBefore: mm(8), spaceAfter: mm(3), keepWithNext: 2, hyphenation: false,
    ruleAbove: true, ruleAboveColor: A, ruleAboveWeight: pt(0.8), ruleAboveOffset: mm(4.5), ruleAboveWidth: RuleWidth.COLUMN_WIDTH });
  ah.properties = span;
  var tw = (W - M.inside - M.outside);
  ah.tabStops.add({ position: mm(tw), alignment: TabStopAlignment.RIGHT_ALIGN });
  cstyle("AnsHeadBank" + s, { appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(7.5), tracking: 100, capitalization: Capitalization.ALL_CAPS, fillColor: C.muted });
  var an = p("Ans", { appliedFont: FONT.sans, fontStyle: "Regular", pointSize: pt(8.3), leading: pt(10.7), leftIndent: mm(7.5),
    firstLineIndent: mm(-7.5), spaceAfter: mm(1.9), fillColor: C.ink });
  an.tabStops.add({ position: mm(7.5), alignment: TabStopAlignment.LEFT_ALIGN });
}

// ------------------------------------------------------------------ masters
function masterFor(ch) {
  var name = ch ? ch.id.toUpperCase() : "BODY";
  var ms = doc.masterSpreads.add({ namePrefix: name.substr(0, 4), baseName: ch ? ch.short : "Body", showMasterItems: true });
  ms.pages[0].marginPreferences.properties = { top: mm(M.top), bottom: mm(M.bottom), left: mm(M.outside), right: mm(M.inside), columnCount: 2, columnGutter: mm(GUT) };
  ms.pages[1].marginPreferences.properties = { top: mm(M.top), bottom: mm(M.bottom), left: mm(M.inside), right: mm(M.outside), columnCount: 2, columnGutter: mm(GUT) };
  var A = ch ? acc(ch) : C.ink;
  for (var i = 0; i < 2; i++) {
    var pg = ms.pages[i], L = (i == 0);
    var outerX = L ? 0 : W, sign = L ? 1 : -1;
    // header hairline + labels
    var hl = pg.graphicLines.add({ geometricBounds: [mm(14.2), mm(L ? M.outside : M.inside), mm(14.2), mm(W - (L ? M.inside : M.outside))] });
    hl.strokeWeight = pt(0.5); hl.strokeColor = C.line;
    var hb = [8.4, L ? M.outside : M.inside, 13.2, W - (L ? M.inside : M.outside)];
    var t1 = tframe(pg, hb, ch ? (ch.part + "  /  " + ch.title).toUpperCase() : MAN.book.title.toUpperCase());
    T(t1, FONT.disp, "Semibold", 6.8, 8, C.muted, { tracking: 120, justification: L ? Justification.LEFT_ALIGN : Justification.RIGHT_ALIGN });
    t1.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
    if (ch) {
      var tv = doc.textVariables.itemByName("Bank " + ch.id);
      var t2 = tframe(pg, hb, "");
      t2.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
      t2.parentStory.insertionPoints[-1].textVariableInstances.add({ associatedTextVariable: tv });
      T(t2, FONT.disp, "Condensed Bold", 8.5, 9, A, { justification: L ? Justification.RIGHT_ALIGN : Justification.LEFT_ALIGN });
    }
    // folio chip
    var fy = H - 13.6;
    var chipW = 13;
    var fx = L ? M.outside : W - M.outside - chipW;
    var chip = rect(pg, [fy, fx, fy + 6, fx + chipW], A);
    var fn = tframe(pg, [fy, fx, fy + 6, fx + chipW], "");
    fn.parentStory.insertionPoints[0].contents = SpecialCharacters.AUTO_PAGE_NUMBER;
    T(fn, FONT.disp, "Condensed Bold", 9.5, 10, C.white, { justification: Justification.CENTER_ALIGN });
    fn.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
    var ft = tframe(pg, [fy, L ? fx + chipW + 3 : M.inside, fy + 6, L ? W - M.inside : fx - 3], MAN.book.title.toUpperCase() + "   /   " + MAN.book.volume.toUpperCase());
    T(ft, FONT.disp, "Semibold", 6.5, 8, C.muted, { tracking: 140, justification: L ? Justification.LEFT_ALIGN : Justification.RIGHT_ALIGN });
    ft.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
    // thumb tab on the outer edge (position by chapter order)
    if (ch) {
      var tabH = 27, y0 = 26 + (ch.order - 1) * (tabH + 1.5);
      var tb = L ? [y0, -BLEED, y0 + tabH, 7] : [y0, W - 7, y0 + tabH, W + BLEED];
      rect(pg, tb, A);
      var tl = tframe(pg, [y0, L ? 0 : W - 7, y0 + tabH, L ? 7 : W], ("0" + ch.order).slice(-2));
      T(tl, FONT.disp, "Condensed Bold", 11, 12, C.white, { justification: Justification.CENTER_ALIGN });
      tl.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
      tl.rotationAngle = L ? 90 : -90;
    }
  }
  return ms;
}

// ------------------------------------------------------------------ page helpers
// Each part is its own document. START = printed number of its first page; the first page of the
// document (created with it) is reused by the first addPage() call so no blank page is left behind.
var START = OPTS.startPage || 1;
var REUSE = null;
function nextPageNumber() { return START + (REUSE ? 0 : doc.pages.length); }
function addPage(master) {
  var pg;
  if (REUSE) { pg = REUSE; REUSE = null; } else pg = doc.pages.add(LocationOptions.AT_END);
  pg.appliedMaster = master || NothingEnum.NOTHING;
  return pg;
}
function ensureSide(side, master) {   // make the NEXT page be `side` ("L"/"R") by adding a notes page
  var nextSide = (nextPageNumber() % 2 == 0) ? "L" : "R";
  if (nextSide != side) notesPage(master);
}
function notesPage(master) {
  var pg = addPage(master);
  var b = textBounds(pg);
  var t = tframe(pg, [b[0] + 2, b[1], b[0] + 10, b[3]], "NOTES");
  T(t, FONT.disp, "Condensed Bold", 18, 20, C.muted);
  for (var y = b[0] + 20; y < b[2] - 2; y += 8.5) {
    var ln = pg.graphicLines.add({ geometricBounds: [mm(y), mm(b[1]), mm(y), mm(b[3])] });
    ln.strokeWeight = pt(0.35); ln.strokeColor = C.line;
  }
  return pg;
}
function flowText(file, master, ch) {
  var pg = addPage(master);
  var tf = pg.textFrames.add({ geometricBounds: textBounds(pg) });
  tf.textFramePreferences.textColumnCount = 2; tf.textFramePreferences.textColumnGutter = mm(GUT);
  tf.textFramePreferences.insetSpacing = [0, 0, 0, 0];
  var f = File(file);
  with (app.taggedTextImportPreferences) { removeTextFormatting = false; styleConflict = StyleConflict.PUBLICATION_DEFINITION; useTypographersQuotes = true; }
  tf.place(f, false);
  var story = tf.parentStory, guard = 0;
  while (tf.overflows && guard++ < 900) {
    var np = addPage(master);
    var nf = np.textFrames.add({ geometricBounds: textBounds(np) });
    nf.textFramePreferences.textColumnCount = 2; nf.textFramePreferences.textColumnGutter = mm(GUT);
    nf.textFramePreferences.insetSpacing = [0, 0, 0, 0];
    tf.nextTextFrame = nf; tf = nf;
  }
  return story;
}

// ------------------------------------------------------------------ inline images  [[IMG:q/g0001.png]]
function inlineImages(story) {
  app.findGrepPreferences = NothingEnum.NOTHING; app.changeGrepPreferences = NothingEnum.NOTHING;
  app.findGrepPreferences.findWhat = "\\[\\[IMG:([^\\]]+)\\]\\]";
  var found = story.findGrep();
  var colW = (W - M.inside - M.outside - GUT) / 2 - 8;
  for (var i = found.length - 1; i >= 0; i--) {
    var t = found[i], name = t.contents.replace(/^\[\[IMG:/, "").replace(/\]\]$/, "");
    var ip = t.insertionPoints[0];
    t.contents = "";
    try {
      var g = ip.place(File(ROOT + "/assets/" + name))[0];
      var fr = g.parent;
      var gb = g.geometricBounds, gw = gb[3] - gb[1], gh = gb[2] - gb[0];
      var w = Math.min(colW, gw), h = gh * w / gw;
      if (h > 58) { h = 58; w = gw * h / gh; }
      var fb = fr.geometricBounds;
      fr.geometricBounds = [fb[0], fb[1], fb[0] + h, fb[1] + w];
      fr.fit(FitOptions.PROPORTIONALLY); fr.fit(FitOptions.FRAME_TO_CONTENT);
      fr.strokeColor = C.line; fr.strokeWeight = pt(0.5);
    } catch (e) { log("inline image failed " + name + ": " + e); }
  }
}

// ------------------------------------------------------------------ hyperlinks Q <-> A
var DEST = {};  // key -> {q: dest, a: dest}
function linkQA(story, ch) {
  app.findGrepPreferences = NothingEnum.NOTHING;
  app.findGrepPreferences.findWhat = ".+";
  app.findGrepPreferences.appliedCharacterStyle = doc.characterStyles.itemByName("QNum-" + ch.id);
  var qs = story.findGrep();
  app.findGrepPreferences.appliedCharacterStyle = doc.characterStyles.itemByName("ANum-" + ch.id);
  var as = story.findGrep();
  app.findGrepPreferences = NothingEnum.NOTHING;
  if (qs.length != ch.questions.length || as.length != ch.answers.length) log("QA count mismatch " + ch.id + " q " + qs.length + "/" + ch.questions.length + " a " + as.length + "/" + ch.answers.length);
  var n = Math.min(qs.length, ch.questions.length);
  var qd = {};
  for (var i = 0; i < n; i++) {
    var k = ch.questions[i].key;
    qd[k] = { text: qs[i], dest: doc.hyperlinkTextDestinations.add(qs[i], { name: "Q " + k }) };
  }
  for (var j = 0; j < Math.min(as.length, ch.answers.length); j++) {
    var ka = ch.answers[j].key;
    var ad = doc.hyperlinkTextDestinations.add(as[j], { name: "A " + ka });
    if (qd[ka]) {
      try {
        var s1 = doc.hyperlinkTextSources.add(qd[ka].text);
        doc.hyperlinks.add(s1, ad, { name: "Q>A " + ka, visible: false });
        var s2 = doc.hyperlinkTextSources.add(as[j]);
        doc.hyperlinks.add(s2, qd[ka].dest, { name: "A>Q " + ka, visible: false });
      } catch (e) { log("link " + ka + " " + e); }
    }
  }
  return qd;
}

// ------------------------------------------------------------------ chapter opener (spread: photo left, title right)
function chapterOpener(ch, master) {
  var A = acc(ch);
  ensureSide("L", null);
  var L = addPage(null), R = addPage(null);
  // ---- left: full-bleed duotone photo, ink fade at the bottom, giant number
  var img = ch.divider && ch.divider.image ? ROOT + "/assets/" + ch.divider.image : null;
  rect(L, [-BLEED, -BLEED, H + BLEED, W + BLEED], C.ink);
  if (img && File(img).exists) placeImage(L, img, [-BLEED, -BLEED, H + BLEED, W + BLEED]);
  var kick = tframe(L, [16, 16, 22, 150], "CHAPTER  " + ("0" + ch.order).slice(-2) + "  /  " + ch.part.toUpperCase());
  T(kick, FONT.disp, "Semibold", 7.5, 9, C.white, { tracking: 260 });
  var big = tframe(L, [H - 150, 10, H - 42, W - 10], ("0" + ch.order).slice(-2));
  T(big, FONT.disp, "ExtraCondensed Black", 300, 250, A);
  big.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
  big.parentStory.texts[0].strokeColor = mixTint(A);
  var nm = tframe(L, [H - 38, 16, H - 20, W - 16], ch.title.toUpperCase());
  T(nm, FONT.disp, "Condensed Bold", 20, 21, C.white, { tracking: 40 });
  var credit = tframe(L, [H - 10, 16, H - 6, W - 16], ch.divider && ch.divider.credit ? ch.divider.credit : "");
  T(credit, FONT.sans, "Regular", 5.5, 7, C.white, { justification: Justification.RIGHT_ALIGN });
  credit.transparencySettings.blendingSettings.opacity = 55;

  // ---- right: title block, intro, stats, contents
  rect(R, [-BLEED, W - 9, H + BLEED, W + BLEED], A);
  var ghost = tframe(R, [150, 60, H + 20, W + 40], ("0" + ch.order).slice(-2));
  T(ghost, FONT.disp, "ExtraCondensed Black", 420, 360, A);
  ghost.transparencySettings.blendingSettings.opacity = 6;
  ghost.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
  var x0 = 22, x1 = W - 26;
  var part = tframe(R, [30, x0, 36, x1], (ch.part).toUpperCase());
  T(part, FONT.disp, "Semibold", 8, 10, A, { tracking: 240 });
  var ttl = tframe(R, [38, x0, 92, x1], ch.title);
  T(ttl, FONT.disp, "ExtraCondensed Black", 64, 58, C.ink, { hyphenation: false });
  ttl.textFramePreferences.autoSizingReferencePoint = AutoSizingReferenceEnum.TOP_CENTER_POINT;
  ttl.textFramePreferences.autoSizingType = AutoSizingTypeEnum.HEIGHT_ONLY;
  var tb = ttl.geometricBounds, ty = tb[2] + 5;
  var rl = R.graphicLines.add({ geometricBounds: [mm(ty), mm(x0), mm(ty), mm(x0 + 28)] });
  rl.strokeColor = A; rl.strokeWeight = pt(3);
  var chDest = doc.paragraphDestinations.add(ttl.parentStory.paragraphs[0], { name: "CH " + ch.id });
  var y = ty + 7;
  if (ch.intro) {
    var intro = tframe(R, [y, x0, y + 40, x1 - 12], ch.intro);
    T(intro, FONT.serif, "Light", 12, 16.5, C.ink2);
    intro.textFramePreferences.autoSizingReferencePoint = AutoSizingReferenceEnum.TOP_CENTER_POINT;
    intro.textFramePreferences.autoSizingType = AutoSizingTypeEnum.HEIGHT_ONLY;
    y = intro.geometricBounds[2] + 9;
  }
  var stats = [[String(ch.n_mcq), "MCQs"], [String(ch.n_emq), "EMQ items"], [String(ch.banks.length), "Question sets"], [String(ch.summaries.length), "Summary figures"]];
  var sw = (x1 - x0) / 4;
  for (var i = 0; i < stats.length; i++) {
    var sx = x0 + i * sw;
    var sr = R.graphicLines.add({ geometricBounds: [mm(y), mm(sx), mm(y), mm(sx + sw - 5)] });
    sr.strokeColor = i == 0 ? A : C.line; sr.strokeWeight = pt(i == 0 ? 2 : 0.8);
    var n = tframe(R, [y + 3, sx, y + 17, sx + sw - 4], stats[i][0]);
    T(n, FONT.disp, "Condensed Bold", 36, 36, i == 0 ? A : C.ink);
    var l = tframe(R, [y + 18, sx, y + 22, sx + sw - 4], stats[i][1].toUpperCase());
    T(l, FONT.disp, "Semibold", 6.5, 8, C.muted, { tracking: 140 });
  }
  y += 34;
  var inTitle = tframe(R, [y, x0, y + 6, x1], "IN THIS CHAPTER");
  T(inTitle, FONT.disp, "Semibold", 7.5, 9, A, { tracking: 240 });
  var list = tframe(R, [y + 9, x0, H - 22, x1], "");
  return { left: L, right: R, list: list, dest: chDest };
}
function mixTint(c) { return c; }

// ------------------------------------------------------------------ essentials (summary images)
function essentials(ch, master) {
  if (!ch.summaries || !ch.summaries.length) return;
  var A = acc(ch);
  var items = ch.summaries.slice(0);
  var first = true;
  while (items.length) {
    var pg = addPage(master);
    var b = textBounds(pg), y = b[0];
    if (first) {
      var k = tframe(pg, [y, b[1], y + 5, b[3]], "CHAPTER ESSENTIALS  •  SUMMARIES, APPROACHES & ALGORITHMS");
      T(k, FONT.disp, "Semibold", 7, 9, A, { tracking: 140 });
      var t = tframe(pg, [y + 6, b[1], y + 18, b[3]], "Essentials at a glance");
      T(t, FONT.disp, "Condensed Bold", 24, 25, C.ink);
      var rl = pg.graphicLines.add({ geometricBounds: [mm(y + 20), mm(b[1]), mm(y + 20), mm(b[1] + 24)] });
      rl.strokeColor = A; rl.strokeWeight = pt(2.2);
      y += 25; first = false;
    }
    var avail = b[2] - y, colW = b[3] - b[1];
    // fit as many as possible on the page, each scaled to page width (max), stacked
    var placed = 0;
    while (items.length) {
      var it = items[0];
      var f = File(ROOT + "/assets/" + it.image);
      if (!f.exists) { items.shift(); continue; }
      var r = rect(pg, [y, b[1], y + 10, b[1] + colW]);
      r.place(f);
      var gr = r.graphics[0], gb = gr.geometricBounds, gw = gb[3] - gb[1], gh = gb[2] - gb[0];
      var w = colW, h = gh * w / gw;
      if (h > (b[2] - b[0]) - 30) { h = (b[2] - b[0]) - 30; w = gw * h / gh; }
      if (placed > 0 && h + 4 > b[2] - y) { r.remove(); break; }
      var x0 = b[1] + (colW - w) / 2;
      r.geometricBounds = [mm(y), mm(x0), mm(y + h), mm(x0 + w)];
      r.fit(FitOptions.PROPORTIONALLY); r.fit(FitOptions.CENTER_CONTENT);
      r.strokeColor = C.line; r.strokeWeight = pt(0.5);
      y += h + 6; placed++; items.shift();
    }
  }
}

// ------------------------------------------------------------------ chapter contents list on opener
function fillOpenerList(op, ch, story) {
  var A = acc(ch);
  app.findGrepPreferences = NothingEnum.NOTHING;
  app.findGrepPreferences.findWhat = ".+";
  app.findGrepPreferences.appliedParagraphStyle = doc.paragraphStyles.itemByName("BankHead-" + ch.id);
  var heads = story.findGrep();
  app.findGrepPreferences = NothingEnum.NOTHING;
  var fmt = doc.crossReferenceFormats.itemByName("Page Number");
  var st = op.list.parentStory;
  var dests = [];
  for (var i = 0; i < heads.length && i < ch.banks.length; i++) {
    var d = doc.paragraphDestinations.add(heads[i].paragraphs[0], { name: "BANK " + ch.banks[i].key });
    dests.push(d);
    ch.banks[i].dest = d;
  }
  var lstyle = pstyle("OpenerList-" + ch.id, { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Condensed Semibold", pointSize: pt(13), leading: pt(15),
    fillColor: C.ink, spaceAfter: mm(2.6), hyphenation: false, ruleBelow: true, ruleBelowColor: C.line, ruleBelowWeight: pt(0.4), ruleBelowOffset: mm(1.3) });
  lstyle.tabStops.everyItem().remove();
  lstyle.tabStops.add({ position: mm(11), alignment: TabStopAlignment.LEFT_ALIGN });
  lstyle.tabStops.add({ position: mm(128), alignment: TabStopAlignment.RIGHT_ALIGN });
  lstyle.tabStops.add({ position: mm(162), alignment: TabStopAlignment.RIGHT_ALIGN });
  for (var j = 0; j < dests.length; j++) {
    var ip = st.insertionPoints[-1];
    ip.contents = ("0" + (j + 1)).slice(-2) + "\t" + ch.banks[j].title + "\t" + ch.banks[j].count + " Q\t";
    var srcIP = st.insertionPoints[-1];
    try {
      var src = doc.crossReferenceSources.add(srcIP, fmt);
      doc.hyperlinks.add(src, dests[j], { visible: false });
    } catch (e) { log("xref " + e); }
    if (j < dests.length - 1) st.insertionPoints[-1].contents = "\r";
  }
  st.texts[0].appliedParagraphStyle = lstyle;
  for (var k = 0; k < st.paragraphs.length; k++) {
    var pgf = st.paragraphs[k];
    try { var w0 = pgf.words[0]; w0.fillColor = A; w0.fontStyle = "Condensed Bold"; } catch (e) {}
  }
  // high-yield topics: the most-examined topics in this chapter
  var cnt = {}, order = [];
  for (var q = 0; q < ch.questions.length; q++) {
    var ix = ch.questions[q].ix || [];
    for (var e = 0; e < ix.length; e++) if (!ix[e][1]) { var t = ix[e][0]; if (!cnt[t]) { cnt[t] = 0; order.push(t); } cnt[t]++; }
  }
  order.sort(function (a, b) { return cnt[b] - cnt[a]; });
  var top = order.slice(0, 12);
  if (top.length) {
    var hy = pstyle("OpenerHY-" + ch.id, { basedOn: BASE, appliedFont: FONT.disp, fontStyle: "Semibold", pointSize: pt(7.5), leading: pt(9), tracking: 240,
      fillColor: A, spaceBefore: mm(7), spaceAfter: mm(1.5), hyphenation: false });
    var hb = pstyle("OpenerHYList-" + ch.id, { basedOn: BASE, appliedFont: FONT.sans, fontStyle: "Semibold", pointSize: pt(8.6), leading: pt(12.5), fillColor: C.ink2, hyphenation: false });
    st.insertionPoints[-1].contents = "\rHIGH-YIELD TOPICS";
    st.paragraphs[-1].appliedParagraphStyle = hy;
    st.insertionPoints[-1].contents = "\r" + top.join("   /   ");
    st.paragraphs[-1].appliedParagraphStyle = hb;
  }
  // shorten the high-yield list until the opener fits
  var guardHY = 0;
  while (st.overflows && top.length > 3 && guardHY++ < 12) {
    top.pop();
    st.paragraphs[-1].contents = top.join("   /   ");
  }
  if (st.overflows && top.length) { st.paragraphs[-1].remove(); st.paragraphs[-1].remove(); }
  if (st.overflows) log("opener list overset " + ch.id);
  return dests;
}

// ------------------------------------------------------------------ BUILD (one part per run)
// OPTS.part = "front" | "back" | <chapter id>.  Every run writes output/parts/<part>.json with its
// page range, bank start pages and question positions; front/back read those files, so page
// numbers are continuous across the separate documents.
var PARTSDIR = OUTDIR + "/parts";
Folder(PARTSDIR).create();
function readJSON(p) { var f = File(p); if (!f.exists) return null; return eval('(' + readText(p) + ')'); }
function toJSON(v) {
  if (v === null || v === undefined) return "null";
  if (typeof v == "number" || typeof v == "boolean") return String(v);
  if (typeof v == "string") return '"' + v.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/[\r\n\t]/g, " ") + '"';
  if (v instanceof Array) { var a = []; for (var i = 0; i < v.length; i++) a.push(toJSON(v[i])); return "[" + a.join(",") + "]"; }
  var o = []; for (var k in v) if (v.hasOwnProperty(k) && typeof v[k] != "function") o.push(toJSON(k) + ":" + toJSON(v[k])); return "{" + o.join(",") + "}";
}
var PART = OPTS.part;
var chaps = MAN.chapters;
for (var i = 0; i < chaps.length; i++) {
  chapterStyles(chaps[i]);
  var tv = doc.textVariables.add({ name: "Bank " + chaps[i].id, variableType: VariableTypes.MATCH_PARAGRAPH_STYLE_TYPE });
  tv.variableOptions.appliedParagraphStyle = doc.paragraphStyles.itemByName("BankHead-" + chaps[i].id);
  tv.variableOptions.searchStrategy = SearchStrategies.FIRST_ON_PAGE;
}
// continuous numbering: this document starts at START
with (doc.sections[0]) { continueNumbering = false; pageNumberStart = START; }
doc.pages[0].appliedMaster = NothingEnum.NOTHING;
var INFO = { part: PART, start: START };
log("start " + PART + " at page " + START);

if (PART == "front") {
  // all chapter + back part files must already exist
  for (var i = 0; i < chaps.length; i++) chaps[i].info = readJSON(PARTSDIR + "/" + chaps[i].id + ".json");
  var BACKINFO = readJSON(PARTSDIR + "/back.json");
  $.evalFile(File(ROOT + "/build/front.jsx"));
  try { fillContents(); } catch (e) { log("fillContents " + e); }
} else if (PART == "back") {
  for (var i = 0; i < chaps.length; i++) chaps[i].info = readJSON(PARTSDIR + "/" + chaps[i].id + ".json");
  REUSE = doc.pages[0];
  $.evalFile(File(ROOT + "/build/back.jsx"));
  INFO.indexPage = BACK.indexPage; INFO.creditsPage = BACK.creditsPage;
} else {
  var ch = null;
  for (var i = 0; i < chaps.length; i++) if (chaps[i].id == PART) ch = chaps[i];
  if (!ch) throw new Error("unknown part " + PART);
  REUSE = doc.pages[0];
  var ms = masterFor(ch);
  var op = chapterOpener(ch, ms);
  essentials(ch, ms);
  var story = flowText(ch.file, ms, ch);
  inlineImages(story);
  ch.qd = linkQA(story, ch);
  fillOpenerList(op, ch, story);
  // record positions for contents / index / merge tool
  INFO.id = ch.id; INFO.title = ch.title; INFO.order = ch.order; INFO.part_title = ch.part;
  INFO.banks = [];
  for (var b = 0; b < ch.banks.length; b++) {
    var bp = null;
    try { bp = ch.banks[b].dest.destinationText.parentTextFrames[0].parentPage.name; } catch (e) {}
    INFO.banks.push({ key: ch.banks[b].key, title: ch.banks[b].title, count: ch.banks[b].count, page: bp ? parseInt(bp, 10) : null });
  }
  INFO.questions = [];
  for (var q = 0; q < ch.questions.length; q++) {
    var hit = ch.qd[ch.questions[q].key];
    if (!hit) continue;
    try {
      var tx = hit.text, pgn = parseInt(tx.parentTextFrames[0].parentPage.name, 10);
      INFO.questions.push({ key: ch.questions[q].key, page: pgn, y: Math.round((tx.baseline - 4) * 10) / 10 });
    } catch (e) {}
  }
}
// remove empty trailing text frames' pages (overflow loop can leave an empty frame)
// (front matter keeps its fixed 7 pages, even an unused second contents page)
for (var p = doc.pages.length - 1; p > 0 && PART != "front"; p--) {
  var pg = doc.pages[p];
  if (pg.textFrames.length == 1 && pg.pageItems.length == 1 && pg.textFrames[0].characters.length == 0) { pg.remove(); }
}

// a chapter part must end on a right-hand (odd) page so the next part opens on a left page
if (PART != "front" && PART != "back") { var lastNo = START + doc.pages.length - 1; if (lastNo % 2 == 0) notesPage(doc.masterSpreads[doc.masterSpreads.length - 1]); }
INFO.pages = doc.pages.length; INFO.end = START + doc.pages.length - 1;
writeText(PARTSDIR + "/" + PART + ".json", toJSON(INFO));
log(PART + " pages " + INFO.start + "-" + INFO.end);

// ------------------------------------------------------------------ save / export
Folder(OUTDIR).create();
var base = PARTSDIR + "/" + OPTS.name;
log("saving"); doc.save(File(base + ".indd")); log("saved");
if (OPTS.idml) { doc.exportFile(ExportFormat.INDESIGN_MARKUP, File(base + ".idml")); log("idml done"); }
if (OPTS.pdf) {
  with (app.pdfExportPreferences) {
    pageRange = PageRange.ALL_PAGES; includeHyperlinks = true; includeBookmarks = true; exportReaderSpreads = false;
    useDocumentBleedWithPDF = false; cropMarks = false; bleedMarks = false; colorBitmapSampling = Sampling.BICUBIC_DOWNSAMPLE;
    colorBitmapSamplingDPI = OPTS.dpi || 150; thresholdToCompressColor = (OPTS.dpi || 150) * 1.5;
    colorBitmapCompression = BitmapCompression.AUTO_COMPRESSION; colorBitmapQuality = CompressionQuality.MEDIUM;
    grayscaleBitmapSamplingDPI = OPTS.dpi || 150; viewPDF = false;
  }
  doc.exportFile(ExportFormat.PDF_TYPE, File(base + ".pdf"), false);
}
if (OPTS.jpg) {
  with (app.jpegExportPreferences) {
    jpegExportRange = ExportRangeOrAllPages.EXPORT_RANGE; pageString = OPTS.jpg; exportResolution = 60;
    jpegQuality = JPEGOptionsQuality.MEDIUM; exportingSpread = false;
  }
  Folder(OUTDIR + "/jpg").create();
  doc.exportFile(ExportFormat.JPG, File(OUTDIR + "/jpg/p.jpg"), false);
}
// overset / missing report
var over = 0; for (var s = 0; s < doc.stories.length; s++) if (doc.stories[s].overflows) over++;
log("pages " + doc.pages.length + " overset stories " + over);
writeText(OUTDIR + "/build_log.txt", LOG.join("\n"));
if (!OPTS.keepOpen) doc.close(SaveOptions.NO);
"ok " + LOG.length;
