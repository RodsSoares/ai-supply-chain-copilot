// Renderiza os fundos HUD (1920x1080) e grava layout.json com as posições dos painéis.
// Uso: node reports/powerbi/kit/backgrounds/src/render.js
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

(async () => {
  const out = path.resolve(__dirname, "..");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(__dirname, "backgrounds.html"));
  await page.waitForTimeout(1500);
  const layouts = await page.evaluate(() => window.LAYOUTS);
  for (const name of Object.keys(layouts)) {
    await page.evaluate((n) => window.renderPage(n), name);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(out, `bg_${name}.png`) });
    console.log(`bg_${name}.png`);
  }
  const layout = {};
  for (const [name, l] of Object.entries(layouts)) {
    layout[name] = l.panels.map(({ id, x, y, w, h }) => ({ id, x, y, largura: w, altura: h }));
  }
  fs.writeFileSync(path.join(out, "layout.json"), JSON.stringify(layout, null, 2) + "\n");
  await browser.close();
})();
