const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1584,height:1100}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.locator('.nav [data-screen="corrections"]').click();
  await page.getByRole('button',{name:'Review →',exact:true}).click();
  await page.waitForTimeout(450);
  const resolve=page.getByRole('button',{name:'Resolve correction',exact:true});
  assert(await resolve.isDisabled());
  await page.getByRole('button',{name:'Edit details →'}).click();
  const editor=page.getByRole('region',{name:'Edit all details'});
  console.log(await editor.locator('[data-slot=select]').first().evaluate(e=>({html:e.outerHTML,children:[...e.querySelectorAll('*')].slice(0,12).map(n=>({tag:n.tagName,slot:n.dataset.slot,css:getComputedStyle(n).position,box:n.getBoundingClientRect().toJSON()}))}))); await editor.getByRole('textbox',{name:'Customer',exact:true}).fill('Cancelled edit');
  await editor.getByRole('button',{name:'Cancel',exact:true}).first().click();
  assert.equal(await page.locator('.correction-heading strong').textContent(),'Riley Bennett');
  await page.getByRole('button',{name:'Edit details →'}).click();
  await editor.getByRole('textbox',{name:'Customer',exact:true}).fill('Riley Bennett updated');
  await editor.getByRole('button',{name:'Apply corrections'}).click();
  assert.equal(await page.locator('.correction-heading strong').textContent(),'Riley Bennett updated');
  assert((await page.locator('.correction-paper').textContent()).includes('Riley Bennett'));
  assert(!(await page.locator('.correction-paper').textContent()).includes('updated'));
  await page.getByRole('button',{name:'Coming out of storage'}).click();
  await page.getByRole('option',{name:'Pirelli P Zero · 235/60R18 · Audi Q5'}).click();
  assert(await resolve.isEnabled());
  assert((await page.getByRole('button',{name:'Coming out of storage'}).boundingBox()).height<60,'Select must remain compact');
  fs.mkdirSync('output/rollcall-visual',{recursive:true});
  await page.waitForTimeout(450); await page.screenshot({path:'output/rollcall-visual/correction-desktop.png',fullPage:true});
  await page.getByRole('button',{name:'Edit details →'}).click();
  await page.waitForTimeout(450); await page.screenshot({path:'output/rollcall-visual/correction-editor-desktop.png',fullPage:true});
  await editor.getByRole('button',{name:'Cancel',exact:true}).first().click();
  for(const width of [390,320]){
   await page.setViewportSize({width,height:900});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Review overflow '+width);
   await page.getByRole('button',{name:'Edit details →'}).click();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Editor overflow '+width);
   await page.waitForTimeout(450); await page.screenshot({path:`output/rollcall-visual/correction-editor-${width}.png`,fullPage:true});
   await editor.getByRole('button',{name:'Cancel',exact:true}).first().click();
  }
  await resolve.click();assert(await resolve.isDisabled());
  assert((await page.getByRole('status').last().textContent()).includes('No live inventory'));
  await page.getByRole('button',{name:'← Back to corrections'}).click();
  assert(await page.getByRole('button',{name:'Reset sample issue'}).isVisible());
  assert.deepEqual(errors,[]);
  console.log('PASS: correction navigation, cancel/apply isolation, immutable source, required selection, resolution, desktop/mobile overflow and screenshots; no page errors.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
