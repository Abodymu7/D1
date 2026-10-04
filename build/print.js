// usage: node print.js in.html out.pdf [in2.html out2.pdf ...]
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME || undefined });
  const ctx = await browser.newContext();
  const args = process.argv.slice(2);
  for (let i = 0; i < args.length; i += 2) {
    const page = await ctx.newPage();
    await page.goto('file://' + require('path').resolve(args[i]), { waitUntil: 'load', timeout: 600000 });
    await page.evaluate(async () => { await document.fonts.ready; });
    await page.pdf({ path: args[i + 1], preferCSSPageSize: true, printBackground: true, timeout: 0 });
    await page.close();
    console.log('ok', args[i + 1]);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
