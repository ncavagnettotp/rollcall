const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1280,height:1000}});
 const errors=[];
 page.on('pageerror',error=>errors.push(error.message));
 try {
  fs.mkdirSync('output/playwright',{recursive:true});fs.mkdirSync('output/stage2-private',{recursive:true});
  await page.goto('http://127.0.0.1:5174');
  await page.getByText('API: Online',{exact:true}).waitFor();
  assert.equal(await page.getByRole('article').count(),4);
  assert.equal(await page.getByText('—',{exact:true}).count(),4);
  assert(await page.getByRole('searchbox',{name:'Search storage records'}).isDisabled());
  const cards=await page.getByRole('article').all();
  const boxes=await Promise.all(cards.map(card=>card.boundingBox()));
  assert.equal(boxes[0].y,boxes[1].y);assert(boxes[2].y>boxes[0].y);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:'output/playwright/heroui-visual-dashboard-desktop.png',fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:'output/playwright/heroui-visual-dashboard-mobile.png',fullPage:true});
  await page.getByRole('button',{name:'Review uploaded documents'}).click();
  await page.getByRole('button',{name:'Open stage2-verification-blank.pdf',exact:true}).click();
  await page.getByLabel('Customer',{exact:true}).waitFor();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:'output/stage2-private/heroui-visual-review-mobile.png',fullPage:true});
  const colors=await page.getByLabel('Customer',{exact:true}).evaluate(input=>({field:getComputedStyle(input).backgroundColor,surface:getComputedStyle(input.closest('[data-slot="card"]')||input.closest('.card')).backgroundColor}));
  assert.notEqual(colors.field,colors.surface,'Input needs a visible surface contrast against its card');
  await page.setViewportSize({width:1280,height:1000});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:'output/stage2-private/heroui-visual-review-desktop.png',fullPage:true});
  assert.deepEqual(errors,[]);
  console.log('PASS: HeroUI visuals, desktop 2x2 cards, honest counts, disabled search, mobile fit, contrasting editable fields, review opening, no page errors.');
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
