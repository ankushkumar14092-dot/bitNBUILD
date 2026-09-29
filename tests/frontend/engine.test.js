import test from 'node:test';
import assert from 'node:assert/strict';
import {analyze,validate,initialForm,forecastData} from '../../frontend/src/data.js';

test('default charter model has a feasible Panamax candidate and reconciled cost',()=>{
 const options=analyze(initialForm),a=options.find(o=>o.isRecommended);
 assert.equal(options.length,3);assert.equal(a.id,'A');assert.equal(a.feasible,true);
 assert.equal(a.freight,1905000);assert.equal(a.insurance,42000);assert.equal(a.charges,118000);assert.equal(a.demurrage,49000);
 assert.equal(a.total,2114000);assert.equal(a.total,a.freight+a.insurance+a.charges+a.demurrage);
 assert.equal(a.eta.toISOString().slice(0,10),'2026-11-05');assert.equal(a.buffer,6);
 assert.equal(options[1].count,2);assert.equal(options[2].feasible,false);
});
test('none feasible is flagged rather than offered as an executable recommendation',()=>{
 const opts=analyze({...initialForm,arrival:'2026-10-15'});
 assert.ok(opts.every(o=>o.noFeasible&&o.review&&!o.feasible));
});
test('an earlier required arrival selects the earlier feasible strategy',()=>{
 const opts=analyze({...initialForm,arrival:'2026-11-02'});
 assert.equal(opts.find(o=>o.isRecommended).id,'B');
});
test('low plant stock requires review',()=>{
 const opts=analyze({...initialForm,inventory:10000});assert.ok(opts.every(o=>o.review&&o.buffer<0));
});
test('high cargo volumes calculate multiple compatible capacity units',()=>{
 const opts=analyze({...initialForm,volume:360000});assert.equal(opts[0].vessel,'Capesize');assert.equal(opts[0].count,2);assert.equal(opts[1].count,7);
});
test('fuel and port-delay stress increase cost and move arrival',()=>{
 const base=analyze(initialForm)[0],stress=analyze(initialForm,{fuel:20,delay:4})[0];assert.ok(stress.total>base.total);assert.ok(stress.eta>base.eta);assert.ok(stress.buffer<base.buffer);
});
test('invalid volumes, dates and run-rate are rejected',()=>{
 assert.equal(validate(initialForm),'');
 for(const change of [{volume:0},{volume:-10},{volume:400000},{volume:'invalid'},{laycanEnd:'2026-10-01'},{arrival:'2026-10-01'},{laycanStart:'2026-01-01'},{consumption:0},{inventory:-1}])assert.notEqual(validate({...initialForm,...change}),'');
});
test('forecast horizons change outcome while retaining historical continuity',()=>{
 const d30=forecastData(30),d60=forecastData(60);assert.equal(d30.at(-1).forecast,25.9);assert.equal(d60.at(-1).forecast,25.3);assert.equal(d30[11].actual,d30[11].forecast);assert.ok(d30.at(-1).band[0]<d30.at(-1).forecast);
});
