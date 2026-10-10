const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
 const routes=require('../routes.json');
 fs.mkdirSync('/tmp/feucht-inspect',{recursive:true});
 const report={pages:[],errors:[],missingResources:[],checks:[]};
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]) {
  const page=await browser.newPage({viewport});
  page.on('pageerror',e=>report.errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)report.missingResources.push({status:r.status(),url:r.url()})});
  await page.route('https://**/*',route=>route.abort());
  for(const route of routes){
   const response=await page.goto('http://127.0.0.1:8000/feucht'+(route==='/'?'/':route+'/'),{waitUntil:'domcontentloaded'});
   await page.locator('h1').first().waitFor();
   await page.evaluate(()=>document.fonts.ready);
   await page.waitForTimeout(400);
   report.pages.push({route,width:viewport.width,status:response.status(),heading:await page.locator('h1').first().innerText(),overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)});
  }
  await page.goto('http://127.0.0.1:8000/feucht/',{waitUntil:'domcontentloaded'});
  await page.waitForTimeout(1000);
  for(let i=0;i<3;i++){
   const reject=page.getByRole('button',{name:'Ablehnen',exact:true});
   if(await reject.count())await reject.last().click();
  }
  if(viewport.width===390){
   await page.getByRole('button',{name:'Menü öffnen'}).click();
   await page.getByRole('link',{name:'Wie es funktioniert',exact:true}).first().click();
   await page.waitForURL('**/feucht/wie-es-funktioniert');
   report.checks.push('Mobile navigation works');
  } else {
   await page.getByRole('link',{name:'Ratgeber',exact:true}).first().click();
   await page.waitForURL('**/feucht/ratgeber');
   report.checks.push('Desktop client navigation stays under /feucht');
  }
  await page.goto('http://127.0.0.1:8000/feucht/',{waitUntil:'domcontentloaded'});
  await page.waitForTimeout(500);
  for(let y=0;y<await page.evaluate(()=>document.body.scrollHeight);y+=700){await page.evaluate(y=>scrollTo(0,y),y);await page.waitForTimeout(120);}
  await page.evaluate(()=>scrollTo(0,0));await page.waitForTimeout(600);
  await page.screenshot({path:'/tmp/feucht-inspect/copy-'+viewport.width+'.png',fullPage:true});
  await page.goto('http://127.0.0.1:8000/feucht/check/',{waitUntil:'domcontentloaded'});
  await page.getByLabel('Postleitzahl',{exact:true}).fill('1010');
  await page.getByRole('button',{name:'Weiter',exact:true}).click();
  await page.waitForTimeout(400);
  const answers=[['Feuchte Wand'],['Immer'],['Einfamilienhaus','vor 1945'],['Nur eine kleine Stelle']];
  for(const group of answers){
    for(const answer of group)await page.locator('#funnel').getByRole('button',{name:new RegExp(answer+'$')}).click();
    await page.getByRole('button',{name:'Weiter',exact:true}).click();
    await page.waitForTimeout(400);
  }
  await page.getByLabel('E-Mail-Adresse',{exact:true}).waitFor();
  if(!await page.getByRole('button',{name:'Ersteinschätzung anzeigen',exact:true}).isDisabled())throw new Error('Empty email should block submission');
  report.checks.push('Questionnaire reaches step 6 and requires email at width '+viewport.width+'; API submission not executed');
  await page.close();
 }
 report.missingResources=[...new Map(report.missingResources.map(r=>[r.url,r])).values()];
 fs.writeFileSync(path.join(__dirname,'../validation.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
 await browser.close();
 if(report.errors.length||report.pages.some(p=>p.status!==200||p.overflow)||report.missingResources.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
