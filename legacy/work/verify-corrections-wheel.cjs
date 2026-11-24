const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.locator('.nav [data-screen=corrections]').click();await page.getByRole('button',{name:'Review →',exact:true}).click();await page.waitForTimeout(450);
  const pdf=page.locator('.pdf-page-current'),viewport=page.locator('.pdf-page-viewport'),review=page.locator('.correction-review');
  const fitWidth=(await pdf.boundingBox()).width;
  for(let i=0;i<3;i++)await page.getByRole('button',{name:'Zoom in PDF',exact:true}).click();
  const bounds=await viewport.boundingBox(),x=bounds.x+bounds.width*.55,y=bounds.y+bounds.height*.55;
  const point=()=>pdf.evaluate((e,{x,y})=>{const r=e.getBoundingClientRect();return{u:(x-r.left)/r.width,v:(y-r.top)/r.height,width:r.width};},{x,y});
  const before=await point();await page.mouse.move(x,y);await page.mouse.wheel(0,-120);await page.waitForTimeout(100);
  const after=await point();assert(after.width>before.width,'Wheel up must zoom in');
  assert(Math.abs(before.u-after.u)<.01&&Math.abs(before.v-after.v)<.01,'Keep the PDF point under the cursor anchored');
  await page.mouse.wheel(0,120);await page.waitForTimeout(100);assert((await pdf.boundingBox()).width<after.width,'Wheel down zooms out');
  await page.mouse.wheel(0,10000);await page.waitForTimeout(100);assert(Math.abs((await pdf.boundingBox()).width-fitWidth)<2,'Minimum is fit size');
  await page.mouse.wheel(0,-10000);await page.waitForTimeout(100);assert((await pdf.boundingBox()).width<=fitWidth*5+2,'Maximum is five times fit');
  const zoomedWidth=(await pdf.boundingBox()).width;await review.hover();await page.mouse.wheel(0,300);await page.waitForTimeout(100);
  assert(await review.evaluate(e=>e.scrollTop>0),'Review pane still scrolls');assert(Math.abs((await pdf.boundingBox()).width-zoomedWidth)<2,'Review wheel cannot zoom PDF');
  await page.getByRole('button',{name:'Fit PDF page',exact:true}).click();assert(Math.abs((await pdf.boundingBox()).width-fitWidth)<2,'Fit still resets zoom');
  const unhandled=await viewport.evaluate(e=>e.dispatchEvent(new WheelEvent('wheel',{deltaX:50,deltaY:0,bubbles:true,cancelable:true})));
  assert.equal(unhandled,true,'Horizontal wheel panning remains available');
  await page.setViewportSize({width:480,height:690});await page.waitForTimeout(100);await viewport.hover();
  const compactWidth=(await pdf.boundingBox()).width;await page.mouse.wheel(0,-160);await page.waitForTimeout(100);assert((await pdf.boundingBox()).width>compactWidth,'Wheel zoom in compact layout');
  assert.deepEqual(errors,[]);console.log('PASS: wheel zoom in/out, pointer anchoring, fit/maximum bounds, independent review scroll, horizontal pan and compact-wheel zoom; no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
