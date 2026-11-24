const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');const path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:960,height:720}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve('docs/rollcall/interaction-preview.html')).href);
  await page.locator('aside [data-screen=corrections]').click();await page.getByRole('button',{name:'Review →',exact:true}).click();await page.waitForTimeout(450);
  const viewport=page.locator('.pdf-page-viewport'),review=page.locator('.correction-review');
  for(let i=0;i<8;i++)await page.getByRole('button',{name:'Zoom in PDF',exact:true}).click();
  const box=await viewport.boundingBox(),x=box.x+box.width*.7,y=box.y+box.height*.7;
  const reviewBefore=await review.evaluate(e=>e.scrollTop);
  await page.mouse.move(x,y);await page.mouse.down();
  assert.equal(await viewport.getAttribute('data-dragging'),'true','Pointer down starts panning');
  await page.mouse.move(x-65,y-70,{steps:8});await page.mouse.up();
  const offset=await viewport.evaluate(e=>({x:e.scrollLeft,y:e.scrollTop}));
  assert(offset.x>=60&&offset.y>=65,'Dragging left/up pans horizontally and vertically');
  assert.equal(await viewport.getAttribute('data-dragging'),'false');
  assert.equal(await review.evaluate(e=>e.scrollTop),reviewBefore,'PDF pan never moves review');
  await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(box.x+box.width+30,y-30,{steps:5});await page.mouse.up();
  assert.equal(await viewport.getAttribute('data-dragging'),'false','Pointer capture releases even outside PDF');
  const beforeWheel=(await page.locator('.pdf-page-current').boundingBox()).width;
  await viewport.hover();await page.mouse.wheel(0,120);await page.waitForTimeout(100);
  assert((await page.locator('.pdf-page-current').boundingBox()).width<beforeWheel,'Wheel still zooms after dragging');
  await page.getByRole('button',{name:'Fit PDF page',exact:true}).click();
  assert.equal(await viewport.evaluate(e=>e.scrollLeft),0);assert.equal(await viewport.evaluate(e=>e.scrollTop),0);
  assert.deepEqual(errors,[]);console.log('PASS: click-drag pans both axes, pointer capture/release outside PDF, review isolation, wheel zoom retained and Fit resets pan; no page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
