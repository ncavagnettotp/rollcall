const {chromium}=require('C:/Users/ndcav/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
const {resolve}=require('node:path');
const assert=require('node:assert/strict');

(async()=>{
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  try {
    const errors=[];
    const open=async options=>{
      const page=await browser.newPage({...options,reducedMotion:'reduce'});
      page.on('pageerror',error=>errors.push(error.message));
      await page.goto(pathToFileURL(resolve('docs/rollcall/interaction-preview.html')).href);
      assert(await page.locator('#profile').isVisible(),'Main opens on Inventory');
      await page.locator('aside [data-screen=insights]').click();
      await page.getByRole('heading',{name:'Storage activity'}).waitFor();
      return page;
    };
    const desktop=await open({viewport:{width:1440,height:900}});
    const activity=await desktop.locator('.insights-activity').boundingBox();
    const averages=await desktop.locator('.insights-averages').boundingBox();
    assert.equal(activity.y,averages.y,'Activity and averages share a desktop row');
    assert.deepEqual(await desktop.locator('.insights-averages dd').allTextContents(),['124','12']);
    assert.equal(await desktop.locator('.insights-activity .insights-icon-accent').count(),3);
    assert.deepEqual(await desktop.locator('.insights-activity td').allTextContents(),['24','19','16']);
    await desktop.screenshot({path:'output/rollcall-visual/insights-desktop.png',fullPage:true});
    const phone=await open({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
    for(const width of [320,390,576,800,1000]){
      await phone.setViewportSize({width,height:844});
      assert(await phone.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Insights fits at '+width);
      assert.equal(Math.round((await phone.locator('aside').boundingBox()).width),64);
    }
    await phone.setViewportSize({width:390,height:844});
    const history=phone.locator('.insights-history');
    const today=phone.getByRole('region',{name:'Today'});
    assert((await history.boundingBox()).y<(await today.boundingBox()).y);
    const todayText=await today.innerText();
    await phone.getByRole('button',{name:/Last 30 days/}).click();
    await phone.getByRole('option',{name:'Last 7 days'}).click();
    await phone.getByText('126',{exact:true}).waitFor();
    await phone.getByText('Nov 11 – Nov 17, 2026',{exact:true}).waitFor();
    assert.equal(await today.innerText(),todayText);
    await phone.getByRole('button',{name:/Last 7 days/}).click();
    await phone.getByRole('option',{name:'Last 90 days'}).click();
    await phone.getByText('117',{exact:true}).waitFor();
    assert.deepEqual(await phone.locator('.insights-averages dd').allTextContents(),['117','10']);
    assert.equal(await today.innerText(),todayText);
    await phone.screenshot({path:'output/rollcall-visual/insights-phone.png',fullPage:true});
    await phone.getByRole('button',{name:'Open full navigation'}).click();
    await phone.getByRole('dialog',{name:'Full navigation'}).getByRole('button',{name:'Dashboard',exact:true}).click();
    await phone.locator('#dashboard').waitFor();
    await phone.getByRole('button',{name:'Open full navigation'}).click();
    await phone.getByRole('dialog',{name:'Full navigation'}).getByRole('button',{name:'Insights',exact:true}).click();
    await phone.getByText('117',{exact:true}).waitFor();
    assert.deepEqual(errors,[]);
    console.log('PASS: Insights report, two daily averages, activity icons, compact layout, fixed Today values, and navigation.');
  } finally {
    await browser.close();
  }
})().catch(error=>{console.error(error);process.exit(1);});
