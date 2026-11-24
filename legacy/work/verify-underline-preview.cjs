const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const baseline=await browser.newPage({viewport:{width:1280,height:900}}),preview=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
  preview.on('pageerror',e=>errors.push(e.message));
  const open=async(page,file)=>{await page.goto(pathToFileURL(path.resolve('docs/rollcall/'+file)).href);await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(350);};
  await open(baseline,'interaction-preview.html');await open(preview,'underline-tabs-preview.html');
  const dimensions=page=>page.locator('#customer-tabs [role=tab]').evaluateAll(tabs=>tabs.map(tab=>{const icon=tab.querySelector('.customer-tab-icon'),a=tab.getBoundingClientRect(),b=icon.getBoundingClientRect();return{label:tab.getAttribute('aria-label'),width:a.width,height:a.height,font:getComputedStyle(tab).fontSize,iconWidth:b.width,iconHeight:b.height,iconViewBox:icon.getAttribute('viewBox')};}));
  assert.deepEqual(await dimensions(preview),await dimensions(baseline),'Main mockup and comparison preview use the same tab/icon geometry');
  const palette=page=>page.evaluate(()=>['body','.shell>aside','.toolbar.page-header','#customer-tabs','#customer-tabs [role=tab][aria-selected=true]','#customer-tabs [role=tab][aria-selected=false]','#customer-tabs .tabs__indicator','#profile>.card:first-child'].map(selector=>{const e=document.querySelector(selector),style=getComputedStyle(e);return{selector,color:style.color,background:style.backgroundColor,image:style.backgroundImage,border:style.borderColor};}).concat([{guide:getComputedStyle(document.querySelector('#customer-tabs'),'::after').backgroundColor}]));
  assert.deepEqual(await palette(baseline),await palette(preview),'Main mockup copies the exact preview palette across sidebar/header/tabs/content');
  assert.equal(await preview.locator('.shell>aside').evaluate(e=>e.getBoundingClientRect().width),248);
  const active=preview.locator('#customer-tabs [role=tab][aria-selected=true]');
  assert.equal(await active.evaluate(e=>getComputedStyle(e).color),'rgb(255, 137, 0)');
  assert.equal(await preview.locator('#customer-tabs .tabs__indicator').evaluate(e=>getComputedStyle(e).height),'4px');
  assert.equal(await preview.locator('#customer-tabs').evaluate(e=>getComputedStyle(e).backgroundColor),await baseline.locator('#customer-tabs').evaluate(e=>getComputedStyle(e).backgroundColor),'Restore the original off-grey shelf');
  const guide=await preview.locator('#customer-tabs').evaluate(e=>{
   const track=getComputedStyle(e,'::after'),bar=e.querySelector('.tabs__indicator').getBoundingClientRect(),host=e.getBoundingClientRect();
   return{height:parseFloat(track.height),barHeight:bar.height,trackCenter:host.bottom-parseFloat(track.bottom)-parseFloat(track.height)/2,barCenter:(bar.top+bar.bottom)/2};
  });
  assert.equal(guide.height*2,guide.barHeight,'Guide is half the orange bar thickness');
  assert(Math.abs(guide.trackCenter-guide.barCenter)<1,'Orange selector follows the center of the grey guide');
  assert.equal(await baseline.locator('#customer-tabs .tabs__indicator').evaluate(e=>getComputedStyle(e,'::before').display==='none'),true,'Main mockup uses approved underline design');
  const mainTabFont=await baseline.locator('#customer-tabs [role=tab]').first().evaluate(e=>parseFloat(getComputedStyle(e).fontSize));
  const rowFont=await baseline.locator('.vehicle-accordion [data-slot=accordion-trigger]').first().evaluate(e=>parseFloat(getComputedStyle(e).fontSize));
  assert(mainTabFont>rowFont,'Tab labels are larger than the information below');
  assert.equal(await baseline.locator('#customer-tabs [role=tab][aria-selected=true]').evaluate(e=>getComputedStyle(e).color),'rgb(255, 137, 0)');
  fs.mkdirSync('output/rollcall-visual',{recursive:true});
  await preview.screenshot({path:'output/rollcall-visual/underline-preview-desktop.png'});
  await preview.locator('#customer-tabs').screenshot({path:'output/rollcall-visual/underline-preview-tabs.png'});
  await preview.getByRole('tab',{name:'All Stored Sets (4)'}).click();assert(await preview.locator('#stored-panel').isVisible());
  await preview.getByRole('tab',{name:'Unassigned (1)'}).focus();await preview.keyboard.press('ArrowLeft');assert.equal(await preview.getByRole('tab',{name:'Vehicles (2)'}).getAttribute('aria-selected'),'true');
  await preview.setViewportSize({width:390,height:650});await preview.waitForTimeout(150);
  const strip=preview.locator('#customer-tabs .tabs__list-container__scroller');
  await strip.evaluate(e=>e.scrollLeft=0);const pageY=await preview.evaluate(()=>scrollY);
  await strip.hover();await preview.mouse.wheel(0,100);await preview.waitForTimeout(350);
  assert(await strip.evaluate(e=>e.scrollLeft>0),'Smooth wheel scroll remains');assert.equal(await preview.evaluate(()=>scrollY),pageY,'Wheel stays in strip');
  assert.equal(await strip.evaluate(e=>e.style.getPropertyValue('--tab-fade-left')),'22px');
  await preview.evaluate(()=>document.activeElement?.blur());
  await preview.screenshot({path:'output/rollcall-visual/underline-preview-compact.png'});
  assert.deepEqual(errors,[]);console.log('PASS: approved underline style in main and comparison preview; larger labels, shared geometry/orange, grey guide ratio/alignment, selection/keyboard/wheel/fades/sidebar retained.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
