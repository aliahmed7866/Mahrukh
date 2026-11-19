import {DatabaseSync} from 'node:sqlite';
// Match D1's Workers binding: BLOB columns are read back as number arrays.
const d1Row=row=>row?Object.fromEntries(Object.entries(row).map(([key,value])=>[key,value instanceof Uint8Array?Array.from(value):value])):null;
export function localDB(path=':memory:'){
 const db=new DatabaseSync(path);const adapter={raw:db,prepare(sql){let values=[];const object={bind(...v){values=v.map(x=>x instanceof ArrayBuffer?new Uint8Array(x):x);return object;},async first(){return d1Row(db.prepare(sql).get(...values));},async all(){return {results:db.prepare(sql).all(...values).map(d1Row)};},async run(){const r=db.prepare(sql).run(...values);return {meta:{changes:Number(r.changes)}};}};return object;},async batch(list){db.exec('BEGIN');try{const out=[];for(const s of list)out.push(await s.run());db.exec('COMMIT');return out;}catch(e){db.exec('ROLLBACK');throw e;}}};return adapter;
}
