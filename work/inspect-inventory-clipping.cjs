const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();
  fs.mkdirSync('output/rollcall-visual',{recursive:true});
  for(const [name,panel] of [['Vehicles (2)','#vehicles-panel'],['All Stored Sets (4)','#stored-panel'],['Unassigned (1)','#unassigned-panel']]){
   await page.getByRole('tab',{name,exact:true}).click();
   if(panel==='#vehicles-panel'){
    await page.locator('#vehicles-panel [data-slot="accordion-trigger"]').first().click();await page.waitForTimeout(400);
   }
   const rows=page.locator(panel+' .row:visible');
   for(const width of [1584,1280,1100,980,850,761,760,640,480,390,320]){
    await page.setViewportSize({width,height:900});await page.waitForTimeout(80);
    const checks=await rows.evaluateAll(items=>items.map(row=>{
     const line=row.querySelector('.set-description-line'),link=line.querySelector('.set-description'),due=line.querySelector('.row-due');
     const a=link.getBoundingClientRect(),b=due.getBoundingClientRect(),c=line.getBoundingClientRect(),style=getComputedStyle(link);
     return{right:c.right,textRight:a.right,dateLeft:b.left,dateRight:b.right,deltaY:Math.abs((a.top+a.height/2)-(b.top+b.height/2)),height:a.height,font:parseFloat(style.fontSize),lineHeight:parseFloat(style.lineHeight),overflow:style.overflowX,mask:style.maskImage};
    }));
    assert(checks.length>0,'Rows must be visible');
    for(const item of checks){
     assert(item.textRight<=item.dateLeft-6,`${name} at ${width}: description must end before date`);
     assert(item.dateRight<=item.right+1,`${name} at ${width}: due date must fit row`);
     if(item.dateRight>width){console.log({width,item});console.log(await page.locator(panel+' .row').first().evaluate(e=>{const result=[];for(let n=e;n;n=n.parentElement)result.push({tag:n.tagName,cls:String(n.className),width:n.getBoundingClientRect().width,left:n.getBoundingClientRect().left,min:getComputedStyle(n).minWidth,display:getComputedStyle(n).display});return result}));}assert(item.dateRight<=width,`${name} at ${width}: due date must fit window`);
     assert(item.deltaY<3,`${name} at ${width}: description and date stay on one row`);
     assert(item.height<=item.lineHeight+7,'Description stays a single line');
     assert.equal(item.overflow,'hidden');assert(item.mask.includes('gradient'),'Description fades at fluid edge');
    }
    if([980,480,320].includes(width))await page.screenshot({path:`output/rollcall-visual/inventory-clipping-${panel.slice(1)}-${width}.png`,fullPage:true});
   }
  }
  await page.getByRole('tab',{name:'All Stored Sets (4)',exact:true}).click();
  const link=page.locator('#stored-panel .set-description').first(),fullText='Pirelli P Zero with a deliberately long unbroken-description-for-resize-testing · 235/60R18';
  await link.evaluate((e,text)=>e.textContent=text,fullText);
  let previousWidth;
  for(const width of [940,939,938,937]){
   await page.setViewportSize({width,height:900});
   const box=await link.boundingBox();assert.equal(await link.textContent(),fullText,'Resize never removes characters');
   if(previousWidth!==undefined)assert(Math.abs(previousWidth-box.width-1)<.2,'Clipping boundary moves continuously with available width');previousWidth=box.width;
  }
  await link.click();await page.waitForTimeout(450);assert.equal(await page.locator('#detail-heading').textContent(),'Pirelli P Zero');
  assert.deepEqual(errors,[]);console.log('PASS: inventory/vehicle/unassigned fluid description clipping, protected dates, one-line rows at 320–1584px, smooth pixel-width resizing without text mutation, links still open details; no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
