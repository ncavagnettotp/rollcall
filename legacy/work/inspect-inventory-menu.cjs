const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();await page.evaluate(()=>document.fonts.ready);
  const fits=async()=>{assert.equal(await page.evaluate(()=>innerWidth),page.viewportSize().width,'Mobile layout viewport matches physical CSS width');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Inventory fits actual viewport width');};
  await fits();
  for(const width of [320,390,576,800,1000,1280]){
   await page.setViewportSize({width,height:844});await page.waitForTimeout(150);await fits();
   const side=await page.locator('.shell>aside').boundingBox();
   assert.equal(Math.round(side.width),width<=1000?64:248,'Sidebar compacts at the Inventory breakpoint');
   assert.equal(await page.getByRole('button',{name:'Open full navigation',exact:true}).isVisible(),width<=1000);
   await page.getByRole('tab',{name:'All Stored Sets (4)'}).click();
   const checks=await page.locator('#stored-panel .row').evaluateAll(rows=>rows.map(row=>({
    vehicle:row.querySelector('.set-secondary-line p').textContent.trim(),vehicleVisible:getComputedStyle(row.querySelector('.set-secondary-line')).display!=='none',
    dueVisible:getComputedStyle(row.querySelector('.row-due')).display!=='none',icons:row.querySelector('.set-type-box').getBoundingClientRect().width,
    fade:getComputedStyle(row.querySelector('.set-description')).maskImage,
   })));
   assert(checks.every(c=>c.vehicle&&c.vehicleVisible&&c.icons>40&&c.fade.includes('gradient')),'Vehicle info, type slots and fading descriptions remain');
   assert(checks.every(c=>c.dueVisible===(width>1000)),'Dates hide only in compact Inventory');
   fs.mkdirSync('output/rollcall-visual',{recursive:true});await page.evaluate(()=>document.activeElement?.blur());await page.screenshot({path:`output/rollcall-visual/inventory-mobile-${width}.png`,fullPage:true});
  }
  await page.setViewportSize({width:390,height:844});
  await page.getByRole('tab',{name:'Unassigned (1)'}).click();
  assert(await page.locator('#unassigned-panel .set-secondary-line').isVisible(),'Customer-only vehicle status remains visible');
  const strip=page.locator('#customer-tabs .tabs__list-container__scroller');await strip.evaluate(e=>e.scrollLeft=0);
  const stripBox=await strip.boundingBox(),session=await page.context().newCDPSession(page),touchY=stripBox.y+stripBox.height/2;
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stripBox.x+stripBox.width-20,y:touchY}]});
  for(let i=1;i<=5;i++)await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:stripBox.x+stripBox.width-20-(stripBox.width-40)*i/5,y:touchY}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await page.waitForTimeout(200);
  assert(await strip.evaluate(e=>e.scrollLeft>0),'Phone swipe reveals overflow tabs');await session.detach();
  await page.getByRole('tab',{name:'All Stored Sets (4)'}).click();
  await page.getByRole('button',{name:'Open full navigation',exact:true}).tap();
  const menu=page.getByRole('dialog',{name:'Full navigation'});assert(await menu.isVisible());await page.waitForTimeout(250);
  const menuBounds=await menu.boundingBox();assert(menuBounds.x>=0&&menuBounds.x+menuBounds.width<=390,'Full menu is inside phone viewport');
  assert(await menu.getByRole('button',{name:'Inventory',exact:true}).isVisible());
  console.log(JSON.stringify(await menu.getByRole('button',{name:'Inventory',exact:true}).evaluate(e=>({html:e.outerHTML,styles:[e,...e.children].map(n=>({tag:n.tagName,color:getComputedStyle(n).color,opacity:getComputedStyle(n).opacity,visibility:getComputedStyle(n).visibility,display:getComputedStyle(n).display,rect:n.getBoundingClientRect().toJSON()}))}))));await page.screenshot({path:'output/rollcall-visual/inventory-mobile-menu.png'});
  await page.keyboard.press('Escape');await menu.waitFor({state:'hidden'});
  assert(await page.getByRole('button',{name:'Open full navigation',exact:true}).evaluate(e=>e===document.activeElement),'Menu restores focus');
  await page.locator('#stored-panel [data-set=RC-104]').tap();await page.waitForTimeout(420);await fits();
  assert.equal(await page.locator('#assigned-vehicle-name').textContent(),'2021 Audi Q5');
  await page.getByRole('button',{name:'Reassign vehicle',exact:true}).tap();
  const pickerBounds=await page.locator('#vehicle-picker').boundingBox();assert(pickerBounds.x+pickerBounds.width<=390);
  await page.locator('#vehicle-picker').getByRole('button',{name:'Cancel',exact:true}).tap();
  await page.locator('#detail [data-screen=profile]').tap();await page.waitForTimeout(420);
  await page.getByRole('button',{name:'Open full navigation',exact:true}).tap();await menu.getByRole('button',{name:'Dashboard',exact:true}).tap();await page.waitForTimeout(420);
  assert.equal(await page.evaluate(()=>document.body.classList.contains('inventory-responsive-layout')),false,'Other screens retain prior behavior');
  assert.deepEqual(errors,[]);console.log('PASS: Inventory responsive 320–1280px, compact sidebar/full-menu focus and navigation, vehicle/type/description priority, compact date hiding, touch details/reassign and no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
