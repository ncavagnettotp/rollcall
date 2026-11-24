const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:390,height:650}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(350);
  const strip=page.locator('#customer-tabs .tabs__list-container__scroller');
  const frames=await strip.evaluate(e=>new Promise(resolve=>{
   e.scrollLeft=0;e.dispatchEvent(new WheelEvent('wheel',{deltaY:60,bubbles:true,cancelable:true}));
   const result=[];const sample=()=>{result.push(e.scrollLeft);if(result.length===30)resolve(result);else requestAnimationFrame(sample);};requestAnimationFrame(sample);
  }));
  assert(frames[0]>0&&frames[0]<55,'First frame should move partway instead of jumping a full wheel notch');
  assert(frames.filter(value=>value>0&&value<59).length>=4,'Wheel motion should interpolate through multiple frames');
  await page.waitForFunction(()=>Math.abs(document.querySelector('#customer-tabs .tabs__list-container__scroller').scrollLeft-60)<1); 
  for(let i=1;i<frames.length;i++)assert(frames[i]>=frames[i-1]-.01,'No backward jitter while moving forward');
  for(const width of [1280,640,576]){
   await page.setViewportSize({width,height:650});
   await page.getByRole('tab',{name:'All Stored Sets (4)'}).click();await page.waitForTimeout(450);
   const join=await page.evaluate(()=>{
    const indicator=document.querySelector('#customer-tabs .tabs__indicator').getBoundingClientRect(),host=document.querySelector('#customer-tabs'),guide=getComputedStyle(host,'::after'),panel=document.querySelector('#profile>.card:first-child').getBoundingClientRect();
    return{barBottom:indicator.bottom,panelTop:panel.top,barHeight:indicator.height,guideHeight:parseFloat(guide.height),guideCenter:host.getBoundingClientRect().bottom-parseFloat(guide.bottom)-parseFloat(guide.height)/2,barCenter:(indicator.top+indicator.bottom)/2};
   });
   assert(Math.abs(join.barBottom-join.panelTop)<1,'Underline stays on the panel boundary');
   assert.equal(join.guideHeight*2,join.barHeight,'Grey guide stays half thickness');
   assert(Math.abs(join.guideCenter-join.barCenter)<1,'Orange selector follows grey guide');
  }
  await page.setViewportSize({width:390,height:650});await page.emulateMedia({reducedMotion:'reduce'});
  const reduced=await strip.evaluate(e=>{e.scrollLeft=0;e.dispatchEvent(new WheelEvent('wheel',{deltaY:60,bubbles:true,cancelable:true}));return e.scrollLeft;});
  assert(Math.abs(reduced-60)<1,'Reduced motion scrolls immediately');
  assert.deepEqual(errors,[]);console.log('PASS: interpolated monotonic wheel motion and exact settling, underline/grey guide aligned at 576/640/1280px, reduced motion; no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
