const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  for(const scale of [1,1.25,1.5,2]){
   const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:scale});
   await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview-connected-tabs.html')).href);
   await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(350);
   const geometry=await page.locator('#customer-tabs .tab-panel-join').evaluate(e=>{
    const left=getComputedStyle(e,'::before'),right=getComputedStyle(e,'::after'),base=getComputedStyle(e);
    return{leftImage:left.backgroundImage,rightImage:right.backgroundImage,transform:right.transform,width:left.width,rightWidth:right.width,base:base.backgroundImage};
   });
   assert(geometry.leftImage.includes('svg'),'Left curve must use the shared exact curve shape');
   assert.equal(geometry.leftImage,geometry.rightImage,'Both sides use one identical curve asset');
   assert.equal(geometry.transform,'matrix(-1, 0, 0, 1, 0, 0)','Right side is a literal mirror');
   assert.equal(geometry.width,geometry.rightWidth,'Mirrored curves have matching dimensions');
   assert(geometry.base.includes('linear-gradient'),'White base seals the tips');
   fs.mkdirSync('output/rollcall-visual',{recursive:true});
   const box=await page.locator('#customer-tabs [role=tab][aria-selected=true]').boundingBox();
   await page.screenshot({path:`output/rollcall-visual/tab-mirror-${scale}.png`,clip:{x:Math.floor(box.x-43),y:Math.floor(box.y-12),width:Math.ceil(box.width+86),height:Math.ceil(box.height+40)}});
   await page.close();
  }
  console.log('PASS: one shared curve shape, exact horizontal mirroring, equal dimensions and white tip seal at 100/125/150/200% display scales.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
