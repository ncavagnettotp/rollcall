const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:900}});
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.getByRole('tab',{name:'All Stored Sets (4)'}).click();await page.waitForTimeout(400);
  await page.locator('#stored-panel .set-type-box').nth(2).evaluate(e=>e.innerHTML=setTypeIcons('wheels'));
  for(const width of [1584,980,640,576]){
   await page.setViewportSize({width,height:900});
   const positions=await page.locator('#stored-panel .row').evaluateAll(rows=>rows.map(row=>{
    const box=row.querySelector('.set-type-box'),tire=box.querySelector('img[src$="tire-user.png"]'),wheel=box.querySelector('img[src$="wheel-replacement.png"]');
    const center=e=>e?(e.getBoundingClientRect().left+e.getBoundingClientRect().right)/2:null;
    return{box:box.getBoundingClientRect().toJSON(),tire:center(tire),wheel:center(wheel)};
   }));
   assert(Math.abs(positions[0].tire-positions[1].tire)<1,'Tire-only icon lines up with tire above');
   assert(Math.abs(positions[0].wheel-positions[2].wheel)<1,'Wheel-only icon lines up with wheel above');
   assert(Math.abs(positions[0].box.width-positions[1].box.width)<1,'Single icons preserve both slots');
   assert.equal(positions[2].tire,null,'Wheel-only set has no tire icon');
   fs.mkdirSync('output/rollcall-visual',{recursive:true});await page.screenshot({path:`output/rollcall-visual/inventory-icon-columns-${width}.png`,fullPage:true});
  }
  console.log('PASS: tire-only and wheel-only icons align with combined-set columns at 576–1584px; absent icons remain empty.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
