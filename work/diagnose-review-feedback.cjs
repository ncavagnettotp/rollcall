const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:Number(process.argv[2]||1280),height:800}});
 try {
  await page.goto('http://127.0.0.1:5174');
  await page.getByRole('button',{name:'Review uploaded documents'}).click();
  const row=page.getByRole('button',{name:'Open stage2-verification-blank.pdf',exact:true});
  await row.click();
  await page.getByLabel('Customer',{exact:true}).waitFor();
  const open=await page.evaluate(()=>({top:document.querySelector('#review-title').getBoundingClientRect().top,viewport:innerHeight,focused:document.activeElement.id}));
  assert(open.top>=0&&open.top<open.viewport&&open.focused==='review-title');
  console.log('PASS: archive click opens and focuses the review in the viewport');
  const response=page.waitForResponse(r=>r.request().method()==='PATCH');
  await page.getByRole('button',{name:'Save review',exact:true}).click();
  assert.equal((await response).status(),200);
  await page.getByText('Review saved. Storage records are unchanged.',{exact:true}).waitFor();
  const saved=await page.evaluate(()=>({top:document.querySelector('.save-row [role="status"]').getBoundingClientRect().top,bottom:document.querySelector('.save-row [role="status"]').getBoundingClientRect().bottom,viewport:innerHeight}));
  assert(saved.top>=0&&saved.bottom<=saved.viewport);
  console.log('PASS: successful save feedback is visibly beside Save review');
  const last=page.locator('.archive-list button').last();
  const opened=page.waitForResponse(r=>r.url().includes('/api/documents/')&&r.request().method()==='GET');
  await last.click(); await opened;
  await page.waitForFunction(()=>document.activeElement?.id==='review-title');
  const bottom=await page.locator('#review-title').boundingBox();
  assert(bottom.y>=0&&bottom.y<800);
  console.log('PASS: bottom archived item brings its loaded review back into view');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
