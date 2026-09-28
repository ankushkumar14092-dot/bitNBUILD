const localNow = new Date();
export const TODAY = new Date(Date.UTC(localNow.getFullYear(), localNow.getMonth(), localNow.getDate()));
export const roundCurrency = n => Math.round((Number(n)+Number.EPSILON)*100)/100;
export const fmt = n => Number(n).toLocaleString('en-US', {maximumFractionDigits: 0});
export const money = n => '$' + fmt(n);
export const shortMoney = n => '$' + (n/1000000).toFixed(2) + 'M';
export const dateLabel = d => new Date(d).toLocaleDateString('en-GB', {day:'2-digit',month:'short',timeZone:'UTC'});
export const dateLabelYear = d => new Date(d).toLocaleDateString('en-GB', {day:'2-digit',month:'short',year:'numeric',timeZone:'UTC'});
export const dateISO = d => new Date(d).toISOString().slice(0,10);
export const addDays = (d,days) => { const a = new Date(d); a.setUTCDate(a.getUTCDate()+days); return a; };
const currentYear = TODAY.getUTCFullYear();
export const portData = [
 {name:'Paradip',state:'Odisha',wait:2.4,ships:18,risk:'Medium',trend:-0.6,capacity:72,weather:'Seasonal swell',note:'Moderate anchorage queue. Allow a 3-day arrival buffer.',x:207,y:155},
 {name:'Visakhapatnam',state:'Andhra Pradesh',wait:1.2,ships:9,risk:'Low',trend:-0.3,capacity:54,weather:'Clear conditions',note:'Berth availability is favorable. Normal operations assumed.',x:164,y:197},
 {name:'Kolkata / Haldia',state:'West Bengal',wait:4.8,ships:24,risk:'High',trend:1.2,capacity:91,weather:'Tidal restrictions',note:'Elevated queue and draft restrictions. Confirm berth and tidal access.',x:239,y:124},
 {name:'Chennai',state:'Tamil Nadu',wait:1.8,ships:12,risk:'Low',trend:-0.2,capacity:61,weather:'Light showers',note:'Stable operations. Monitor northeast monsoon development.',x:135,y:270}
];
export const shipments = [
 {id:`CR-${currentYear}-014`,cargo:'Thermal coal',tonnes:75000,origin:'Newcastle, AU',dest:'Paradip',laycanStart:dateISO(addDays(TODAY,14)),laycanEnd:dateISO(addDays(TODAY,22)),arrival:dateISO(addDays(TODAY,38)),risk:'Medium',status:'Ready to plan',rate:25.4},
 {id:`CR-${currentYear}-013`,cargo:'Limestone',tonnes:55000,origin:'Richards Bay, ZA',dest:'Visakhapatnam',laycanStart:dateISO(addDays(TODAY,10)),laycanEnd:dateISO(addDays(TODAY,17)),arrival:dateISO(addDays(TODAY,33)),risk:'Low',status:'In review',rate:27.1},
 {id:`CR-${currentYear}-012`,cargo:'Phosphate rock',tonnes:40000,origin:'Santos, BR',dest:'Kolkata / Haldia',laycanStart:dateISO(addDays(TODAY,17)),laycanEnd:dateISO(addDays(TODAY,24)),arrival:dateISO(addDays(TODAY,47)),risk:'High',status:'Action required',rate:31.2},
 {id:`CR-${currentYear}-011`,cargo:'Thermal coal',tonnes:60000,origin:'Taboneo, ID',dest:'Chennai',laycanStart:dateISO(addDays(TODAY,7)),laycanEnd:dateISO(addDays(TODAY,14)),arrival:dateISO(addDays(TODAY,26)),risk:'Low',status:'Booked',rate:18.5}
];
export const initialForm = {cargo:'Coal',volume:75000,origin:'Newcastle, Australia',destination:'Paradip',laycanStart:dateISO(addDays(TODAY,14)),laycanEnd:dateISO(addDays(TODAY,22)),arrival:dateISO(addDays(TODAY,38)),charter:'Open',inventory:110000,consumption:2500};
export const drivers = [
 {name:'Bunker prices',detail:'Fuel proxy easing week-on-week',impact:-18,width:88},
 {name:'Vessel availability',detail:'More open tonnage in the Pacific',impact:-11,width:61},
 {name:'Seasonal demand',detail:'Restocking ahead of winter',impact:8,width:46},
 {name:'Port congestion',detail:'Longer wait times at Haldia',impact:6,width:32},
 {name:'Historical route index',detail:'Softening dry-bulk market',impact:-4,width:24}
];
export function forecastData(horizon=30,route='all',signal='Freight rate') {
 const h=[29.1,28.7,29.5,28.9,29.3,28.1,28.5,27.8,28.4,27.5,27.9,27.4];
 const f = horizon===30?[27.4,27.1,27.25,26.7,26.8,26.3,26.4,25.9]:horizon===60?[27.4,27.1,26.7,25.9,25.7,26.2,25.6,25.3]:[27.4,26.7,25.9,25.7,25.3,26.1,26.5,26.2];
 const mult=route==='Indonesia → India'?0.73:route==='South Africa → India'?1.1:1;
 const adjust=v=>signal==='Bunker'?v*19.2:signal==='Seasonality'?100+(v-27)*8:signal==='Demand'?100+(v-27)*5:signal==='Vessel supply'?100-(v-27)*6:v*mult;
 const all=h.map((v,i)=>({date:dateLabel(addDays(TODAY,(i-11)*5)),bunker:563-i*3.1,actual:adjust(v),backtest:adjust(v+(i%2?0.55:-0.38))}));
 f.forEach((v,i)=>{ const point={date:dateLabel(addDays(TODAY,Math.round(i*horizon/7))),bunker:529-i*2.8,forecast:adjust(v),band:[adjust(v)-(.45+i*.13)*(signal==='Bunker'?19.2:1),adjust(v)+(.45+i*.13)*(signal==='Bunker'?19.2:1)]}; if(i===0) Object.assign(all[all.length-1],point); else all.push(point); });
 return all;
}
export function analyze(form, adjustments={}) {
 const v=Number(form.volume), port=portData.find(p=>p.name===form.destination)||portData[0];
 const originFactor=form.origin.includes('Taboneo')?.73:form.origin.includes('Richards')?1.1:form.origin.includes('Santos')?1.3:1;
 const transit=form.origin.includes('Taboneo')?12:form.origin.includes('Santos')?32:form.origin.includes('Richards')?24:18;
 const fuel=1+(Number(adjustments.fuel||0)/100)*.32;
 const slots=[{id:'A',vessel:v>82000?'Capesize':v>58000?'Panamax':'Supramax',capacity:v>82000?180000:v>58000?82000:58000,offset:3,rate:25.4,delay:port.wait,risk:port.risk,reason:'Balanced freight cost and arrival certainty'}, {id:'B',vessel:'Supramax',capacity:58000,offset:0,rate:27.1,delay:Math.max(0,port.wait-1.2),risk:port.risk==='High'?'Medium':'Low',reason:'Earlier loading; lower delay exposure'}, {id:'C',vessel:v>82000?'Capesize':'Panamax',capacity:v>82000?180000:82000,offset:7,rate:24.3,delay:port.wait+2.5,risk:'High',reason:'Lower freight; less arrival buffer'}];
 const results = slots.map(o=>{
 const count=Math.ceil(v/o.capacity);
 const rate=+(o.rate*originFactor*fuel*(form.cargo==='Fertilizer raw materials'?1.05:1)*(form.charter==='Time charter'?1.04:form.charter==='Contract of affreightment'?.98:1)).toFixed(2);
 const delay=Math.max(0,o.delay+Number(adjustments.delay||0));
 const freight=roundCurrency(v*rate),insurance=roundCurrency(v*.56),charges=roundCurrency(count*118000),demurrage=roundCurrency(Math.max(0,delay-1)*35000*count);
 const eta=addDays(form.laycanStart,transit+o.offset+Math.ceil(delay));
 const laycanOK=addDays(form.laycanStart,o.offset)<=new Date(form.laycanEnd);
 const daysToArrival=Math.ceil((eta-TODAY)/86400000),cover=Number(form.inventory)/Number(form.consumption);
 const buffer=cover-daysToArrival;
 const feasible=eta<=new Date(form.arrival)&&laycanOK;
 const bookStart = new Date(Math.max(+TODAY,+addDays(form.laycanStart, o.id==='A'?-11:o.id==='B'?-14:-5)));
 const bookEnd = new Date(Math.max(+bookStart,Math.min(+addDays(bookStart,6),+addDays(form.laycanStart,-1))));
 const window = dateLabelYear(bookStart)+' – '+dateLabelYear(bookEnd);
 return {...o,window,count,rate,delay,freight,insurance,charges,demurrage,total:roundCurrency(freight+insurance+charges+demurrage),eta,buffer,feasible,review:!feasible||buffer<3||o.risk==='High',confidence:'Moderate',port,transit};
 });
 const supported=results.filter(o=>o.feasible&&o.buffer>=3&&o.risk!=='High').sort((a,b)=>a.total-b.total);
 const candidate=supported[0]||results.filter(o=>o.feasible).sort((a,b)=>a.total-b.total)[0]||results[0];
 return results.map(o=>({...o,isRecommended:o.id===candidate.id,noFeasible:!results.some(r=>r.feasible)}));
}
export function validate(form){
 if(!Number.isFinite(+form.volume)||+form.volume<1000||+form.volume>360000) return 'Enter a cargo volume between 1,000 and 360,000 MT.';
 if(!form.laycanStart||!form.laycanEnd||!form.arrival) return 'Complete the laycan and required arrival dates.';
 if(new Date(form.laycanStart)<TODAY) return `Laycan must start on or after ${dateLabelYear(TODAY)}, the scenario date.`;
 if(form.laycanEnd<form.laycanStart) return 'Laycan end must be on or after the start date.';
 if(form.arrival<=form.laycanStart) return 'Required arrival must be after the laycan start.';
 if(!Number.isFinite(+form.inventory)||!Number.isFinite(+form.consumption)||+form.inventory<0||+form.consumption<=0) return 'Inventory must be zero or higher and daily consumption must be greater than zero.';
 return '';
}
export function downloadCSV(name,rows){
 const csv=rows.map(row=>row.map(v=>'"'+String(v??'').replaceAll('"','""')+'"').join(',')).join('\r\n');
 const url=URL.createObjectURL(new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8;'}));
 const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
