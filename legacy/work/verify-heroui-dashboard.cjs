const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:1000}});
 try {
  await page.goto('http://127.0.0.1:5174');
  await page.getByText('API: Online',{exact:true}).waitFor();
  assert.equal(await page.getByRole('article').count(),4);
  assert.equal(await page.getByText('—',{exact:true}).count(),4);
  assert(await page.getByRole('searchbox',{name:'Search storage records'}).isDisabled());
  assert.equal(await page.getByRole('button',{name:'Upload Invoice'}).getAttribute('data-slot'),'button');
  assert.equal(await page.locator('.category-card.card').count(),4);
  fs.mkdirSync('output/playwright',{recursive:true});
  await page.screenshot({path:'output/playwright/heroui-dashboard-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:'output/playwright/heroui-dashboard-mobile.png',fullPage:true});
  await page.route('**/api/**',route=>route.abort());
  await page.getByRole('button',{name:'Refresh status'}).click();
  await page.getByRole('alert').waitFor();
  assert.equal(await page.getByRole('article').count(),4);
  await page.unroute('**/api/**');
  await page.getByRole('button',{name:'Refresh status'}).click();
  await page.getByText('PostgreSQL: Connected',{exact:true}).waitFor();
  assert.equal(await page.getByRole('alert').count(),0);
  console.log('PASS: runtime HeroUI Button/Card, real API/DB, placeholder counts, disabled search, mobile fit and dashboard failure/recovery.');
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
