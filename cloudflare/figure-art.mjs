/** Original editable vector fashion portraits. All curves and motifs are native SVG. */
const petal = (x, y, scale = 1, colour = '#c4a45e') => `<g transform="translate(${x} ${y}) scale(${scale})" fill="none" stroke="${colour}" stroke-width=".85"><path d="M0 10C-3 2-7-3-6-9C-1-8 2-5 0 0C2-6 5-9 9-9C10-3 5 0 0 1M0 10C4 4 7 2 12 3C11 8 6 11 0 10M0 7C-5 3-8 3-11 5C-9 9-5 11 0 10"/><path d="M0 13V0"/><circle cy="-3" r="2.2" fill="${colour}" stroke="none"/></g>`;
function embroideryRows(festive) {
  let pattern = '';
  for (let row = 0; row < (festive ? 10 : 8); row++) {
    const y = 348 + row * 29;
    const width = festive ? 72 + row * 13 : 61 + row * 4.5;
    for (let col = -3; col <= 3; col++) {
      const x = 314 + col * width / 3 + (row % 2 ? 8 : 0);
      pattern += petal(x, y, .48, '#d0b77e');
    }
  }
  return pattern;
}
function flower(x, y, s = 1, tone = '#e6d7b2') {
  return `<g transform="translate(${x} ${y}) scale(${s})">${Array.from({length:6},(_,i)=>`<path d="M0 0C-9-6-8-18 0-18C8-18 9-6 0 0" transform="rotate(${i*60})" fill="${tone}" stroke="#9c8552" stroke-width=".5"/>`).join('')}<circle r="3.5" fill="#ad8a4e"/><circle r="1.4" fill="#eed399"/></g>`;
}
function garden() {
  return `<g id="botanical-garden"><g fill="none" stroke="#a28e5b" stroke-width="1.2"><path d="M102 699C119 637 71 579 91 515M101 655C145 631 154 594 152 551M102 627C62 605 51 571 55 545M101 585C125 570 127 548 125 526M543 706C525 640 560 594 549 530M537 648C499 633 489 604 489 577M538 620C582 592 588 565 581 535"/></g>${[[91,560,-48],[99,593,53],[100,630,-44],[111,668,55],[145,608,34],[73,589,-50],[539,650,-57],[550,594,49],[540,681,46],[568,582,55],[511,621,-45]].map(([x,y,r])=>`<g transform="translate(${x} ${y}) rotate(${r})"><path d="M0 0C-14-10-13-33 0-43C12-31 13-10 0 0" fill="#345a48" stroke="#a5925f" stroke-width=".8"/><path d="M0-3V-36M0-15l-7-9M0-24l6-7" stroke="#879364" stroke-width=".7" fill="none"/></g>`).join('')}${flower(91,519,.72)}${flower(151,550,.53,'#cfab9f')}${flower(55,543,.5)}${flower(127,527,.4,'#d0a79e')}${flower(549,528,.72)}${flower(581,534,.5,'#cfab9f')}${flower(488,575,.55)}<g stroke="#ac925d" stroke-width="1.3"><path d="M67 689Q105 674 139 689L129 743Q104 754 78 743Z" fill="url(#brass)"/><ellipse cx="103" cy="688" rx="37" ry="8" fill="#2c3d2b"/><path d="M515 699Q541 689 565 699L561 741Q541 751 519 741Z" fill="url(#brass)"/><ellipse cx="541" cy="698" rx="25" ry="6" fill="#263c2e"/><path d="M74 706Q105 715 135 705M78 735Q104 743 130 734M518 716Q542 724 563 715" fill="none" opacity=".7"/></g></g>`;
}
export function fashionPortrait(festive = false) {
  const name=festive?'Marigold dusk':'The emerald courtyard';
  const p=festive?{bg:'#2d232b',stone:'#56404a',dark:'#291e28',lit:'#b36674',mid:'#813e59',shade:'#4d263e',scarf:'#e3bc89',scarfDark:'#b87b61'}:{bg:'#13271f',stone:'#3f5141',dark:'#142a23',lit:'#4c8d7c',mid:'#256651',shade:'#123f36',scarf:'#dcc892',scarfDark:'#9b8752'};
  const tunic=`M282 247Q307 260 340 247L358 281C352 324 353 363 363 405L396 618Q316 646 228 617L256 412C268 365 269 327 264 283Z`;
  const dress=`M282 247Q309 260 340 247L357 282C351 321 353 351 361 381C375 438 429 581 470 690Q322 754 171 691C204 588 249 440 259 382Q273 327 264 283Z`;
  const garment=festive?dress:tunic;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 800" role="img" aria-labelledby="portrait-title portrait-description">
<title id="portrait-title">${name} — Mahrukh fashion illustration</title>
<desc id="portrait-description">An original illustrated Pakistani woman in ${festive?'a rose and mulberry embroidered formal dress':'an emerald embroidered kameez and ivory trousers'}, with a flowing gold dupatta, detailed jewellery and a softly lit courtyard garden. Decorative fashion art, not a product photograph.</desc>
<defs>
 <linearGradient id="backdrop" x2="1" y2="1"><stop stop-color="${p.stone}"/><stop offset=".55" stop-color="${p.bg}"/><stop offset="1" stop-color="${p.dark}"/></linearGradient>
 <radialGradient id="courtyard-light" cx=".4" cy=".3" r=".75"><stop stop-color="#c6b58e" stop-opacity=".15"/><stop offset="1" stop-color="#ac9660" stop-opacity="0"/></radialGradient>
 <linearGradient id="silk" x1="0" x2="1"><stop stop-color="${p.shade}"/><stop offset=".3" stop-color="${p.mid}"/><stop offset=".52" stop-color="${p.lit}"/><stop offset=".72" stop-color="${p.mid}"/><stop offset="1" stop-color="${p.shade}"/></linearGradient>
 <linearGradient id="sleeve" x1="0" x2="1" y2=".4"><stop stop-color="${p.shade}"/><stop offset=".55" stop-color="${p.mid}"/><stop offset=".78" stop-color="${p.lit}"/><stop offset="1" stop-color="${p.mid}"/></linearGradient>
 <linearGradient id="chiffon" x2="1" y2=".5"><stop stop-color="${p.scarf}" stop-opacity=".87"/><stop offset=".3" stop-color="${p.scarfDark}" stop-opacity=".82"/><stop offset=".53" stop-color="#eedcb1" stop-opacity=".88"/><stop offset=".72" stop-color="${p.scarfDark}" stop-opacity=".75"/><stop offset="1" stop-color="${p.scarf}" stop-opacity=".94"/></linearGradient>
 <linearGradient id="skin" x1="0" x2="1" y2=".3"><stop stop-color="#b88064"/><stop offset=".4" stop-color="#e4b38e"/><stop offset=".7" stop-color="#d5a07d"/><stop offset="1" stop-color="#ad745e"/></linearGradient>
 <linearGradient id="ivory"><stop stop-color="#b7b19a"/><stop offset=".4" stop-color="#e9ddba"/><stop offset=".75" stop-color="#d0c5a7"/><stop offset="1" stop-color="#918e7a"/></linearGradient>
 <linearGradient id="brass"><stop stop-color="#665332"/><stop offset=".35" stop-color="#b69b5d"/><stop offset=".7" stop-color="#8d7949"/><stop offset="1" stop-color="#584d32"/></linearGradient>
 <pattern id="woven" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M0 1h5M1 0v5" stroke="#eddfbd" stroke-width=".3" stroke-opacity=".07"/></pattern>
 <pattern id="jaali" width="36" height="36" patternUnits="userSpaceOnUse"><path d="m18 1 5 12 12 5-12 5-5 12-5-12L1 18l12-5Z" fill="none" stroke="#b69b65" stroke-width=".6"/><circle cx="18" cy="18" r="4" fill="none" stroke="#b69b65" stroke-width=".6"/></pattern>
 <pattern id="fine-buti" width="38" height="43" patternUnits="userSpaceOnUse">${petal(19,19,.45,'#f2dba5')}</pattern>
 <clipPath id="garment-clip"><path d="${garment}"/></clipPath>
 <clipPath id="scarf-clip"><path d="M344 237C371 241 392 261 402 287C409 321 422 350 443 380C466 420 451 457 463 500C480 557 501 615 502 681C475 700 436 686 410 671C418 625 408 570 392 518C378 467 377 414 366 372C355 324 338 282 344 237Z"/></clipPath>
</defs>
<g id="courtyard-architecture">
 <path fill="${p.bg}" d="M0 0h640v800H0z"/><path d="M24 770V283C24 169 139 96 250 76Q284 67 320 37Q356 67 390 76C501 96 616 169 616 283V770Z" fill="url(#backdrop)"/>
 <path d="M42 759V281C42 173 151 111 256 91Q292 81 320 58Q348 81 384 91C489 111 598 173 598 281V759Z" fill="none" stroke="#aa945e" stroke-width="1.3"/>
 <path d="M58 750V283Q58 188 154 144Q178 110 220 119Q247 83 283 91L320 76L357 91Q393 83 420 119Q462 110 486 144Q582 188 582 283V750" fill="none" stroke="#bba779" stroke-width=".8" opacity=".75"/>
 <path d="M0 0h640v800H0z" fill="url(#courtyard-light)"/>
 <path d="M80 660V327Q80 284 123 267Q166 284 166 327V660Z" fill="#0e241e" opacity=".35"/><path d="M88 650V329Q88 291 123 277Q158 291 158 329V650Z" fill="url(#jaali)" opacity=".45"/>
 <path d="M476 660V327Q476 284 519 267Q562 284 562 327V660Z" fill="#11251d" opacity=".35"/><path d="M484 650V329Q484 291 519 277Q554 291 554 329V650Z" fill="url(#jaali)" opacity=".45"/>
 <path d="M0 747Q320 730 640 747V800H0Z" fill="#22382c"/><path d="M0 769Q320 747 640 769M74 800l129-59M566 800l-129-59M320 800v-61" fill="none" stroke="#a49569" stroke-opacity=".2"/>
 <path d="M178 163q142-53 284 0" fill="none" stroke="#c2ae79" stroke-width=".7" opacity=".3"/>
</g>
<ellipse cx="321" cy="746" rx="133" ry="13" fill="#0a1915" opacity=".48"/>
<g id="fashion-figure"${festive?' transform="translate(640 0) scale(-1 1)"':''}>
 <g id="trousers-and-jutti">
  <path d="M262 564L247 711Q269 721 289 714L317 597L339 715Q361 721 382 709L363 563Z" fill="url(#ivory)"/>
  <path d="m275 598-12 110M350 596l12 114M252 704q19 9 39 2M339 707q20 7 40-2" fill="none" stroke="#897f62" stroke-width="1.2"/>
  <path d="M249 711Q246 724 232 731Q221 735 225 741Q251 749 282 740L289 716Q269 719 249 711Z" fill="#af8b50" stroke="#d4b273" stroke-width="1"/>
  <path d="M340 716L342 739Q376 752 399 741Q405 736 393 733Q382 727 380 711Q361 719 340 716Z" fill="#b6955c" stroke="#d4b273" stroke-width="1"/>
  <path d="M238 733Q258 726 275 734M353 734q14-6 33 2" fill="none" stroke="#edd09c" stroke-width="1"/>
 </g>
 <g id="tailored-sleeves">
  <path d="M282 248C257 251 245 280 240 307L221 409Q232 424 251 423L275 342L291 275Z" fill="url(#sleeve)" stroke="#6e977d" stroke-width=".65"/>
  <path d="M251 288C247 329 238 366 230 402M262 308l-23 98" fill="none" stroke="#a7b49a" stroke-opacity=".26" stroke-width="1.2"/>
  <path d="M223 395Q239 410 255 408L251 424Q232 427 219 412Z" fill="${p.shade}" stroke="#c4aa73" stroke-width="1.3"/>
  ${Array.from({length:5},(_,i)=>petal(225+i*5.5,406+i*1.5,.3)).join('')}
  <path d="M340 247Q368 248 382 277L412 341Q421 361 404 375L371 395L354 375L386 352L357 308Z" fill="url(#sleeve)" stroke="#6e977d" stroke-width=".65"/>
  <path d="M367 275q12 39 31 73M387 357l-24 20" fill="none" stroke="#adbc9a" stroke-opacity=".3" stroke-width="1.1"/>
  <path d="m373 369 11 19-15 10-15-21Z" fill="${p.shade}" stroke="#d3b97c" stroke-width="1"/>
 </g>
 <g id="embroidered-garment">
  <path d="${garment}" fill="url(#silk)" stroke="#73977a" stroke-width=".7"/>
  <g clip-path="url(#garment-clip)">
   <path d="M264 280Q295 324 280 390Q253 505 246 703M338 279Q321 348 339 409Q376 566 411 719" fill="none" stroke="#d6d5ad" stroke-opacity=".13" stroke-width="9"/>
   ${festive?'<path d="M274 384Q261 539 206 698M298 387Q285 580 278 721M321 390Q327 580 342 722M343 385Q376 563 434 698" stroke="#f0b9ae" stroke-opacity=".25" stroke-width="1.3" fill="none"/>':'<path d="M273 377Q252 513 251 621M294 385Q283 516 290 630M337 391Q350 537 373 623" fill="none" stroke="#9abc9d" stroke-width="1" stroke-opacity=".36"/>'}
   ${embroideryRows(festive)}
   <path d="M150 ${festive?680:598}Q320 ${festive?746:640} 482 ${festive?676:598}" fill="none" stroke="${p.shade}" stroke-width="31"/>
   <path d="M160 ${festive?677:597}Q320 ${festive?741:634} 476 ${festive?675:597}" fill="none" stroke="#c4a76c" stroke-width="1.3"/>
   <path d="M160 ${festive?699:618}Q320 ${festive?763:656} 476 ${festive?696:618}" fill="none" stroke="#ddc893" stroke-width="2"/>
   ${Array.from({length:festive?19:12},(_,i)=>{const x=festive?176+i*16:229+i*15;const y=festive?686+27*Math.sin(i/18*Math.PI):608+17*Math.sin(i/11*Math.PI);return petal(x,y,.62,'#dfc58e');}).join('')}
   <path d="M160 200h330v550H160z" fill="url(#woven)"/>
  </g>
  <path d="M284 250Q310 280 339 250L331 282L313 303L292 282Z" fill="${p.shade}" stroke="#d0b278" stroke-width="1.5"/>
  <path d="M288 253Q312 276 335 252M293 277l19 20 17-20M313 302v44" fill="none" stroke="#e4c996" stroke-width=".7"/>
  ${[313,324,335].map(y=>`<circle cx="313" cy="${y}" r="1.7" fill="#d4b77c"/>`).join('')}
  ${petal(292,287,.53)}${petal(334,286,.53)}
 </g>
 <g id="neck-and-face">
  <path d="M306 213L307 242Q309 253 324 253Q334 251 340 241L337 211Z" fill="url(#skin)"/>
  <path d="M306 222Q321 237 339 218L338 235Q323 245 308 234Z" fill="#9f6d56" opacity=".5"/>
  <path d="M287 179C277 163 285 141 304 136C326 129 350 142 354 164L350 212Q345 232 333 237L292 222Z" fill="#24201b"/>
  <path d="M290 174C294 157 316 151 334 162C347 172 349 191 343 207Q337 224 325 230Q312 234 302 221L292 205Q286 191 290 174Z" fill="url(#skin)"/>
  <path d="M336 172Q342 193 332 213Q327 225 317 229Q331 234 341 214Q352 191 342 177Z" fill="#ad725d" opacity=".4"/>
  <path d="M294 193Q298 186 307 191" stroke="#4a352c" stroke-width="1.3" fill="none" stroke-linecap="round"/>
  <path d="M324 189Q330 185 337 189" stroke="#4a352c" stroke-width="1.3" fill="none" stroke-linecap="round"/>
  <path d="M295 194Q301 197 307 192M325 191Q330 193 336 190" stroke="#54352c" stroke-width=".9" fill="none"/>
  <ellipse cx="302" cy="193" rx="1.2" ry="1.8" fill="#332b24"/><ellipse cx="330" cy="190.5" rx="1.1" ry="1.7" fill="#332b24"/>
  <path d="M292 186Q299 181 307 185M324 183Q330 180 338 183" stroke="#493327" stroke-width="1.8" stroke-linecap="round" fill="none"/>
  <path d="M317 190l-3 13q3 4 7 1" stroke="#a8735b" stroke-width="1" stroke-linecap="round" fill="none"/>
  <path d="M310 214Q315 210 319 212Q323 210 328 211Q320 219 310 214Z" fill="#9b5f57"/><path d="M312 214q8 1 13-2" fill="none" stroke="#6f4742" stroke-width=".65"/><path d="M314 218q5 1 9-1" fill="none" stroke="#dba393" stroke-width=".7"/>
  <path d="M286 179C282 154 300 137 319 139C341 138 351 154 351 176Q339 164 329 158C317 174 305 180 287 184Z" fill="#29231d"/>
  <path d="M325 144Q313 169 290 176M314 144Q300 149 290 163M331 145q15 11 17 25" stroke="#726049" stroke-width="1" stroke-opacity=".45" fill="none"/>
  <path d="M290 178C280 198 285 211 290 231C298 254 283 271 276 283C303 271 310 257 298 230Q285 209 295 181Z" fill="#29251e"/>
  <path d="M289 195q-3 19 6 40q11 26-10 40" fill="none" stroke="#655642" stroke-width=".9" opacity=".65"/>
  <path d="M345 192q8-6 7 4t-8 11" fill="#bd846b" stroke="#a66f58" stroke-width=".6"/>
 </g>
 <g id="jewellery" stroke="#d5b773" fill="#d5b773">
  <circle cx="346" cy="207" r="2.3"/><path d="M346 209v6" stroke-width=".9"/><path d="M346 214q-8 3-8 10h16q0-7-8-10Z" fill="url(#brass)" stroke-width=".8"/>
  <circle cx="339" cy="226" r="1.4"/><circle cx="346" cy="228" r="1.5"/><circle cx="353" cy="226" r="1.4"/>
  <path d="M307 239q15 17 30 0" fill="none" stroke-width="1.5"/><circle cx="322" cy="251" r="2.5" fill="#d7ba80"/>
 </g>
 <g id="flowing-dupatta">
  <path d="M344 237C371 241 392 261 402 287C409 321 422 350 443 380C466 420 451 457 463 500C480 557 501 615 502 681C475 700 436 686 410 671C418 625 408 570 392 518C378 467 377 414 366 372C355 324 338 282 344 237Z" fill="url(#chiffon)" stroke="#e3cc95" stroke-width="1.2"/>
  <g clip-path="url(#scarf-clip)"><path d="M340 230h180v475H340z" fill="url(#fine-buti)" opacity=".65"/><path d="M350 246C387 311 375 348 417 410C441 465 416 497 446 560Q474 625 470 688" fill="none" stroke="#fbebc1" stroke-opacity=".36" stroke-width="4"/><path d="M361 255C394 303 385 358 427 415C445 452 435 498 461 568Q489 626 483 689" fill="none" stroke="#665839" stroke-opacity=".17" stroke-width="8"/></g>
  <path d="M347 240C346 294 363 326 374 372C386 414 387 466 401 517Q427 600 419 667Q461 690 497 679" fill="none" stroke="#765f37" stroke-width="5" opacity=".6"/>
  <path d="M347 240C346 294 363 326 374 372C386 414 387 466 401 517Q427 600 419 667Q461 690 497 679" fill="none" stroke="#f0d7a1" stroke-width="2.2"/>
  <path d="M355 243C389 265 390 290 400 322C413 356 450 391 450 424Q445 471 463 520Q496 608 498 676" fill="none" stroke="#f0d7a1" stroke-width="1.1"/>
  ${Array.from({length:9},(_,i)=>`<path d="M${422+i*9} ${673+10*Math.sin(i/8*Math.PI)}l-2 10" stroke="#dcc28b" stroke-width="1"/><circle cx="${420+i*9}" cy="${685+10*Math.sin(i/8*Math.PI)}" r="1.8" fill="#c7a66a"/>`).join('')}
 </g>
 <g id="natural-hands">
  <path d="M224 415L218 434Q211 443 214 452Q216 456 219 450L222 441L220 460Q221 466 224 462L227 446L226 463Q228 467 231 462L234 447L234 459Q236 462 238 456L243 437L245 424Z" fill="url(#skin)" stroke="#ad785f" stroke-width=".65"/>
  <path d="M226 435l9 2M221 447l3-8M228 444l2-7" stroke="#a8755e" stroke-width=".65" fill="none"/>
  <path d="M367 386L354 393Q344 389 335 391Q328 393 335 397L344 400L326 402Q320 405 327 407L346 407L331 410Q327 413 334 414L351 411L341 417Q340 420 346 418Q363 411 375 400Z" fill="url(#skin)" stroke="#af7c62" stroke-width=".65"/>
  <path d="M343 401l11 1M349 407l9-2M359 395l4 8" stroke="#a57159" stroke-width=".6" fill="none"/>
  <path d="m223 419 21 8M221 423l22 7M365 384l12 17M361 388l12 17" fill="none" stroke="#ddbd77" stroke-width="2"/>
  <ellipse cx="345" cy="405" rx="1.3" ry="2.2" fill="#e2bd78"/>
 </g>
</g>
${garden()}
<g id="fine-frame" fill="none" stroke="#aa915e"><path d="M17 781H623M23 788H617" stroke-width=".7" opacity=".6"/><path d="M24 744V282M616 744V282" stroke-width=".6" opacity=".3"/></g>
</svg>`;
}
