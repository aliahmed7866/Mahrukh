import {DatabaseSync} from 'node:sqlite';
export function localDB(path=':memory:'){
 const db=new DatabaseSync(path);const adapter={raw:db,prepare(sql){let values=[];const object={bind(...v){values=v.map(x=>x instanceof ArrayBuffer?new Uint8Array(x):x);return object;},async first(){return db.prepare(sql).get(...values)||null;},async all(){return {results:db.prepare(sql).all(...values)};},async run(){const r=db.prepare(sql).run(...values);return {meta:{changes:Number(r.changes)}};}};return object;},async batch(list){db.exec('BEGIN');try{const out=[];for(const s of list)out.push(await s.run());db.exec('COMMIT');return out;}catch(e){db.exec('ROLLBACK');throw e;}}};return adapter;
}
