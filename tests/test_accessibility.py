"""Concrete palette checks; not a claim of complete WCAG conformance."""
import unittest

def luminance(hexcolor):
    rgb=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
    rgb=[x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4 for x in rgb]
    return sum(a*b for a,b in zip(rgb,(.2126,.7152,.0722)))

def contrast(a,b):
    bright,dark=sorted((luminance(a),luminance(b)),reverse=True)
    return (bright+.05)/(dark+.05)

# Match the named tokens and key component colours in business.css/heritage.css.
TEXT_PAIRS={'body':('#faf1df','#191713'), 'muted':('#c1b6a2','#24211b'),
 'gold action':('#121008','#d4af37'), 'hero copy':('#6d5b47','#f2e7d2'),
 'hero heading':('#352b20','#f2e7d2'), 'hero eyebrow':('#775833','#f2e7d2'),
 'paper action':('#f3e7cc','#25291f'), 'story copy':('#695543','#eee2cf'),
 'error':('#ffc1b3','#262213'), 'contact button':('#25221a','#e8d6a8'),
 'product category':('#d2b779','#191713'), 'status':('#f6df9b','#322c1e')}

class AccessibilityTests(unittest.TestCase):
    def test_text_palette_exceeds_aa_normal_text(self):
        for label,pair in TEXT_PAIRS.items():
            with self.subTest(label=label): self.assertGreaterEqual(contrast(*pair),4.5)
    def test_controls_and_focus_are_distinguishable(self):
        for pair in [('#9b896d','#26221b'),('#f4d978','#191713'),('#493919','#f2e7d2')]:
            self.assertGreaterEqual(contrast(*pair),3)

if __name__=='__main__':
    for label,pair in TEXT_PAIRS.items(): print(f'{label}: {contrast(*pair):.2f}:1')
    unittest.main()
