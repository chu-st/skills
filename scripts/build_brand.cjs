/* Render GitHub artwork from the supplied chu.st design system.
   Usage: node scripts/build_brand.cjs <design-system-directory> <output-directory>
   Requires Playwright and Chromium. Fonts are rendered, not redistributed. */
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const [design, output] = process.argv.slice(2);
if (!design || !output) throw new Error('Provide design-system and output directories');
fs.mkdirSync(output, { recursive: true });
const read = p => fs.readFileSync(path.join(design, p));
const data = (p, type) => `data:${type};base64,${read(p).toString('base64')}`;
const logo = data('assets/chust-logo-inverse.svg','image/svg+xml');
const symbol = data('assets/chust-symb-inverse.svg','image/svg+xml');
const css = `@font-face{font-family:Uni;src:url('${data('fonts/UniSansHeavyCaps.ttf','font/ttf')}')}
@font-face{font-family:Roboto;src:url('${data('fonts/roboto/roboto-400-cyrillic.woff2','font/woff2')}');unicode-range:U+0400-052F}
@font-face{font-family:Roboto;src:url('${data('fonts/roboto/roboto-400-latin.woff2','font/woff2')}');unicode-range:U+0000-024F}
*{box-sizing:border-box}html,body{margin:0}body{font-family:Roboto,sans-serif;color:white;background:#0D5452}
.cover{width:1200px;height:630px;padding:56px 64px;position:relative;overflow:hidden}
.logo{width:425px;height:auto}.site{position:absolute;right:64px;top:57px;font-size:27px;color:#B0E1D4}
h1{font-family:Uni,sans-serif;font-size:76px;font-weight:900;text-transform:uppercase;line-height:1.06;margin:64px 0 24px;letter-spacing:.2px;max-width:1080px}
.lead{font-size:27px;line-height:1.4;margin:0;color:#E6EDED;max-width:1000px}
.bottom{position:absolute;bottom:48px;left:64px;right:64px;border-top:1px solid #19A8A3;padding-top:22px;font-size:22px;color:#B0E1D4;display:flex;justify-content:space-between;gap:20px}
.avatar{width:512px;height:512px;background:#137E7A;display:flex;align-items:center;justify-content:center}.avatar img{height:416px;width:auto}`;
const covers = {
  'skills-cover': {title:'Двухмодельная<br>проверка', lead:'Исследуйте вопросы. Проверяйте основания решений.', left:'Claude + Codex · Codex + Claude', right:'Вторую модель выбираете вы'},
  'organization-cover': {title:'Решения на данных,<br>усиленные ИИ', lead:'Открытые инструменты «Чувства управления».', left:'Исследования · Аналитика · Управление', right:'chu.st'}
};
(async () => {
  const options={headless:true};
  if (process.env.CHUST_BROWSER_BIN) options.executablePath=process.env.CHUST_BROWSER_BIN;
  const browser=await chromium.launch(options);
  try {
    const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
    for (const [name,c] of Object.entries(covers)) {
      await page.setContent(`<html lang="ru"><head><meta charset="utf-8"><style>${css}</style></head><body><main class="cover"><img class="logo" src="${logo}" alt="Чувство управления"><div class="site">chu.st</div><h1>${c.title}</h1><p class="lead">${c.lead}</p><div class="bottom"><span>${c.left}</span><span>${c.right}</span></div></main></body></html>`);
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({path:path.join(output,name+'.png')});
    }
    await page.setViewportSize({width:512,height:512});
    await page.setContent(`<html><head><style>${css}</style></head><body><div class="avatar"><img src="${symbol}" alt="chu.st"></div></body></html>`);
    await page.screenshot({path:path.join(output,'avatar.png')});
    for (const name of ['chust-logo.svg','chust-logo-inverse.svg']) fs.copyFileSync(path.join(design,'assets',name),path.join(output,name));
  } finally {await browser.close();}
})().catch(e => {console.error(e);process.exitCode=1});
