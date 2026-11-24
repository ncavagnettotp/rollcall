const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:640,height:650}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();
  await page.evaluate(()=>{window.wheelTrace=[];document.addEventListener('wheel',e=>window.wheelTrace.push({y:scrollY,target:e.target.className,inStrip:!!e.target.closest('.tabs__list-container__scroller'),prevented:e.defaultPrevented}),false)});const strip=page.locator('#customer-tabs .tabs__list-container__scroller');
  assert.equal(await strip.evaluate(e=>getComputedStyle(e).overflowX),'auto','Tab strip must scroll horizontally');
  for(const width of [640,576]){
   await page.setViewportSize({width,height:650});await strip.evaluate(e=>e.scrollLeft=0);await page.waitForTimeout(150);
   const initial=await strip.evaluate(e=>({overflow:e.scrollWidth>e.clientWidth,right:e.style.getPropertyValue('--tab-fade-right'),left:e.scrollLeft}));
   assert(initial.overflow,'Tab labels remain readable rather than shrinking to fit');assert.equal(initial.right,'22px');
   const pageY=await page.evaluate(()=>scrollY);
   await strip.hover();await page.mouse.wheel(0,180);await page.waitForTimeout(120);
   assert(await strip.evaluate(e=>e.scrollLeft>0),'Wheel moves tabs horizontally');
   assert.equal(await page.evaluate(()=>scrollY),pageY,'Wheel over tab strip does not move document');
   assert.equal(await strip.evaluate(e=>e.style.getPropertyValue('--tab-fade-left')),'22px');
   await page.getByRole('tab',{name:'All Stored Sets (4)'}).click();
   assert.equal(await page.locator('#stored-panel').isVisible(),true);
   await strip.hover();await page.mouse.wheel(0,-10000);await page.waitForFunction(()=>document.querySelector('#customer-tabs .tabs__list-container__scroller').scrollLeft<1);assert.equal(await strip.evaluate(e=>e.scrollLeft),0);
   const max=await strip.evaluate(e=>e.scrollWidth-e.clientWidth);await page.mouse.wheel(0,10000);await page.waitForTimeout(120);
   await page.waitForFunction(()=>{const e=document.querySelector('#customer-tabs .tabs__list-container__scroller');return Math.abs(e.scrollLeft-(e.scrollWidth-e.clientWidth))<1;});assert(Math.abs((await strip.evaluate(e=>e.scrollLeft))-max)<1);
   await page.mouse.wheel(0,300);await page.waitForTimeout(80);console.log({width,expected:pageY,current:await page.evaluate(()=>scrollY),trace:await page.evaluate(()=>window.wheelTrace),box:await strip.boundingBox()});assert.equal(await page.evaluate(()=>scrollY),pageY,'Tab edge must not leak wheel to page');
   fs.mkdirSync('output/rollcall-visual',{recursive:true});await page.screenshot({path:`output/rollcall-visual/tabs-scroll-${width}.png`});
   await page.getByRole('tab',{name:'All Stored Sets (4)'}).focus();await page.keyboard.press('ArrowLeft');
   assert.equal(await page.getByRole('tab',{name:'Unassigned (1)'}).getAttribute('aria-selected'),'true','Keyboard navigation remains functional');
  }
  await page.setViewportSize({width:1584,height:992});await strip.evaluate(e=>e.scrollLeft=0);await page.waitForTimeout(150);
  assert.equal(await strip.evaluate(e=>e.style.getPropertyValue('--tab-fade-right')),'0px','No fade when all tabs fit');
  const accepted=await strip.evaluate(e=>e.dispatchEvent(new WheelEvent('wheel',{deltaY:100,bubbles:true,cancelable:true})));
  assert.equal(accepted,true,'Do not capture wheel when tabs fit');
  await page.setViewportSize({width:640,height:650});await page.locator('#profile .card').last().hover();
  const tabScroll=await strip.evaluate(e=>e.scrollLeft);await page.mouse.wheel(0,200);await page.waitForTimeout(100);
  assert.equal(await strip.evaluate(e=>e.scrollLeft),tabScroll,'Outside wheel cannot move tab strip');
  assert.deepEqual(errors,[]);console.log('PASS: horizontal tab fade and local wheel scroll, edge containment, normal page scroll outside, no wheel capture when tabs fit, tab selection and keyboard navigation.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
