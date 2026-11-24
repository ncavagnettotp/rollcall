// Manual Stage 1 browser acceptance, using the existing bundled Playwright runtime.
const {chromium} = require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const output = path.resolve('output/playwright');
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({headless:true, channel:'msedge'});
  const page = await browser.newPage({viewport:{width:1280,height:1000}});
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  try {
    await page.goto('http://127.0.0.1:5174');
    await page.getByText('API: Online', {exact:true}).waitFor();
    await page.getByText('PostgreSQL: Connected', {exact:true}).waitFor();
    for (const name of ['In Storage','Due Soon','Overdue','Needs Attention']) {
      await page.getByRole('heading', {name,exact:true}).waitFor();
    }
    assert(await page.getByRole('button',{name:'Upload Invoice'}).isDisabled());
    assert(await page.getByRole('searchbox').isDisabled());
    assert.equal(await page.getByText('—',{exact:true}).count(), 4);
    assert.equal(await page.getByText('Storage records will appear here',{exact:true}).count(), 1);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.screenshot({path:path.join(output,'stage1-desktop.png'),fullPage:true});
    const cards = page.getByRole('region',{name:'Storage categories'}).locator('article');
    assert.equal(await cards.count(),4);
    const bounds = await Promise.all([0,1,2,3].map(i => cards.nth(i).boundingBox()));
    assert.equal(bounds[0].y,bounds[1].y);
    assert(bounds[2].y > bounds[0].y);
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.screenshot({path:path.join(output,'stage1-mobile.png'),fullPage:true});
    await page.route('**/api/health/db', route => route.fulfill({status:503,contentType:'application/json',body:'{"status":"unavailable","database":"postgresql"}'}));
    await page.getByRole('button',{name:'Refresh status'}).click();
    await page.getByText('PostgreSQL: Unavailable',{exact:true}).waitFor();
    await page.getByText('API: Online',{exact:true}).waitFor();
    await page.unroute('**/api/health/db');
    await page.route('**/api/**', route => route.abort());
    await page.getByRole('button',{name:'Refresh status'}).click();
    await page.getByRole('alert').waitFor();
    await page.getByText('API: Unavailable',{exact:true}).waitFor();
    assert.equal(await page.getByText('—',{exact:true}).count(),4);
    await page.unroute('**/api/**');
    await page.getByRole('button',{name:'Refresh status'}).click();
    await page.getByText('PostgreSQL: Connected',{exact:true}).waitFor();
    assert.equal(await page.getByRole('alert').count(),0);
    assert.deepEqual(pageErrors,[]);
    console.log('PASS: live proxy/API/PostgreSQL, four null counts, unavailable future controls, desktop/mobile fit, simulated DB/API failure and refresh recovery; no page errors.');
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
