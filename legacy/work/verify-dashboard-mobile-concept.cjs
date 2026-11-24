const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const preview=await browser.newPage({viewport:{width:1280,height:900}}),main=await browser.newPage({viewport:{width:1280,height:900}}),errors=[];
  preview.on('pageerror',e=>errors.push(e.message));const url=file=>pathToFileURL(path.resolve('docs/rollcall/'+file)).href;
  await main.goto(url('interaction-preview.html'));assert(await main.locator('#profile').isVisible(),'Main still opens Inventory');await main.locator('aside [data-screen=dashboard]').click();
  await preview.goto(url('dashboard-mobile-concept.html'));await preview.locator('#dashboard').waitFor({state:'visible'});await preview.evaluate(()=>document.fonts.ready);await preview.waitForTimeout(450);
  const boxes=page=>page.locator('#dashboard .metric-card,#dashboard .dashboard-panels>.card').evaluateAll(elements=>elements.map(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height};}));
  assert.deepEqual(await boxes(preview),await boxes(main),'Dashboard desktop arrangement is unchanged');
  fs.mkdirSync('output/rollcall-visual',{recursive:true});await preview.screenshot({path:'output/rollcall-visual/dashboard-concept-desktop.png'});
  const phone=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});phone.on('pageerror',e=>errors.push(e.message));
  await phone.goto(url('interaction-preview.html'));assert(await phone.locator('#profile').isVisible(),'Main still opens Inventory on phones');
  await phone.locator('aside [data-screen=dashboard]').tap();await phone.locator('#dashboard').waitFor({state:'visible'});await phone.evaluate(()=>document.fonts.ready);await phone.waitForFunction(()=>!document.querySelector('.workspace[data-entering],.screen-leaving'));
  for(const width of [320,390,576,800]){
   await phone.setViewportSize({width,height:844});await phone.waitForTimeout(100);
   assert.equal(await phone.evaluate(()=>innerWidth),width,'Mobile CSS width matches viewport');
   assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'No horizontal page overflow');
   assert.equal(Math.round((await phone.locator('.shell>aside').boundingBox()).width),64,'Use approved icon rail');
   assert.deepEqual(await phone.locator('.metric-number').allTextContents(),['128','18','10'],'Sample totals are preserved');
   assert(await phone.getByRole('button',{name:'Choose PDF',exact:true}).isVisible());
   const tiles=await phone.locator('#dashboard .metric-card').evaluateAll(items=>items.map(e=>e.getBoundingClientRect().toJSON()));
   assert(tiles[0].bottom<=tiles[1].top,'Total sits above due status cards');assert(Math.abs(tiles[1].top-tiles[2].top)<1,'Due soon and overdue stay together');
   await phone.screenshot({path:`output/rollcall-visual/dashboard-concept-${width}.png`,fullPage:true});
  }
  await phone.setViewportSize({width:390,height:844});await phone.getByRole('button',{name:'Choose PDF',exact:true}).tap();
  assert((await phone.locator('#upload-feedback').textContent()).includes('not connected'),'Upload remains clearly a demo');
  await phone.getByRole('button',{name:'Open full navigation',exact:true}).tap();const menu=phone.getByRole('dialog',{name:'Full navigation'});
  await menu.getByRole('button',{name:'Corrections',exact:true}).tap();await phone.waitForTimeout(350);assert(await phone.locator('#corrections').isVisible());
  await phone.getByRole('button',{name:'Open full navigation',exact:true}).tap();await menu.getByRole('button',{name:'Dashboard',exact:true}).tap();await phone.waitForTimeout(350);
  assert(await phone.locator('#dashboard').isVisible());await phone.evaluate(()=>scrollTo(0,0));await phone.screenshot({path:'output/rollcall-visual/dashboard-concept-phone.png'});
  assert.deepEqual(errors,[]);console.log('PASS: main Dashboard matches concept desktop geometry and fits 320–800px with prioritized metrics, sample upload feedback and full-menu navigation. Main opens Inventory.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
