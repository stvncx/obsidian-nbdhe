"""Extra NBDHE note types: Basic (+optional reverse), Type-in, Matching, Ordering, Sorting,
Label-the-diagram. Same look as the IO/Cloze/MCQ types in build_deck.py.

Interactive types (match/order/sort/label) run plain JavaScript on the FRONT: everything is
TAP-based (tap one thing, then where it goes) because drag is unreliable on iPhone. A "Check"
button marks each item right/wrong and shows a score; the BACK shows the full answer key.
Scripts find their own container via `:not([data-init])`, so they work whether Anki reloads
the page per side (AnkiDroid) or swaps content in place (desktop, AnkiMobile).

Card data travels as JSON in a field, embedded in <script type="application/json">.

Model IDs are FIXED forever (see build_deck.py for the first three).
"""
import json, random
import genanki

BASIC_MODEL_ID = 1728390004
TYPEIN_MODEL_ID = 1728390005
MATCH_MODEL_ID = 1728390006
ORDER_MODEL_ID = 1728390007
SORT_MODEL_ID = 1728390008
LABEL_MODEL_ID = 1728390009

GRADE_HINT = ('<div class="hint">Tap <b>Check</b>, then grade: all correct → Good · '
              'one slip → Hard · more → Again</div>')

def js_data(obj):
    """JSON safe to embed in a <script> element inside an Anki field."""
    return json.dumps(obj, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e')

def make(base_css):
    """Build the note-type objects (needs the shared CSS from build_deck)."""
    TEXT_TMPL = '<div class="title">{{Section}}</div><div class="panel">%s</div>'
    TAIL = '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}<div class="source">{{Source}}</div>'

    basic = genanki.Model(
        BASIC_MODEL_ID, 'NBDHE Basic',
        fields=[{'name': n} for n in ('Front', 'Back', 'Reverse', 'Section', 'Extra', 'Source')],
        templates=[
            {'name': 'Forward',
             'qfmt': TEXT_TMPL % '{{Front}}',
             'afmt': TEXT_TMPL % '{{Front}}<hr class="sep"><div class="ans">{{Back}}</div>' + TAIL},
            {'name': 'Reverse',   # only generated when the Reverse field is non-empty
             'qfmt': '{{#Reverse}}' + TEXT_TMPL % '{{Back}}' + '{{/Reverse}}',
             'afmt': TEXT_TMPL % '{{Back}}<hr class="sep"><div class="ans">{{Front}}</div>' + TAIL}],
        css=base_css + BASIC_CSS, sort_field_index=0)

    typein = genanki.Model(
        TYPEIN_MODEL_ID, 'NBDHE Type-in',
        fields=[{'name': n} for n in ('Question', 'Answer', 'Section', 'Extra', 'Source')],
        templates=[{'name': 'Type',
                    'qfmt': TEXT_TMPL % '{{Question}}' + '<div class="typein">{{type:Answer}}</div>',
                    'afmt': TEXT_TMPL % '{{Question}}' + '<div class="typein">{{type:Answer}}</div>' + TAIL}],
        css=base_css + BASIC_CSS + TYPEIN_CSS, sort_field_index=0)

    def interactive(mid, name, kind, key_html):
        front = (f'<div class="title">{{{{Section}}}}</div><div class="panel nb-{kind}">'
                 f'<div class="prompt">{{{{Prompt}}}}</div>'
                 f'<script type="application/json" class="nb-data">{{{{Data}}}}</script>'
                 f'<div class="nb-ui"></div><button class="nb-check">Check</button><div class="nb-score"></div>'
                 f'</div>{GRADE_HINT}<script>{JS[kind]}</script>')
        back = (f'<div class="title">{{{{Section}}}}</div><div class="panel"><div class="prompt">{{{{Prompt}}}}</div>'
                f'<div class="keyhead">Answer key</div>{key_html}</div>' + TAIL)
        return genanki.Model(mid, name,
                             fields=[{'name': n} for n in ('Prompt', 'Data', 'Key', 'Section', 'Extra', 'Source')],
                             templates=[{'name': kind.capitalize(), 'qfmt': front, 'afmt': back}],
                             css=base_css + INTERACTIVE_CSS, sort_field_index=0)

    match = interactive(MATCH_MODEL_ID, 'NBDHE Matching', 'match', '{{Key}}')
    order = interactive(ORDER_MODEL_ID, 'NBDHE Ordering', 'order', '{{Key}}')
    sort = interactive(SORT_MODEL_ID, 'NBDHE Sorting', 'sort', '{{Key}}')

    label = genanki.Model(
        LABEL_MODEL_ID, 'NBDHE Label Diagram',
        fields=[{'name': n} for n in ('Title', 'Image', 'Data', 'Section', 'Extra', 'Source')],
        templates=[{'name': 'Label',
                    'qfmt': ('<div class="title">{{Title}} — label the diagram</div>'
                             '<div class="nb-label"><script type="application/json" class="nb-data">{{Data}}</script>'
                             '<div class="io lab">{{Image}}</div><div class="tray"></div>'
                             '<button class="nb-check">Check</button><div class="nb-score"></div></div>'
                             + GRADE_HINT + '<script>' + JS['label'] + '</script>'),
                    'afmt': ('<div class="title">{{Title}} — label the diagram</div>'
                             '<div class="io">{{Image}}</div>' + TAIL)}],
        css=base_css + IO_LIKE_CSS + INTERACTIVE_CSS, sort_field_index=0)
    return dict(basic=basic, typein=typein, match=match, order=order, sort=sort, label=label)

# ---------------------------------------------------------------- note builders
def _key_table(rows):
    return '<table class="keytab">' + ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in rows) + '</table>'

def basic_note(m, q, pdf):
    return genanki.Note(model=m['basic'], fields=[q['front'], q['back'], 'y' if q.get('reverse') else '',
                        q.get('section', ''), q.get('extra', ''), f"StudentRDH {pdf} p.{q['page']}"],
                        guid=genanki.guid_for('nbdhe-basic', q['id']), tags=[pdf.lower(), f"p{q['page']}", 'basic'])

def typein_note(m, q, pdf):
    return genanki.Note(model=m['typein'], fields=[q['question'], q['answer'], q.get('section', ''),
                        q.get('extra', ''), f"StudentRDH {pdf} p.{q['page']}"],
                        guid=genanki.guid_for('nbdhe-typein', q['id']), tags=[pdf.lower(), f"p{q['page']}", 'typein'])

def match_note(m, q, pdf):
    key = _key_table(q['pairs'])
    return genanki.Note(model=m['match'], fields=[q['prompt'], js_data({'pairs': q['pairs']}), key,
                        q.get('section', ''), q.get('extra', ''), f"StudentRDH {pdf} p.{q['page']}"],
                        guid=genanki.guid_for('nbdhe-match', q['id']), tags=[pdf.lower(), f"p{q['page']}", 'matching'])

def order_note(m, q, pdf):
    key = '<ol class="keylist">' + ''.join(f'<li>{x}</li>' for x in q['items']) + '</ol>'
    return genanki.Note(model=m['order'], fields=[q['prompt'], js_data({'items': q['items']}), key,
                        q.get('section', ''), q.get('extra', ''), f"StudentRDH {pdf} p.{q['page']}"],
                        guid=genanki.guid_for('nbdhe-order', q['id']), tags=[pdf.lower(), f"p{q['page']}", 'ordering'])

def sort_note(m, q, pdf):
    cats = q['categories']                     # [[category, [items...]], ...] — order kept
    key = ''.join(f'<div class="keycat"><b>{c}</b>: {", ".join(items)}</div>' for c, items in cats)
    return genanki.Note(model=m['sort'], fields=[q['prompt'], js_data({'cats': cats}), key,
                        q.get('section', ''), q.get('extra', ''), f"StudentRDH {pdf} p.{q['page']}"],
                        guid=genanki.guid_for('nbdhe-sort', q['id']), tags=[pdf.lower(), f"p{q['page']}", 'sorting'])

def label_note(m, spec, slots, pdf, book_page):
    """slots: [{l,t,w,h,rot,a}] in % of the image — the same covers as the IO cards."""
    return genanki.Note(model=m['label'], fields=[spec['title'], f'<img src="{spec["name"]}.jpg">',
                        js_data({'slots': slots}), spec.get('deck', ''), '', f"StudentRDH {pdf} p.{book_page}"],
                        guid=genanki.guid_for('nbdhe-label', spec['name']),
                        tags=[pdf.lower(), f"p{book_page}", 'label-diagram'])

# ---------------------------------------------------------------- CSS
BASIC_CSS = """
.sep { border: 0; border-top: 1px solid #e5e5ea; margin: 14px 0; }
.ans { font-weight: 600; color: #0b6bcb; }
.nightMode .ans, .night_mode .ans { color: #5eaeff; }
.nightMode .sep, .night_mode .sep { border-top-color: #48484a; }
"""
TYPEIN_CSS = """
.typein { max-width: 720px; margin: 12px auto 0; text-align: center; }
.typein input, #typeans { width: 100%; box-sizing: border-box; font-size: 20px; padding: 10px 12px;
  border-radius: 10px; border: 2px solid #c7c7cc; }
code#typeans { display: block; font-size: 18px; }
"""
IO_LIKE_CSS = """
.card { text-align: center; }
.io { container-type: inline-size; position: relative; display: inline-block; width: 100%;
  max-width: 1000px; line-height: 0; border-radius: 10px; overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 6px 20px rgba(0,0,0,.06); }
.io img { width: 100%; height: auto; display: block; max-width: none; max-height: none; }
.slot { position: absolute; display: flex; align-items: center; justify-content: center; box-sizing: border-box;
  border-radius: 4px; background: #e8781e; border: 1px solid #b85a0e; color: #fff; line-height: 1.05;
  font-size: 2.1cqw; font-weight: 700; text-align: center; padding: 0 2px; cursor: pointer; overflow: hidden; }
.slot.filled { background: #fff; color: #1d1d1f; border: 2px solid #0b6bcb; }
.slot.ok { background: #e3f6e8; border: 2px solid #1f9d55; color: #14532d; }
.slot.bad { background: #fde8e8; border: 2px solid #d64545; color: #7f1d1d; }
.slot.target { box-shadow: 0 0 0 3px rgba(11,107,203,.45); }
.tray { max-width: 1000px; margin: 12px auto 0; display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
"""
INTERACTIVE_CSS = """
.prompt { font-weight: 600; margin-bottom: 12px; }
.nb-ui { display: block; }
.chip { display: inline-block; padding: 9px 12px; margin: 4px; border-radius: 10px; background: #f0f0f3;
  border: 2px solid transparent; font-size: 17px; line-height: 1.25; cursor: pointer; user-select: none;
  -webkit-user-select: none; -webkit-tap-highlight-color: transparent; }
.chip.sel { border-color: #0b6bcb; background: #e6f0fb; }
.chip.used { opacity: .35; }
.chip.ok { background: #e3f6e8; border-color: #1f9d55; }
.chip.bad { background: #fde8e8; border-color: #d64545; }
.cols { display: flex; gap: 10px; }
.cols > div { flex: 1; display: flex; flex-direction: column; }
.cols .chip { display: block; margin: 4px 0; }
.chip .tag { display: inline-block; min-width: 1.4em; margin-right: 6px; padding: 0 4px; border-radius: 6px;
  color: #fff; font-weight: 700; font-size: 14px; text-align: center; }
.olist .chip { display: block; margin: 6px 0; }
.olist .num { display: inline-block; width: 1.6em; color: #8e8e93; font-weight: 700; }
.bins { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }
.bin { flex: 1 1 140px; min-height: 70px; border: 2px dashed #c7c7cc; border-radius: 12px; padding: 6px; }
.bin.target { border-color: #0b6bcb; background: #f3f8fe; }
.bin h4 { margin: 2px 4px 6px; font-size: 15px; color: #3a3a3c; }
.pool { margin-top: 6px; }
.nb-check { display: block; margin: 14px auto 0; padding: 10px 26px; font-size: 17px; font-weight: 700;
  border: 0; border-radius: 10px; background: #0b6bcb; color: #fff; }
.nb-score { text-align: center; margin-top: 8px; font-weight: 700; font-size: 18px; }
.hint { max-width: 720px; margin: 10px auto 0; font-size: 13px; color: #8e8e93; text-align: center; }
.keyhead { font-size: 13px; text-transform: uppercase; letter-spacing: .04em; color: #8e8e93; margin: 6px 0; }
.keytab { width: 100%; border-collapse: collapse; }
.keytab td { padding: 7px 6px; border-bottom: 1px solid #e5e5ea; vertical-align: top; }
.keytab td:first-child { font-weight: 600; width: 45%; }
.keylist li { margin: 4px 0; }
.keycat { margin: 6px 0; }
.nightMode .chip, .night_mode .chip { background: #3a3a3c; color: #f2f2f7; }
.nightMode .chip.sel, .night_mode .chip.sel { background: #1f3a5c; }
.nightMode .chip.ok, .night_mode .chip.ok { background: #1e3b2a; }
.nightMode .chip.bad, .night_mode .chip.bad { background: #4a1f1f; }
.nightMode .keytab td, .night_mode .keytab td { border-bottom-color: #48484a; }
.nightMode .bin h4, .night_mode .bin h4 { color: #d1d1d6; }
"""

# ---------------------------------------------------------------- JS (ES5, no modules)
_COMMON = r"""
function nbShuffle(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;}return a;}
function nbEl(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
var NB_COLORS=['#0b6bcb','#e8781e','#1f9d55','#8e44ad','#d64545','#0f9fb4','#b8860b','#c2185b','#5d6d7e','#2e7d32'];
"""
JS = {}
JS['match'] = _COMMON + r"""
(function(){var roots=document.querySelectorAll('.nb-match:not([data-init])');
for(var r=0;r<roots.length;r++)(function(root){root.setAttribute('data-init','1');
 var pairs=JSON.parse(root.querySelector('.nb-data').textContent).pairs;
 var ui=root.querySelector('.nb-ui'),cols=nbEl('div','cols'),L=nbEl('div'),R=nbEl('div');cols.appendChild(L);cols.appendChild(R);ui.appendChild(cols);
 var rightOrder=nbShuffle(pairs.map(function(p,i){return i;})),sel=null,map={},lbtn=[],rbtn={};
 function paint(){for(var i=0;i<pairs.length;i++){var b=lbtn[i];b.className='chip'+(sel===i?' sel':'');
   var t=b.querySelector('.tag');if(map[i]!=null){t.style.background=NB_COLORS[i%NB_COLORS.length];t.textContent=i+1;}else{t.style.background='transparent';t.textContent='';}}
  for(var k in rbtn){var rb=rbtn[k],owner=null;for(var i2 in map)if(map[i2]==k)owner=+i2;
   var tg=rb.querySelector('.tag');rb.className='chip';if(owner!=null){tg.style.background=NB_COLORS[owner%NB_COLORS.length];tg.textContent=owner+1;}else{tg.style.background='transparent';tg.textContent='';}}}
 pairs.forEach(function(p,i){var b=nbEl('div','chip','<span class="tag"></span><span class="t">'+p[0]+'</span>');b.onclick=function(){if(map[i]!=null&&sel!==i){delete map[i];sel=i;}else sel=(sel===i?null:i);paint();};L.appendChild(b);lbtn[i]=b;});
 rightOrder.forEach(function(j){var b=nbEl('div','chip','<span class="tag"></span><span class="t">'+pairs[j][1]+'</span>');b.onclick=function(){if(sel==null)return;for(var i in map)if(map[i]==j)delete map[i];map[sel]=j;sel=null;paint();};R.appendChild(b);rbtn[j]=b;});
 paint();
 root.querySelector('.nb-check').onclick=function(){var ok=0;for(var i=0;i<pairs.length;i++){var good=map[i]===i;if(good)ok++;lbtn[i].className='chip '+(good?'ok':'bad');}
  root.querySelector('.nb-score').textContent=ok+' / '+pairs.length+' correct';};
})(roots[r]);})();
"""
JS['order'] = _COMMON + r"""
(function(){var roots=document.querySelectorAll('.nb-order:not([data-init])');
for(var r=0;r<roots.length;r++)(function(root){root.setAttribute('data-init','1');
 var items=JSON.parse(root.querySelector('.nb-data').textContent).items;
 var ui=root.querySelector('.nb-ui'),list=nbEl('div','olist');ui.appendChild(nbEl('div','hint','Tap two items to swap them.'));ui.appendChild(list);
 var idx=items.map(function(x,i){return i;});do{idx=nbShuffle(idx);}while(items.length>2&&idx.every(function(v,i){return v===i;}));
 var sel=null;
 function draw(){list.innerHTML='';idx.forEach(function(v,pos){var b=nbEl('div','chip'+(sel===pos?' sel':''),'<span class="num">'+(pos+1)+'</span>'+items[v]);
   b.onclick=function(){if(sel==null){sel=pos;}else{var t=idx[sel];idx[sel]=idx[pos];idx[pos]=t;sel=null;}draw();};list.appendChild(b);});}
 draw();
 root.querySelector('.nb-check').onclick=function(){var ok=0,ch=list.children;for(var p=0;p<idx.length;p++){var good=idx[p]===p;if(good)ok++;ch[p].className='chip '+(good?'ok':'bad');}
  root.querySelector('.nb-score').textContent=ok+' / '+items.length+' in the right place';};
})(roots[r]);})();
"""
JS['sort'] = _COMMON + r"""
(function(){var roots=document.querySelectorAll('.nb-sort:not([data-init])');
for(var r=0;r<roots.length;r++)(function(root){root.setAttribute('data-init','1');
 var cats=JSON.parse(root.querySelector('.nb-data').textContent).cats,all=[];
 cats.forEach(function(c,ci){c[1].forEach(function(t){all.push({t:t,c:ci,at:-1});});});all=nbShuffle(all);
 var ui=root.querySelector('.nb-ui'),pool=nbEl('div','pool'),bins=nbEl('div','bins'),sel=null,binEls=[];
 ui.appendChild(nbEl('div','hint','Tap an item, then the group it belongs to.'));ui.appendChild(pool);ui.appendChild(bins);
 cats.forEach(function(c,ci){var b=nbEl('div','bin','<h4>'+c[0]+'</h4>');b.onclick=function(e){if(sel==null||e.target.classList.contains('chip'))return;sel.at=ci;sel=null;draw();};bins.appendChild(b);binEls.push(b);});
 function draw(){pool.innerHTML='';binEls.forEach(function(b){while(b.children.length>1)b.removeChild(b.lastChild);b.classList.toggle('target',sel!=null);});
  all.forEach(function(it){var ch=nbEl('div','chip'+(sel===it?' sel':''),it.t);ch.onclick=function(){sel=(sel===it?null:it);draw();};(it.at<0?pool:binEls[it.at]).appendChild(ch);it.el=ch;});}
 draw();
 root.querySelector('.nb-check').onclick=function(){var ok=0;all.forEach(function(it){var good=it.at===it.c;if(good)ok++;it.el.className='chip '+(good?'ok':'bad');});
  root.querySelector('.nb-score').textContent=ok+' / '+all.length+' sorted correctly';};
})(roots[r]);})();
"""
JS['label'] = _COMMON + r"""
(function(){var roots=document.querySelectorAll('.nb-label:not([data-init])');
for(var r=0;r<roots.length;r++)(function(root){root.setAttribute('data-init','1');
 var slots=JSON.parse(root.querySelector('.nb-data').textContent).slots,io=root.querySelector('.io'),tray=root.querySelector('.tray');
 var chips=nbShuffle(slots.map(function(s,i){return {t:s.a,i:i,used:false};})),sel=null,put={},slotEls=[];
 slots.forEach(function(s,i){var e=nbEl('div','slot','?');e.style.left=s.l+'%';e.style.top=s.t+'%';e.style.width=s.w+'%';e.style.height=s.h+'%';
  if(s.rot)e.style.transform='rotate('+s.rot+'deg)';
  e.onclick=function(){if(put[i]!=null){put[i].used=false;delete put[i];}else if(sel){for(var k in put)if(put[k]===sel)delete put[k];put[i]=sel;sel.used=true;sel=null;}draw();};io.appendChild(e);slotEls.push(e);});
 function draw(){tray.innerHTML='';chips.forEach(function(c){var b=nbEl('div','chip'+(c.used?' used':'')+(sel===c?' sel':''),c.t);b.onclick=function(){if(c.used)return;sel=(sel===c?null:c);draw();};tray.appendChild(b);});
  slotEls.forEach(function(e,i){e.className='slot'+(put[i]?' filled':'')+(sel&&!put[i]?' target':'');e.textContent=put[i]?put[i].t:'?';});}
 draw();
 root.querySelector('.nb-check').onclick=function(){var ok=0;slotEls.forEach(function(e,i){var good=put[i]&&put[i].t===slots[i].a;if(good)ok++;e.className='slot '+(good?'ok':'bad');if(!put[i])e.textContent=slots[i].a;});
  root.querySelector('.nb-score').textContent=ok+' / '+slots.length+' labels correct';};
})(roots[r]);})();
"""
