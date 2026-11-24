const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:900}});
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview-connected-tabs.html')).href);
  await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();await page.evaluate(()=>document.fonts.ready);
  for(const width of [1584,1280,760,640,576]){
   await page.setViewportSize({width,height:900});
   for(const name of ['Vehicles (2)','Unassigned (1)','All Stored Sets (4)']){
    await page.getByRole('tab',{name,exact:true}).click();await page.waitForTimeout(420);
    await page.locator('#customer-tabs .tabs__list-container__scroller').evaluate(e=>{const selected=e.querySelector('[aria-selected=true]');selected.scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'});});
    const geometry=await page.evaluate(()=>{
     const strip=document.querySelector('#customer-tabs .tabs__list-container__scroller'),tabs=[...strip.querySelectorAll('[role=tab]')],active=strip.querySelector('[aria-selected=true]'),join=active.querySelector('.tab-panel-join'),s=getComputedStyle(join),r=join.getBoundingClientRect(),a=strip.getBoundingClientRect(),b=document.querySelector('#profile>.card:first-child').getBoundingClientRect();
     return{corner:getComputedStyle(join,"::before").backgroundImage,mirror:getComputedStyle(join,"::after").transform,background:s.backgroundImage,height:r.height,inset:parseFloat(getComputedStyle(active.querySelector(".tabs__indicator"),"::before").left),topRadius:parseFloat(getComputedStyle(active.querySelector(".tabs__indicator"),"::before").borderTopLeftRadius),joinLeft:parseFloat(s.left),left:r.left,right:r.right,stripLeft:a.left,stripRight:a.right,bottom:r.bottom,panelTop:b.top,gaps:tabs.slice(1).map((tab,i)=>tab.getBoundingClientRect().left-tabs[i].getBoundingClientRect().right)};
    });
    assert(geometry.gaps.every(gap=>gap>=7&&gap<=9),'All tabs remain adjacent with a fixed gap');
    assert(geometry.corner.includes('svg'),'Both corners use the explicit shared curve path');
    assert.equal(geometry.mirror,'matrix(-1, 0, 0, 1, 0, 0)','Second corner is an exact mirror');
    assert.equal(geometry.height,geometry.topRadius,'Lower reverse curves match the upper surround radius');
    assert.equal(geometry.joinLeft,geometry.inset-geometry.topRadius,'Reverse curve starts tangent to the white surround side');
    assert(geometry.left>=geometry.stripLeft-1&&geometry.right<=geometry.stripRight+1,`Both corners remain unclipped at ${width} for ${name}`);
    assert(Math.abs(geometry.bottom-geometry.panelTop)<1,'Curves connect to the content panel');
    if(width===1280&&name==='Vehicles (2)'){
     fs.mkdirSync('output/rollcall-visual',{recursive:true});
     const b=await page.locator('#customer-tabs [role=tab][aria-selected=true]').boundingBox();
     await page.screenshot({path:'output/rollcall-visual/tab-reverse-curves-closeup.png',clip:{x:Math.floor(b.x-43),y:Math.floor(b.y-12),width:Math.ceil(b.width+86),height:Math.ceil(b.height+40)},scale:'css'});
    }
   }
   fs.mkdirSync('output/rollcall-visual',{recursive:true});await page.screenshot({path:`output/rollcall-visual/tab-geometry-${width}.png`});
  }
  console.log('PASS: adjacent tabs and both fixed concave bottom corners remain visible and connected to the panel across selections at 576–1584px.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
