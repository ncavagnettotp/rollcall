// Local browser acceptance; real customer screenshots stay in ignored private output.
const {chromium} = require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async()=>{
  fs.mkdirSync('output/playwright',{recursive:true});
  fs.mkdirSync('output/stage2-private',{recursive:true});
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  const page=await browser.newPage({viewport:{width:1280,height:1000}});
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  try {
    await page.goto('http://127.0.0.1:5174');
    await page.getByText('API: Online',{exact:true}).waitFor();
    await page.getByRole('button',{name:'Upload Invoice'}).click();
    const picker=page.getByLabel('Choose PDF');
    await picker.waitFor();
    await picker.setInputFiles('C:/Users/ndcav/OneDrive/Desktop/Storage Examples/Tire-and-Wheel-Swap-With-Storage-And-Notes-Invoice-215798-Invoice.pdf');
    await page.getByRole('button',{name:'Upload PDF',exact:true}).click();
    await page.getByLabel('Customer',{exact:true}).waitFor();
    await page.getByRole('button',{name:/Accessories/}).click();
    const lugs=page.getByRole('button',{name:/Lug nuts/});
    assert((await lugs.innerText()).includes('Yes'));
    assert((await page.getByRole('button',{name:/Center caps/}).innerText()).includes('Yes'));
    assert((await page.getByRole('button',{name:/Centering rings/}).innerText()).includes('No'));
    // Exercise the real HeroUI/React Aria popover, not a hidden native select.
    await lugs.click();
    await page.getByRole('option',{name:'No',exact:true}).click();
    assert((await lugs.innerText()).includes('No'));
    await lugs.click();
    await page.getByRole('option',{name:'Yes',exact:true}).click();
    assert((await lugs.innerText()).includes('Yes'));
    assert((await page.locator('body').innerText()).includes('already archived'));
    assert(await page.getByRole('link',{name:/View original PDF/}).getAttribute('href'));
    await page.screenshot({path:'output/stage2-private/review-desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:'output/stage2-private/review-mobile.png',fullPage:true});
    // Save review metadata, never a storage action. Reopen after page reload.
    await page.getByRole('button',{name:'Save review',exact:true}).click();
    await page.getByText('Review saved. Storage records are unchanged.',{exact:true}).waitFor();
    await page.reload();
    await page.getByRole('button',{name:'Upload Invoice'}).click();
    await page.getByRole('button',{name:/Open Tire-and-Wheel-Swap-With-Storage/}).click();
    await page.getByLabel('Customer',{exact:true}).waitFor();
    assert.equal(await page.getByRole('alert').count(),0);
    assert.deepEqual(errors,[]);
    console.log('PASS: real upload/duplicate review, accessories, original link, save/reload/reopen, mobile fit, no page errors');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
