const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:760,height:650}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.getByRole('tab',{name:'Vehicles (2)'}).waitFor();
  const side=page.locator('.shell>aside'),main=page.locator('.shell>main');
  const at760=await side.boundingBox(),content760=await main.boundingBox();
  assert(content760.x>=at760.x+at760.width-1,'Sidebar stays left instead of becoming a top bar');
  fs.mkdirSync('output/rollcall-visual',{recursive:true});
  for(const screen of ['profile','dashboard','corrections','settings']){
   await page.locator('aside [data-screen="'+screen+'"]').click();await page.waitForTimeout(450);
   for(const [width,height] of [[1584,992],[1051,650],[1050,650],[761,500],[760,500],[576,384]]){
    await page.setViewportSize({width,height});await page.waitForTimeout(350);
    const a=await side.boundingBox(),b=await main.boundingBox();
    const compact=['profile','corrections'].includes(screen)&&width<=1000;assert(a.x===0&&Math.abs(a.width-(compact?64:248))<1,'Sidebar remains on the left at the scoped width');
    assert.equal(await page.locator('aside .attention-label').isVisible(),!compact,'Only compact Inventory hides sidebar text');
    assert(b.x>=a.x+a.width-1,'Content sits beside sidebar');
    assert(Math.abs(a.y)<2,'Sidebar stays at viewport top');
    assert(Math.abs(a.height-height)<2,'Sidebar uses viewport height');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`${screen} ${width}: no horizontal page overflow above minimum`);
   }
   await page.screenshot({path:`output/rollcall-visual/sidebar-${screen}-minimum.png`});
  }
  await page.setViewportSize({width:1440,height:384});
  await page.locator('aside [data-screen=profile]').click();await page.waitForTimeout(400);
  const scroll=page.getByRole('region',{name:'Sidebar navigation'});
  const top=await scroll.evaluate(e=>({overflow:e.scrollHeight>e.clientHeight,fade:e.style.getPropertyValue('--sidebar-fade-bottom'),mask:getComputedStyle(e).maskImage}));
  assert(top.overflow,'Short sidebar contents must scroll');assert.equal(top.fade,'18px');assert(top.mask.includes('gradient'));
  const mainTop=(await main.boundingBox()).y;
  await scroll.hover();await page.mouse.wheel(0,600);await page.waitForTimeout(150);
  assert(await scroll.evaluate(e=>e.scrollTop>0),'Sidebar wheel scroll works');
  assert.equal(await scroll.evaluate(e=>e.style.getPropertyValue('--sidebar-fade-top')),'18px');
  assert.equal((await main.boundingBox()).y,mainTop,'Sidebar scroll does not scroll page');
  await page.screenshot({path:'output/rollcall-visual/sidebar-short-scrolled.png'});
  await page.locator('aside [data-screen=settings]').click();await page.waitForTimeout(400);assert.equal(await page.locator('#settings').isVisible(),true);
  await page.setViewportSize({width:480,height:300});
  const minimum=await page.locator('.shell').boundingBox();assert(minimum.width>=576&&minimum.height>=384,'6 by 4 CSS inch minimum layout');
  await page.locator('aside [data-screen=corrections]').click();await page.waitForTimeout(450);
  const correctionMinimum=await page.locator('.shell').boundingBox();assert(Math.abs(correctionMinimum.width-480)<1&&Math.abs(correctionMinimum.height-300)<1,'Approved mobile Corrections fits below the old desktop minimum');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Mobile Corrections does not require a minimum-width canvas');
  assert.deepEqual(errors,[]);console.log('PASS: sidebar remains left across all screens/breakpoints, minimum 576×384 layout, vertical sidebar overflow/fades and independent scrolling, Settings reachable and no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
