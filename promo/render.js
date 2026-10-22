// Renders promo HTML frame-by-frame with headless Chromium.
// usage: node render.js <html> <outdir> [fps] [duration] [sampleTimes:comma-separated]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const [html, outdir, fpsArg, durArg, sample] = process.argv.slice(2);
  const fps = +fpsArg || 30, dur = +durArg || 35.5;
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
  const [hp, q] = html.split('?'); await page.goto('file://' + path.resolve(hp) + (q ? '?' + q : ''));
  await page.evaluate(() => document.fonts.ready);
  const times = sample ? sample.split(',').map(Number) : Array.from({ length: Math.round(dur * fps) }, (_, i) => i / fps);
  let i = 0;
  for (const t of times) {
    await page.evaluate(t => window.seek(t), t);
    const name = sample ? `t${t}.png` : `f${String(i).padStart(5, '0')}.png`;
    await page.screenshot({ path: path.join(outdir, name), type: 'png' });
    if (++i % 150 === 0) console.log('frames', i);
  }
  await browser.close();
  console.log('done', i);
})();
