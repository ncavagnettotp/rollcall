const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const errors=[],desktop=await browser.newPage({viewport:{width:1280,height:900}}),main=await browser.newPage({viewport:{width:1280,height:900}});
  desktop.on('pageerror',e=>errors.push(e.message));
  const url=file=>pathToFileURL(path.resolve('docs/rollcall/'+file)).href;
  await main.goto(url('interaction-preview.html'));await main.locator('aside [data-screen=corrections]').click();await main.getByRole('button',{name:'Review →',exact:true}).click();
  await desktop.goto(url('corrections-mobile-concept.html'));await desktop.locator('.correction-review').waitFor({state:'visible'});await desktop.waitForTimeout(450);
  const boxes=page=>page.locator('.correction-source,.correction-review').evaluateAll(elements=>elements.map(e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height};}));
  assert.deepEqual(await boxes(desktop),await boxes(main),'Desktop preview keeps current two-pane geometry');
  assert.equal(await main.locator('.correction-mobile-view-tabs').isVisible(),false,'Desktop keeps mobile switch hidden');
  fs.mkdirSync('output/rollcall-visual',{recursive:true});await desktop.screenshot({path:'output/rollcall-visual/corrections-concept-desktop.png'});
  const phone=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});phone.on('pageerror',e=>errors.push(e.message));
  await phone.goto(url('interaction-preview.html'));assert(await phone.locator('#profile').isVisible(),'Inventory remains the default screen');await phone.locator('aside [data-screen=corrections]').tap();await phone.getByRole('button',{name:'Review →',exact:true}).tap();await phone.getByRole('tab',{name:'Review details',exact:true}).waitFor();
  const fits=async()=>{assert.equal(await phone.evaluate(()=>innerWidth),phone.viewportSize().width);assert.equal(await phone.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);};
  for(const width of [320,390,640]){
   await phone.setViewportSize({width,height:844});await fits();await phone.waitForTimeout(150);
   assert(await phone.locator('.correction-review').isVisible());assert.equal(await phone.locator('.correction-source').isVisible(),false);
   await phone.screenshot({path:`output/rollcall-visual/corrections-concept-review-${width}.png`});
  }
  await phone.setViewportSize({width:390,height:844});
  const reviewTab=phone.getByRole('tab',{name:'Review details',exact:true}),pdfTab=phone.getByRole('tab',{name:'Original PDF',exact:true});
  await pdfTab.tap();await phone.waitForTimeout(200);await fits();
  await phone.getByRole('button',{name:'Next PDF page',exact:true}).tap();await phone.waitForTimeout(420);
  assert.equal(await phone.locator('.pdf-page-current').getAttribute('alt'),'Supplied invoice 215798, page 2 of 2');
  await phone.getByRole('button',{name:'Zoom in PDF',exact:true}).tap();
  const viewport=phone.locator('.pdf-page-viewport'),rect=await viewport.boundingBox(),touch=await phone.context().newCDPSession(phone);
  await touch.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:rect.x+rect.width*.7,y:rect.y+rect.height*.7}]});
  for(let i=1;i<=4;i++)await touch.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:rect.x+rect.width*.7-30*i/4,y:rect.y+rect.height*.7-35*i/4}]});
  await touch.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await touch.detach();
  assert(await viewport.evaluate(e=>e.scrollLeft>0&&e.scrollTop>0),'Native touch drag pans the magnified PDF');
  await phone.screenshot({path:'output/rollcall-visual/corrections-concept-pdf-390.png'});
  await reviewTab.tap();await phone.getByRole('button',{name:'Edit details →'}).tap();
  const editor=phone.getByRole('region',{name:'Edit all details'});
  await editor.getByRole('textbox',{name:'Notes',exact:true}).fill('Unsubmitted phone draft');
  await pdfTab.tap();await phone.waitForTimeout(150);
  assert.equal(await phone.locator('.pdf-page-current').getAttribute('alt'),'Supplied invoice 215798, page 2 of 2','PDF page survives switching');
  assert.equal(await phone.getByRole('button',{name:'Zoom out PDF',exact:true}).isDisabled(),false,'PDF zoom survives switching');
  await reviewTab.tap();assert.equal(await editor.getByRole('textbox',{name:'Notes',exact:true}).inputValue(),'Unsubmitted phone draft','Draft survives source comparison');
  await editor.getByRole('button',{name:'Cancel',exact:true}).first().tap();
  await phone.getByRole('button',{name:'Coming out of storage'}).tap();await phone.getByRole('option',{name:'Example stored set A · Tahoe'}).tap();
  const resolve=phone.getByRole('button',{name:'Resolve correction',exact:true});assert(await resolve.isEnabled());await resolve.tap();assert(await resolve.isDisabled(),'Resolution remains single-use in the sample');
  await phone.getByRole('button',{name:'Open full navigation',exact:true}).tap();
  const menu=phone.getByRole('dialog',{name:'Full navigation'});assert(await menu.getByRole('button',{name:'Corrections',exact:true}).isVisible());
  await menu.getByRole('button',{name:'Close navigation',exact:true}).tap();await menu.waitFor({state:'hidden'});
  await phone.setViewportSize({width:800,height:700});await phone.waitForTimeout(150);await fits();
  assert(await phone.locator('.correction-source').isVisible());assert(await phone.locator('.correction-review').isVisible());
  await phone.screenshot({path:'output/rollcall-visual/corrections-concept-small-desktop.png'});
  await phone.setViewportSize({width:390,height:844});await pdfTab.tap();
  await phone.getByRole('button',{name:'Fit PDF page',exact:true}).tap();
  await phone.getByRole('button',{name:'Previous PDF page',exact:true}).tap();await phone.waitForTimeout(420);
  await phone.screenshot({path:'output/rollcall-visual/corrections-concept-pdf-390.png'});
  assert.deepEqual(errors,[]);console.log('PASS: approved mobile Corrections in main mockup; desktop geometry unchanged, 320–640 phone fit, mobile PDF/review switching, draft/page/zoom preservation, menu and wider two-pane layout. Inventory stays the default screen.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
