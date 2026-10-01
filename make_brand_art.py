"""Reproduce Mahrukh's original decorative SVG fashion illustrations.

These editorial drawings are brand artwork, never product photographs or
evidence of a garment's materials, origin or embroidery technique. The two
figures have deliberately different silhouettes and gestures. No third-party
assets, fonts, external references or raster images are needed.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'static/art'


def canvas(title, description, drawing, *, rose=False):
    paper = '#f0e7df' if rose else '#f3eee3'
    wash = '#e4cec5' if rose else '#dce2d3'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 760" role="img" aria-labelledby="title description">
<title id="title">{title}</title>
<desc id="description">{description}</desc>
<defs>
 <linearGradient id="paper" x2="0" y2="1"><stop stop-color="{paper}"/><stop offset="1" stop-color="#e9dfd0"/></linearGradient>
 <radialGradient id="wash"><stop stop-color="{wash}" stop-opacity=".8"/><stop offset="1" stop-color="{wash}" stop-opacity="0"/></radialGradient>
 <linearGradient id="emerald" x1="0" y1="0" x2="1" y2=".2"><stop stop-color="#163e37"/><stop offset=".45" stop-color="#346c5b"/><stop offset="1" stop-color="#204f44"/></linearGradient>
 <linearGradient id="ruby" x1="0" y1="0" x2="1" y2=".35"><stop stop-color="#673441"/><stop offset=".48" stop-color="#a85b64"/><stop offset="1" stop-color="#763b49"/></linearGradient>
 <linearGradient id="silk" x1="0" y1="0" x2="1" y2=".3"><stop stop-color="#c99a8e"/><stop offset=".5" stop-color="#dfb7a6"/><stop offset="1" stop-color="#ac766f"/></linearGradient>
 <linearGradient id="sage" x1="0" y1="0" x2="1" y2=".7"><stop stop-color="#91a28b"/><stop offset=".6" stop-color="#bec7aa"/><stop offset="1" stop-color="#7d9480"/></linearGradient>
 <g id="sprig" fill="none" stroke="#bda26d" stroke-width="1.2" stroke-linecap="round">
  <path d="M0 10C1 2-1-6 0-14M0 3C-8 0-10-5-9-7C-3-7 0-2 0 3M0-4C7-6 9-11 8-13C2-12 0-8 0-4"/>
  <circle cy="-17" r="1.7" fill="#cfb27d" stroke="none"/>
 </g>
</defs>
<rect width="600" height="760" fill="url(#paper)"/>
<ellipse cx="307" cy="328" rx="261" ry="322" fill="url(#wash)"/>
{drawing}
</svg>
'''


def heritage_portrait():
    return canvas(
        'A woman in an emerald kameez, trousers and dupatta',
        'Original decorative fashion illustration. A woman in a flowing emerald kameez and ivory trousers gently gathers a sage dupatta. Fine botanical lines sit against warm ivory.',
        '''<!-- A light architectural curve and a single quiet botanical gesture. -->
<path d="M106 577V270C106 142 181 87 298 87C411 87 487 153 487 276V593" fill="none" stroke="#b7a280" stroke-width="1" opacity=".46"/>
<path d="M124 651C89 606 101 548 158 512M116 610C91 597 81 577 91 563C112 573 118 590 116 610M113 579C140 571 152 550 146 540C128 545 117 557 113 579M128 545C119 524 122 506 135 500C146 516 141 532 128 545" fill="none" stroke="#8d9b80" stroke-width="1.6" opacity=".63"/>
<path d="M397 684C426 687 452 688 479 681" fill="none" stroke="#ae9771" opacity=".45"/>
<ellipse cx="307" cy="697" rx="99" ry="10" fill="#665447" opacity=".09"/>
<!-- Softly tapered trousers and simple low shoes. -->
<path d="M257 547C257 585 261 622 267 675L296 677C302 628 307 595 312 563L323 672L357 674C364 624 363 586 354 545Z" fill="#dbd7c7"/>
<path d="M271 583C279 618 278 645 279 672M341 592C337 620 340 647 343 671" fill="none" stroke="#b8baaa" stroke-width="2"/>
<path d="M269 672C268 679 263 684 252 687C245 689 242 694 249 696C264 700 284 696 296 692L295 674M325 670L325 685C337 691 354 698 368 694C373 690 358 684 352 680L352 671" fill="#927859"/>
<path d="M250 692C264 694 279 690 291 687M331 681L349 687" fill="none" stroke="#c0a779" stroke-width="1.4"/>
<!-- The dupatta falls behind one shoulder in one broad, unbroken curve. -->
<path d="M330 244C354 238 373 259 381 293C392 334 399 379 402 426C405 485 421 546 431 590C419 602 395 607 378 595C365 538 353 492 352 444C348 385 339 321 314 274Z" fill="url(#sage)"/>
<path d="M354 253C378 313 383 369 385 427C387 489 403 550 416 594M363 258C386 314 391 373 393 425C395 491 412 550 423 591" fill="none" stroke="#e0d3aa" stroke-width="1.4" opacity=".9"/>
<path d="M384 593C399 598 412 595 423 590" fill="none" stroke="#ac996e" stroke-width="2"/>
<!-- Hair, a turned face, and a relaxed neckline. -->
<path d="M268 175C263 148 280 128 306 130C337 131 352 155 343 184C337 202 342 222 354 236C338 248 316 243 302 224L272 214Z" fill="#302b28"/>
<path d="M334 181C359 167 366 195 351 207C343 214 333 207 329 201Z" fill="#36302c"/>
<path d="M293 215C299 231 294 240 282 253L316 268L335 251C317 247 316 234 319 217Z" fill="#bc886b"/>
<path d="M278 161C289 147 309 148 320 164C332 181 326 204 315 218C307 228 296 230 285 221C277 214 274 205 273 198L266 194C266 191 272 187 274 182Z" fill="#d4a484"/>
<path d="M276 178C279 167 289 160 302 157C289 151 279 155 276 168M301 155C318 165 322 182 326 192L332 178C332 159 318 148 301 155" fill="#302b28"/>
<path d="M277 184C281 182 286 182 289 184M278 187C281 189 284 189 286 187M276 199L282 201M282 211C286 213 290 213 294 210" fill="none" stroke="#725548" stroke-width="1.4" stroke-linecap="round"/>
<path d="M315 201C321 195 325 199 321 206" fill="none" stroke="#ad795f" stroke-width="1.4"/>
<circle cx="319" cy="210" r="3.2" fill="#be9a59"/><path d="M319 214L316 225Q320 231 324 224L322 214" fill="#bd9a5c"/>
<!-- A long kameez with shaped shoulders, easy sleeves and an uneven drape. -->
<path d="M282 249C267 250 250 255 240 267C226 287 220 320 213 350L193 421C199 434 213 441 228 438L255 353C257 385 252 428 247 469L235 582C263 597 292 602 322 601C344 601 363 596 382 587C367 541 357 500 352 459C347 420 346 385 349 351L369 383C382 380 392 372 397 361C382 327 370 296 352 271C342 258 330 252 317 249C308 261 296 265 282 249Z" fill="url(#emerald)"/>
<path d="M275 255C268 291 272 311 287 333M318 266C329 294 329 321 325 346M259 363C250 414 248 475 244 541M332 360C331 445 345 514 364 575M291 441C288 491 291 544 300 589" fill="none" stroke="#0e332d" stroke-width="2.4" opacity=".45"/>
<path d="M269 278C255 304 250 324 249 344M281 379C273 441 271 494 272 545M321 484C324 522 333 557 341 581" fill="none" stroke="#77a080" stroke-width="1.4" opacity=".35"/>
<path d="M282 250C287 267 293 281 308 286C316 277 318 265 318 252" fill="none" stroke="#c5a66d" stroke-width="2"/>
<path d="M307 286L309 312" fill="none" stroke="#c5a66d" stroke-width="1.4"/><circle cx="308" cy="295" r="1.5" fill="#d8bd88"/><circle cx="309" cy="306" r="1.5" fill="#d8bd88"/>
<path d="M240 575C276 590 334 599 376 581M240 580C279 596 334 603 377 586M197 414C205 424 216 429 231 429M366 371C377 367 384 362 389 353" fill="none" stroke="#c4aa72" stroke-width="1.6"/>
<use href="#sprig" transform="translate(258 567) rotate(-9) scale(.8)"/><use href="#sprig" transform="translate(303 578) scale(.8)"/><use href="#sprig" transform="translate(350 573) rotate(8) scale(.8)"/>
<!-- One relaxed wrist; the other hand gently gathers the cloth. -->
<path d="M198 427C194 441 192 450 196 461C199 470 203 474 206 472L205 455C208 462 211 468 214 466C215 463 209 449 210 442L222 435Z" fill="#d0a080"/>
<path d="M206 448L209 457M200 443C198 450 199 456 201 462" fill="none" stroke="#ad7e64" stroke-width="1.2" stroke-linecap="round"/>
<path d="M369 378C355 390 337 393 317 385L303 379C297 375 291 375 287 378L278 386C278 390 284 391 290 387L301 388C310 397 324 403 338 404C361 406 376 398 385 386Z" fill="#c79577"/>
<path d="M294 383L306 388M299 379L310 385" fill="none" stroke="#a5755e" stroke-width="1.2" stroke-linecap="round"/>
<path d="M368 381L375 392M364 384L370 395" stroke="#c5a36a" stroke-width="2.6"/>
<!-- The foreground fold crosses the figure instead of covering the whole dress. -->
<path d="M331 251C331 299 317 338 301 376C302 386 313 393 324 393C333 368 346 345 351 318C357 289 352 264 342 251Z" fill="url(#sage)"/>
<path d="M338 258C343 305 321 352 313 384" fill="none" stroke="#e1d5af" stroke-width="2"/>
<path d="M302 392C302 429 315 463 338 487C351 501 363 507 373 506C356 483 340 455 338 421L336 397Z" fill="#92a48b"/>
<path d="M307 397C311 445 340 487 365 501" fill="none" stroke="#d3c89f" stroke-width="1.5"/>
''')


def festive_portrait():
    return canvas(
        'A woman in a ruby festive outfit and rose dupatta',
        'Original decorative fashion illustration. A woman turns gently in a full ruby outfit, holding a rose dupatta over one arm. Restrained gold details and a botanical branch complement the warm background.',
        '''<!-- A softer oval opening, distinct from the emerald composition. -->
<path d="M123 586V256C123 153 185 91 282 91C402 91 465 168 465 280V608" fill="none" stroke="#ad927b" stroke-width="1" opacity=".38"/>
<ellipse cx="310" cy="701" rx="122" ry="10" fill="#694947" opacity=".08"/>
<path d="M433 676C477 638 484 587 467 543M458 648C485 646 501 629 497 613C476 616 462 630 458 648M477 610C452 601 445 581 453 569C470 576 478 592 477 610M476 570C487 555 485 539 474 532C465 544 468 558 476 570" fill="none" stroke="#ad887b" stroke-width="1.5" opacity=".6"/>
<!-- Shoes beneath the softly turning skirt. -->
<path d="M267 676L265 687C250 690 235 695 237 700C253 707 276 701 291 695L294 676M329 675L336 692C349 697 363 698 374 694C372 689 357 684 354 676Z" fill="#96764e"/>
<path d="M244 699C259 700 273 696 286 691M340 689L362 692" fill="none" stroke="#c9a970" stroke-width="1.4"/>
<!-- A wide rose dupatta moves behind the figure. -->
<path d="M285 246C258 240 236 257 217 290C190 335 178 385 169 437C162 481 150 522 129 550C151 574 180 585 207 571C227 530 239 481 250 439C263 395 287 353 307 313Z" fill="url(#silk)" opacity=".88"/>
<path d="M267 253C222 304 199 382 188 446C180 492 168 540 152 565M259 256C214 306 192 381 181 445C173 491 160 538 145 559" fill="none" stroke="#d7ba88" stroke-width="1.5"/>
<path d="M144 549C162 565 181 570 204 561" fill="none" stroke="#b69566" stroke-width="2"/>
<!-- A lifted chin and low swept hair keep the gesture open. -->
<path d="M268 175C260 151 271 124 296 119C326 112 347 136 345 159C344 180 337 196 321 211L284 210Z" fill="#342b2c"/>
<path d="M266 178C247 167 238 183 245 198C250 212 266 215 277 207Z" fill="#3d3031"/>
<path d="M286 209C289 228 284 238 270 249L294 268L324 249C307 244 306 228 310 211Z" fill="#ba8168"/>
<path d="M280 154C291 139 316 139 328 155C336 165 335 181 340 188C345 192 344 196 337 198C335 214 324 226 311 226C297 225 283 211 278 195C274 181 275 165 280 154Z" fill="#d4a080"/>
<path d="M277 179C285 170 291 156 295 145C308 153 322 156 332 170C335 150 321 136 300 138C283 138 274 156 277 179Z" fill="#342b2c"/>
<path d="M317 178C322 176 327 177 330 180M319 183C323 186 327 185 329 182M331 199L336 198M315 211C320 213 326 212 329 209" fill="none" stroke="#795548" stroke-width="1.4" stroke-linecap="round"/>
<path d="M282 190C273 186 272 193 279 199" fill="none" stroke="#ad795f" stroke-width="1.4"/>
<circle cx="280" cy="200" r="3" fill="#c6a064"/><path d="M280 204L273 219C276 225 285 225 289 217L283 204Z" fill="#bd9758"/><path d="M277 216L281 220L285 215" fill="none" stroke="#e1c38d" stroke-width="1.2"/>
<!-- The fitted upper body opens into a broad, gently swinging hem. -->
<path d="M272 245C250 247 231 261 226 281C222 309 235 341 246 364C252 380 253 393 250 410C239 463 223 504 204 548C182 597 174 638 170 663C217 692 275 699 326 693C368 690 408 679 436 661C403 611 386 563 365 515C346 470 329 432 327 400C324 382 327 363 332 344L354 381C367 382 379 374 385 361C371 334 358 305 349 280C344 261 330 250 317 245C304 260 290 260 272 245Z" fill="url(#ruby)"/>
<path d="M250 396C276 405 303 407 327 396" fill="none" stroke="#c5a06b" stroke-width="2"/>
<path d="M255 407C244 476 213 553 198 643M276 414C265 498 249 578 251 675M302 414C307 495 321 595 340 677M325 416C341 492 379 586 409 651" fill="none" stroke="#61303d" stroke-width="3" opacity=".43"/>
<path d="M264 438C253 512 230 588 227 655M291 442C284 518 287 594 293 674M335 469C349 526 371 580 388 636" fill="none" stroke="#c17a7b" stroke-width="1.8" opacity=".4"/>
<path d="M174 652C241 687 348 692 428 654M173 659C238 693 349 698 432 661" fill="none" stroke="#c2a06c" stroke-width="1.6"/>
<use href="#sprig" transform="translate(205 650) rotate(-15)"/><use href="#sprig" transform="translate(253 666) rotate(-5)"/><use href="#sprig" transform="translate(304 669)"/><use href="#sprig" transform="translate(356 662) rotate(9)"/><use href="#sprig" transform="translate(401 646) rotate(18)"/>
<path d="M273 246C277 269 286 284 298 292C310 281 316 265 317 246M279 250C284 269 290 278 299 285C307 276 312 263 312 250" fill="none" stroke="#d0aa71" stroke-width="1.5"/>
<path d="M297 292L298 320" fill="none" stroke="#c7a26c" stroke-width="1.3"/><circle cx="298" cy="307" r="2" fill="#d6b886"/>
<!-- A curved bent sleeve and one raised hand holding the dupatta. -->
<path d="M247 275C237 297 246 326 263 348L286 330C274 312 266 292 264 274Z" fill="#8c4654"/>
<path d="M258 339C266 336 275 330 280 326" fill="none" stroke="#d0aa71" stroke-width="2"/>
<!-- The other hand supports the loose cloth at the hip. -->
<path d="M357 378C354 390 348 400 339 407L329 412C326 417 331 420 337 416C334 422 338 425 343 421C354 414 365 405 374 390L377 379Z" fill="#c79577"/>
<path d="M343 409L352 399" fill="none" stroke="#aa765f" stroke-width="1.3" stroke-linecap="round"/>
<!-- A rose fold passes over the near shoulder and across the resting arm. -->
<path d="M277 245C267 260 269 283 281 309C296 342 319 371 340 394C346 420 357 457 380 481C401 503 424 508 447 504C426 482 412 458 407 432C400 410 389 391 373 378C337 349 316 316 301 284C290 263 290 251 291 244Z" fill="url(#silk)"/>
<path d="M281 250C280 283 310 337 347 383C357 412 371 456 391 477C406 492 421 498 439 499M275 255C276 289 309 347 341 387C351 419 366 461 387 483" fill="none" stroke="#dec191" stroke-width="1.5"/>
<path d="M373 389C384 406 387 427 400 447M354 409C367 438 374 451 385 461" fill="none" stroke="#a16b68" stroke-width="1.6" opacity=".52"/>
<!-- Her near hand rests in front of the fabric, with a continuous forearm. -->
<path d="M264 347C281 351 298 341 309 323L315 313C320 312 330 308 330 305C329 302 322 307 318 306C321 301 325 296 324 293C320 292 314 302 310 305L307 312C300 321 290 331 280 332L276 330Z" fill="#d19c7c"/>
<path d="M311 310L317 310M308 316L314 318" fill="none" stroke="#ae7b64" stroke-width="1.2" stroke-linecap="round"/>
<path d="M284 332L291 344M288 329L296 340" stroke="#d0aa71" stroke-width="2.5"/>
''', rose=True)


def botanical_border():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 48" role="img" aria-labelledby="title">
<title id="title">A fine antique-gold botanical vine</title>
<g fill="none" stroke="#b69a62" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
 <path d="M0 27C28 27 37 15 60 21S99 34 120 27S153 15 180 21S215 31 240 27"/>
 <path d="M26 23C21 18 19 11 22 8C30 10 33 17 26 23M43 20C46 26 52 30 56 27C57 22 50 19 43 20M78 26C77 17 81 12 85 12C89 19 86 25 78 26M99 29C104 33 111 34 115 31C113 25 106 25 99 29M144 22C140 16 141 10 144 8C151 11 152 17 144 22M162 19C164 25 170 29 175 26C176 20 169 17 162 19M198 26C197 19 201 13 205 13C210 19 205 25 198 26M220 29C225 34 231 34 235 30C232 25 226 25 220 29"/>
</g>
</svg>
'''


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, artwork in {
        'heritage-woman.svg': heritage_portrait(),
        'festive-woman.svg': festive_portrait(),
        'botanical-border.svg': botanical_border(),
    }.items():
        (OUT / filename).write_text(artwork, encoding='utf-8')
    print('Created two distinct decorative fashion portraits and a botanical border.')
