import {test,expect} from '@playwright/test';
const nav=(page,name)=>page.locator('.main-nav').getByRole('button',{name,exact:true}).click();
test('overview and forecast controls',async({page})=>{
 await page.goto('/');await expect(page.getByRole('heading',{level:1})).toHaveText('Cargo Intelligence Control Tower');
 await page.getByRole('button',{name:'60 days',exact:true}).click();await expect(page.locator('.kpi').nth(1)).toContainText('$25.30');
 await page.getByRole('button',{name:'Bunker',exact:true}).click();await expect(page.getByRole('button',{name:'Bunker',exact:true})).toHaveAttribute('aria-pressed','true');
 await page.getByRole('button',{name:'Toggle bunker overlay',exact:true}).click();await expect(page.locator('.chart-legend')).toContainText('Bunker · right axis');
 await page.getByRole('button',{name:'Toggle prior forecast',exact:true}).click();await expect(page.locator('.chart-legend')).toContainText('Prior forecast');
 await page.getByRole('combobox',{name:'Region and port scope'}).selectOption('Chennai');await expect(page.locator('.port-row')).toHaveCount(1);await expect(page.locator('.cargo-panel tbody tr')).toHaveCount(1);
});
test('cargo search, status filters and CSV download',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Needs attention'}).click();await expect(page.locator('.cargo-panel tbody tr')).toHaveCount(1);await expect(page.locator('.cargo-panel tbody')).toContainText('CR-2026-012');
 await page.getByRole('button',{name:'All requirements'}).click();await page.getByRole('button',{name:'Search cargo requirements'}).click();await page.getByPlaceholder('Search cargo, route or requirement ID…').fill('limestone');await expect(page.locator('.cargo-panel tbody tr')).toHaveCount(1);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export CSV',exact:true}).click();await expect((await download).suggestedFilename()).toContain('cargo-requirements');
});
test('generate, compare, save and restore a charter scenario',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Generate recommendation',exact:true}).click();await expect(page.getByRole('heading',{level:1})).toHaveText('Charter Recommendation');
 await expect(page.locator('.recommendation-result')).toContainText('YOUR CHARTER STRATEGY');await expect(page.locator('.rec-title')).toContainText('Panamax');await expect(page.locator('.options-panel tbody tr')).toHaveCount(3);
 await expect(page.locator('.rec-metrics')).toContainText('$2.08M');await page.getByRole('button',{name:'Save',exact:true}).click();
 await nav(page,'Scenario Planning');await expect(page.locator('tbody tr')).toHaveCount(1);await page.getByRole('slider',{name:'Bunker price change'}).fill('20');await expect(page.locator('.scenario-results')).not.toContainText('+$0');await page.getByRole('button',{name:'Save scenario',exact:true}).click();await expect(page.locator('tbody tr')).toHaveCount(2);
 await page.reload();await expect(page.locator('tbody tr')).toHaveCount(2);await page.getByRole('button',{name:'Restore',exact:true}).first().click();await expect(page.getByRole('slider',{name:'Bunker price change'})).toHaveValue('20');
});
test('invalid laycan and infeasible scenario are clearly flagged',async({page})=>{
 await page.goto('/#charter-recommendation');await page.getByLabel('Laycan end',{exact:true}).fill('2026-10-01');await page.getByRole('button',{name:'Generate recommendation',exact:true}).click();await expect(page.getByRole('alert')).toContainText('Laycan end must');
 await page.getByLabel('Laycan end',{exact:true}).fill('2026-10-20');await page.getByLabel('Required arrival by',{exact:true}).fill('2026-10-15');await page.getByRole('button',{name:'Generate recommendation',exact:true}).click();await expect(page.locator('.recommendation-result')).toContainText('NO FEASIBLE STRATEGY');await expect(page.locator('.rec-warning')).toContainText('No candidate meets');
});
test('landed cost assumptions recalculate and export',async({page})=>{
 await page.goto('/#landed-cost');const before=await page.locator('.cost-total').textContent();await page.getByLabel('Insurance (USD / MT)',{exact:true}).fill('1.5');await expect(page.locator('.cost-total')).not.toHaveText(before);
 await page.getByRole('button',{name:'Reset assumptions'}).click();await expect(page.locator('.cost-total')).toHaveText(before);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export this cost breakdown'}).click();expect((await download).suggestedFilename()).toBe('CARGO-PILOT-custom-landed-cost.csv');
});
test('port selection and locally persisted review',async({page})=>{
 await page.goto('/#port-risk');await page.getByRole('button',{name:'Select Kolkata / Haldia',exact:true}).click();await expect(page.locator('.port-details')).toContainText('4.8 days');await page.getByRole('button',{name:'Request human review'}).click();
 await page.getByLabel('Review note').fill('Confirm safe draft before booking.');await page.getByRole('button',{name:'Record review'}).click();await expect(page.locator('.port-details')).toContainText('Confirm safe draft before booking.');await page.reload();await page.getByRole('button',{name:'Select Kolkata / Haldia',exact:true}).click();await expect(page.locator('.port-details')).toContainText('Confirm safe draft before booking.');
});
test('inventory changes affect stock cover and raise warning',async({page})=>{
 await page.goto('/#inventory-sync');await page.getByLabel('Current inventory (MT)',{exact:true}).fill('10000');await expect(page.locator('.inventory-kpi').nth(1)).toContainText('4.0 days');await expect(page.locator('.notice')).toContainText('Escalate the supply plan');
});
test('vessel filtering and details',async({page})=>{
 await page.goto('/#vessel-market');await page.getByPlaceholder('Search vessel or open location…').fill('Pacific');await expect(page.locator('tbody tr')).toHaveCount(1);await page.getByRole('button',{name:'View profile',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('82,000 DWT');await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
});
test('notification state, help modal and user preferences',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'View notifications',exact:true}).click();await page.getByRole('button',{name:'Mark all as read'}).click();await expect(page.getByRole('dialog')).toContainText('All caught up');await page.keyboard.press('Escape');
 await page.getByRole('button',{name:'Profile settings',exact:true}).click();await page.getByLabel('Display name').fill('Maya Patel');await page.getByRole('button',{name:'Save preferences'}).click();await expect(page.locator('.profile-person')).toContainText('Maya Patel');await page.reload();await expect(page.locator('.profile-person')).toContainText('Maya Patel');
 await page.getByRole('button',{name:'Help & resources',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('Define your requirement');await page.keyboard.press('Escape');
});
test('reports download and record export activity',async({page})=>{
 await page.goto('/#reports');const download=page.waitForEvent('download');await page.getByRole('button',{name:'Download',exact:true}).first().click();expect((await download).suggestedFilename()).toContain('charter-decision-brief');await expect(page.locator('tbody tr')).toHaveCount(1);
});
test('all desktop pages load without runtime errors',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('/');for(const name of ['Freight Forecast','Charter Recommendation','Landed Cost','Port Risk','Inventory Sync','Vessel Market','Scenario Planning','Reports','Overview']){await nav(page,name);await expect(page.getByRole('heading',{level:1})).toBeVisible();expect(await page.evaluate(()=>document.body.scrollWidth<=innerWidth)).toBeTruthy();}expect(errors).toEqual([]);
});
test('mobile navigation, no overflow, and accessible requirement dialog',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');await page.evaluate(()=>document.fonts.ready);expect(await page.evaluate(()=>document.body.scrollWidth)).toBe(390);
 await page.getByRole('button',{name:'Open navigation'}).click();await nav(page,'Scenario Planning');await expect(page.getByRole('heading',{level:1})).toHaveText('Scenario Planning');expect(await page.evaluate(()=>document.body.scrollWidth)).toBe(390);
 await page.getByRole('button',{name:'New requirement'}).click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.getByLabel('Laycan start',{exact:true})).toBeVisible();await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.locator('.mobile-bottom').getByRole('button',{name:'Overview',exact:true}).click();await expect(page.getByRole('heading',{level:1})).toContainText('Control Tower');
});
