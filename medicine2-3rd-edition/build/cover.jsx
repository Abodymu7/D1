// Print cover spread: back | spine | front, A4 trim, spine from page count. Output: output/Cover-Spread.indd/.idml/.pdf
#target indesign
var ROOT = OPTS.root, OUTDIR = OPTS.outdir;
function readText(p) { var f = File(p); f.encoding = "UTF-8"; f.open("r"); var t = f.read(); f.close(); return t; }
var MAN = eval('(' + readText(ROOT + "/build/out/manifest.json") + ')');
var BK = MAN.book, ST = MAN.stats || {};
app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
var W = 210, H = 297, BLEED = 3;
var SPINE = Math.max(8, Math.round((OPTS.pages / 2) * 0.1 * 10) / 10 + 1);   // 80 gsm ≈ 0.1 mm per leaf + board allowance
var TW = W * 2 + SPINE;
var doc = app.documents.add(false);
with (doc.documentPreferences) { pageWidth = TW + "mm"; pageHeight = H + "mm"; facingPages = false; documentBleedTopOffset = BLEED + "mm"; documentBleedUniformSize = true; }
doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.MILLIMETERS; doc.viewPreferences.verticalMeasurementUnits = MeasurementUnits.MILLIMETERS;
var pg = doc.pages[0];
pg.marginPreferences.properties = { top: "0mm", bottom: "0mm", left: "0mm", right: "0mm", columnCount: 1 };
function sw(n, h) { var c = doc.colors.itemByName(n); if (c.isValid) return c; return doc.colors.add({ name: n, model: ColorModel.PROCESS, space: ColorSpace.RGB, colorValue: [parseInt(h.substr(0, 2), 16), parseInt(h.substr(2, 2), 16), parseInt(h.substr(4, 2), 16)] }); }
var INK = sw("IMB Ink", "0E1726"), GOLD = sw("IMB Gold", "E8B64C"), WHITE = sw("IMB White", "FFFFFF");
function R(b, fill) { var r = pg.rectangles.add({ geometricBounds: [b[0] + "mm", b[1] + "mm", b[2] + "mm", b[3] + "mm"] }); r.fillColor = fill || "None"; r.strokeColor = "None"; return r; }
function TF(b, s, fam, st, size, lead, col, extra) {
  var t = pg.textFrames.add({ geometricBounds: [b[0] + "mm", b[1] + "mm", b[2] + "mm", b[3] + "mm"] });
  t.textFramePreferences.insetSpacing = [0, 0, 0, 0]; t.contents = s;
  var x = t.parentStory.texts[0]; x.appliedFont = fam; x.fontStyle = st; x.pointSize = size + "pt"; x.leading = (lead || size * 1.2) + "pt"; x.fillColor = col || WHITE;
  if (extra) x.properties = extra; return t;
}
var DISP = "Acumin Variable Concept", SERIF = "Source Serif Variable";
function fmtN(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
var TOTAL = (ST.mcq || 0) + (ST.emq || 0), CH = [], TX = BK.texts || {};
function tx(k, d) { return TX[k] !== undefined ? TX[k] : d; }
function sub(s) { return String(s || "").replace(/\{total\}/g, fmtN(TOTAL)).replace(/\{corrected\}/g, fmtN(ST.corrected || 0)).replace(/\{new\}/g, String(ST.new || 0)).replace(/\{chapters\}/g, String(CH.length)); }
for (var i = 0; i < MAN.chapters.length; i++) if (!MAN.chapters[i].appendix) CH.push(MAN.chapters[i]);

R([-BLEED, -BLEED, H + BLEED, TW + BLEED], INK);
var FX = W + SPINE;                       // front panel x origin
var img = ROOT + "/assets/" + (BK.cover && BK.cover.image ? BK.cover.image : "dividers/cover.jpg");
if (File(img).exists) { var ph = R([-BLEED, FX, H + BLEED, TW + BLEED]); ph.place(File(img)); ph.fit(FitOptions.FILL_PROPORTIONALLY); ph.fit(FitOptions.CENTER_CONTENT); }
// ---- front (mirrors page 1 of the book)
TF([16, FX + 16, 21, TW - 16], (BK.team || "").toUpperCase() + "   /   " + BK.volume.toUpperCase() + "   /   " + BK.edition.toUpperCase(), DISP, "Semibold", 7.5, 9, GOLD, { tracking: 260 });
var CL = tx("cover_lines", String(BK.title).toUpperCase().split(" ").slice(0, 3));
for (var li = 0; li < CL.length && li < 3; li++) TF([34 + li * 36, FX + 13, 72 + li * 36, TW - 10], CL[li], DISP, "ExtraCondensed Black", 118, 100, li == CL.length - 1 ? GOLD : WHITE, { tracking: -10 });
TF([148, FX + 16, 170, FX + 150], sub(tx("tagline", "")), SERIF, "Light", 12.5, 16, WHITE);
var by = 222, bh = 34, bw = (W - 32) / CH.length;
for (var c = 0; c < CH.length; c++) {
  var bx = FX + 16 + c * bw, col = sw("IMB " + CH[c].id, CH[c].color);
  R([by, bx, by + bh, bx + bw - 1.2], col);
  TF([by + 2.5, bx + 2.5, by + 12, bx + bw - 3], ("0" + CH[c].order).slice(-2), DISP, "Condensed Bold", 16, 16, WHITE);
  var nm = TF([by + 17, bx + 2.5, by + bh - 2, bx + bw - 3], CH[c].short.toUpperCase(), DISP, "Condensed Bold", 7.2, 8.2, WHITE);
  nm.textFramePreferences.verticalJustification = VerticalJustification.BOTTOM_ALIGN;
}
TF([H - 30, FX + 16, H - 22, TW - 16], (BK.authors || []).join("   /   ").toUpperCase(), DISP, "Condensed Bold", 11, 13, WHITE, { tracking: 80 });
// ---- spine
for (var s = 0; s < CH.length; s++) R([H - 60 + s * 6, W, H - 54 + s * 6, W + SPINE], sw("IMB " + CH[s].id, CH[s].color));
var sp = TF([20, W, H - 70, W + SPINE], BK.title.toUpperCase() + "   /   " + BK.volume.toUpperCase(), DISP, "Condensed Bold", Math.min(14, SPINE * 1.6), Math.min(14, SPINE * 1.6), WHITE, { tracking: 120 });
sp.rotationAngle = -90; sp.geometricBounds = [20 + "mm", W + "mm", (H - 70) + "mm", (W + SPINE) + "mm"];
sp.textFramePreferences.verticalJustification = VerticalJustification.CENTER_ALIGN;
// ---- back
TF([30, 20, 36, W - 20], BK.title.toUpperCase() + "   /   " + BK.volume.toUpperCase(), DISP, "Semibold", 8, 10, GOLD, { tracking: 260 });
TF([40, 20, 100, W - 30], sub(tx("back_headline", BK.title)), DISP, "ExtraCondensed Black", 46, 44, WHITE);
var pts = tx("back_points", ["{total} questions with answers and explanations"]); for (var q = 0; q < pts.length; q++) pts[q] = sub(pts[q]);
var y = 108;
for (var p = 0; p < pts.length; p++) { R([y + 1.2, 20, y + 4.2, 23], GOLD); TF([y, 28, y + 12, W - 30], pts[p], SERIF, "Regular", 12, 15.5, WHITE); y += 16; }
TF([H - 34, 20, H - 20, W - 20], (BK.team || "") + "   " + (BK.telegram || "").replace(/^https?:\/\//, ""), DISP, "Semibold", 8, 11, WHITE, { tracking: 100 });
for (var k = 0; k < MAN.chapters.length; k++) R([H - 14, -BLEED + k * (W + BLEED) / MAN.chapters.length, H + BLEED, -BLEED + (k + 1) * (W + BLEED) / MAN.chapters.length], sw("IMB " + MAN.chapters[k].id, MAN.chapters[k].color));
// guides for folds
pg.guides.add({ orientation: HorizontalOrVertical.VERTICAL, location: W + "mm" });
pg.guides.add({ orientation: HorizontalOrVertical.VERTICAL, location: (W + SPINE) + "mm" });
var base = OUTDIR + "/Cover-Spread";
doc.save(File(base + ".indd"));
doc.exportFile(ExportFormat.INDESIGN_MARKUP, File(base + ".idml"));
app.pdfExportPreferences.pageRange = PageRange.ALL_PAGES;
app.pdfExportPreferences.useDocumentBleedWithPDF = true;
app.pdfExportPreferences.viewPDF = false;
doc.exportFile(ExportFormat.PDF_TYPE, File(base + ".pdf"), false);
doc.close(SaveOptions.NO);
"cover ok spine " + SPINE;
