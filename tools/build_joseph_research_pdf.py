"""Build the illustrated research edition from the current assembled study HTML.

The HTML remains canonical. No historical text or image pixels are generated.
Use Python with reportlab, BeautifulSoup, Pillow, pypdf and pypdfium2 available.
"""
from pathlib import Path
import argparse, hashlib, html, json, random, re, shutil, os
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString, Tag
from PIL import Image as PILImage
from reportlab import rl_config
rl_config.useA85 = 0  # Binary lossless streams avoid ASCII85 overhead; pixels stay unchanged.
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, PageBreak, Table, TableStyle, KeepTogether, Flowable, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'joseph-smith-portrait-research.html'
OUTPUT = ROOT / 'assets/research/focuschrist-joseph-evidence.pdf'
ORIGIN = 'https://focuschrist.com/joseph-smith-portrait-research.html'
PAPER = HexColor('#142a35'); INK = HexColor('#f0e8d9')
TEAL = HexColor('#f3cf83')
GOLD = HexColor('#f3cf83'); MUTED = HexColor('#d2d2bb'); RULE = HexColor('#8a8565')
WIDTH, HEIGHT = 612, 792
LEFT, RIGHT, TOP, BOTTOM = 49, 49, 92, 63
CONTENT_WIDTH = WIDTH-LEFT-RIGHT
RECEIPT = {'sections': [], 'features': [], 'figures': [], 'text_blocks': [], 'links': []}
IDS = set()
HEADER_NAV = [('Cover','pdf-cover'),('Contents','pdf-contents'),('Evidence','portrait-section-4'),('Facial Features','portrait-section-6'),('Creation','portrait-section-11'),('Sources','portrait-section-13')]

def fonts():
    candidates = [Path(os.environ['JOSEPH_PDF_FONT_DIR'])] if os.environ.get('JOSEPH_PDF_FONT_DIR') else [Path('C:/Windows/Fonts'), Path('/usr/share/fonts/truetype/msttcorefonts'), Path('/usr/share/fonts/truetype/liberation2'), Path('/usr/share/fonts/truetype/dejavu')]
    families = [('georgia.ttf','georgiab.ttf','georgiai.ttf','georgiaz.ttf'), ('LiberationSerif-Regular.ttf','LiberationSerif-Bold.ttf','LiberationSerif-Italic.ttf','LiberationSerif-BoldItalic.ttf'), ('DejaVuSerif.ttf','DejaVuSerif-Bold.ttf','DejaVuSerif-Italic.ttf','DejaVuSerif-BoldItalic.ttf')]
    found = next(((base,files) for base in candidates for files in families if all((base/f).exists() for f in files)), None)
    if not found:raise FileNotFoundError('Set --font-dir to a directory containing Georgia, Liberation Serif, or DejaVu Serif regular/bold/italic/bold-italic TTF files')
    base,files=found
    RECEIPT['fonts']=[{'file':f,'sha256':hashlib.sha256((base/f).read_bytes()).hexdigest()} for f in files]
    for name, filename in zip(('Text','TextBold','TextItalic','TextBI'),files):
        pdfmetrics.registerFont(TTFont(name, str(base/filename)))
    pdfmetrics.registerFontFamily('Text', normal='Text', bold='TextBold', italic='TextItalic', boldItalic='TextBI')
    body_bases=[base,Path('C:/Windows/Fonts'),Path('/usr/share/fonts/truetype/liberation2'),Path('/usr/share/fonts/truetype/dejavu')]
    body_families=[('segoeui.ttf','segoeuib.ttf','segoeuii.ttf','segoeuiz.ttf'),('LiberationSans-Regular.ttf','LiberationSans-Bold.ttf','LiberationSans-Italic.ttf','LiberationSans-BoldItalic.ttf'),('DejaVuSans.ttf','DejaVuSans-Bold.ttf','DejaVuSans-Oblique.ttf','DejaVuSans-BoldOblique.ttf')]
    body_base,body_files=next((b,fs) for b in body_bases for fs in body_families if all((b/f).exists() for f in fs))
    for name,filename in zip(('Body','BodyBold','BodyItalic','BodyBI'),body_files):pdfmetrics.registerFont(TTFont(name,str(body_base/filename)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBI')
    RECEIPT['body_fonts']=[{'file':f,'sha256':hashlib.sha256((body_base/f).read_bytes()).hexdigest()} for f in body_files]
    symbol_candidates=[base/'seguisym.ttf',base/'DejaVuSans.ttf',Path('C:/Windows/Fonts/seguisym.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    symbol=next((x for x in symbol_candidates if x.exists()),None)
    if symbol is None:raise FileNotFoundError('Source arrow cues need Segoe UI Symbol or DejaVu Sans TTF alongside the chosen font directory')
    pdfmetrics.registerFont(TTFont('LinkMark',str(symbol)))
    RECEIPT['link_marker_font']={'file':symbol.name,'sha256':hashlib.sha256(symbol.read_bytes()).hexdigest()}

def style(name, **kw):
    defaults=dict(fontName='Body', fontSize=10.2, leading=15.3, textColor=INK,
                  spaceAfter=9, allowWidows=0, allowOrphans=0)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

STYLES = {
    'body':style('body'), 'small':style('small',fontSize=8.1,leading=11.4,spaceAfter=6,textColor=MUTED),
    'source':style('source',fontSize=8.8,leading=12.8,spaceAfter=9),
    'h1':style('h1',fontName='TextBold',textColor=GOLD,fontSize=33,leading=38,spaceAfter=21),
    'h2':style('h2',fontName='TextBold',textColor=GOLD,fontSize=23,leading=28,spaceAfter=17,keepWithNext=True),
    'h3':style('h3',fontName='TextBold',textColor=GOLD,fontSize=15,leading=20,spaceBefore=13,spaceAfter=10,keepWithNext=True),
    'h4':style('h4',fontName='BodyBold',fontSize=10.6,leading=14.1,spaceAfter=6,keepWithNext=True),
    'label':style('label',fontName='BodyBold',fontSize=7.5,leading=10.5,textColor=GOLD,spaceAfter=7,tracking=1),
    'caption':style('caption',fontSize=8.2,leading=11.6,textColor=MUTED,spaceAfter=7),
    'cell':style('cell',fontSize=8.3,leading=11.6,spaceAfter=4),
}

def clean(t):
    return t.replace('\u2011','-').replace('\u2013','-').replace('\u2014',' - ').replace('\u00a0',' ')

def link_target(value):
    if value.startswith('#') and value[1:] in IDS:
        return value
    return urljoin(ORIGIN,value)

def rich(node):
    if isinstance(node,NavigableString):return html.escape(clean(str(node)))
    if not isinstance(node,Tag):return ''
    if node.name in ('script','style','button','img','svg'):return ''
    if node.has_attr('hidden') or node.get('aria-hidden')=='true':return ''
    inner=('<br/>'.join(rich(c) for c in node.children if isinstance(c,Tag)) if 'fc-study-visual-sources' in node.get('class',[]) else ''.join(rich(c) for c in node.children))
    if node.name=='br':return '<br/>'
    if node.name in ('strong','b'):return '<b>'+inner+'</b>'
    if node.name in ('em','i'):return '<i>'+inner+'</i>'
    if node.name=='a' and node.get('href'):
        target=link_target(node['href']);RECEIPT['links'].append(target)
        marker=' <font name="LinkMark" size="7">↗</font>' if not target.startswith('#') else ''
        return '<link href="'+html.escape(target,quote=True)+'" color="#f3cf83">'+inner+marker+'</link>'
    return inner

def para(node, kind='body', prefix=''):
    text=rich(node) if isinstance(node,Tag) else html.escape(clean(str(node)))
    if not text.strip():return None
    if isinstance(node,Tag):
        for item in [node,*node.find_all(attrs={'id':True})]:
            if item.get('id') in IDS:text='<a name="'+item['id']+'"/>'+text
    p=Paragraph(prefix+text,STYLES[kind])
    RECEIPT['text_blocks'].append(clean(node.get_text(' ',strip=True) if isinstance(node,Tag) else str(node)))
    return p

class Heading(Paragraph):
    def __init__(self,text,key,level=0):
        self.key=key;self.level=level;self.title=clean(text)
        super().__init__(html.escape(self.title),STYLES['h2' if level==0 else 'h3'])

class SourceImage(Flowable):
    """Proportional original image or faithful clipped detail, without pixel edits."""
    def __init__(self,path,maxw,maxh,crop=None,target=None):
        Flowable.__init__(self);self.path=path;self.target=target
        iw,ih=PILImage.open(path).size;self.iw=iw;self.ih=ih
        self.crop=crop or (0,0,iw,ih)
        x,y,w,h=self.crop;scale=min(maxw/w,maxh/h,1.0)
        self.width=w*scale;self.height=h*scale;self.scale=scale;self.hAlign='CENTER'
    def draw(self):
        c=self.canv;x,y,w,h=self.crop;s=self.scale;c.saveState()
        p=c.beginPath();p.rect(0,0,self.width,self.height);c.clipPath(p,stroke=0)
        c.drawImage(ImageReader(str(self.path)),-x*s,-(self.ih-y-h)*s,
                    width=self.iw*s,height=self.ih*s,mask='auto')
        c.restoreState();c.setStrokeColor(RULE);c.setLineWidth(.4);c.rect(0,0,self.width,self.height,fill=0,stroke=1)
        if self.target:c.linkURL(self.target,(0,0,self.width,self.height),relative=1,thickness=0)

def figure_parts(figure,width,maxheight):
    img=figure.find('img');a=img.find_parent('a');src=img.get('data-source-original') or (a.get('href') if a else img['src'])
    path=ROOT/src.lstrip('/');iw,ih=PILImage.open(path).size
    crop=None
    if a and 'research-detail-window' in a.get('class',[]):
        st=img.get('style','');ratio=re.search(r'aspect-ratio:([\d.]+)/([\d.]+)',a.get('style',''))
        if ratio:
            w,h=map(float,ratio.groups());left=re.search(r'left:([-\d.]+)%',st);top=re.search(r'top:([-\d.]+)%',st)
            x=-float(left[1])*w/100 if left else 0;y=-float(top[1])*h/100 if top else 0
            crop=(max(0,x),max(0,y),w,h)
    cap=figure.find('figcaption');title=cap.find(['h2','h3','h4']).get_text(' ',strip=True)
    RECEIPT['figures'].append({'title':title,'src':src,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'crop':crop,'original_id':figure.get('data-research-art'),'caption':cap.get_text(' ',strip=True)})
    parts=[SourceImage(path,width,maxheight,crop,urljoin(ORIGIN,src)),Spacer(1,9)]
    for n in cap.find_all(recursive=False):
        if not isinstance(n,Tag):continue
        kind='h4' if n.name in ('h2','h3','h4') else 'label' if 'fc-study-visual-label' in n.get('class',[]) else 'caption'
        p=para(n,kind)
        if p:parts.append(p)
    return parts

def figure_group(figures):
    # Pair comparison details; use generous single-column plates for originals/scans.
    result=[];i=0
    while i<len(figures):
        f=figures[i];original=f.get('data-research-art');nxt=figures[i+1] if i+1<len(figures) else None
        pair=nxt is not None and not original and not nxt.get('data-research-art')
        if pair:
            w=(CONTENT_WIDTH-20)/2
            cells=[figure_parts(x,w,235) for x in (f,nxt)]
            table=Table([cells],colWidths=[w+10,w+10],hAlign='CENTER')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
            result.extend([CondPageBreak(310),table,Spacer(1,14)]);i+=2
        else:
            result.extend([KeepTogether(figure_parts(f,CONTENT_WIDTH,320 if original else 270)),Spacer(1,16)]);i+=1
    return result

def walk(node):
    if not isinstance(node,Tag):return []
    if node.has_attr('hidden') or node.get('aria-hidden')=='true':return []
    classes=node.get('class',[])
    if node.name in ('script','style','button','nav'):return []
    if node.name=='figure':return figure_group([node])
    if node.name=='article' and 'research-feature-study' in classes:
        key=node['id'];RECEIPT['features'].append(node['data-research-feature'])
        title=node.find('h3').get_text(' ',strip=True)
        out=[CondPageBreak(260),para('Look closely · Follow the evidence','label'),Heading(title,key,1)]
        for child in node.find_all(recursive=False):
            if child.name=='header':continue
            out+=walk(child)
        return out
    if node.name in ('p','h3','h4','h5','blockquote','dt','dd','a'):
        p=para(node,'label' if 'fc-eyebrow' in classes else 'h4' if node.name=='dt' else node.name if node.name in ('h3','h4') else 'body')
        return [KeepTogether([p])] if p and node.name in ('p','dd','blockquote') else [p] if p else []
    if node.name=='table':
        rows=[]
        for tr in node.find_all('tr'):
            rows.append([para(c,'cell') for c in tr.find_all(['td','th'],recursive=False)])
        if not rows:return []
        cols=max(map(len,rows));table=Table(rows,colWidths=[CONTENT_WIDTH/cols]*cols,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),HexColor('#365c4d')),('LINEBELOW',(0,0),(-1,0),.7,GOLD),('LINEBELOW',(0,1),(-1,-1),.25,RULE),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
        return [table,Spacer(1,15)]
    if node.name in ('ul','ol'):
        out=[]
        for i,li in enumerate(node.find_all('li',recursive=False),1):
            p=para(li,'body',prefix=(str(i)+'. ' if node.name=='ol' else '&#8226; '))
            if p:out.append(p)
        return out
    direct=node.find_all(recursive=False)
    if direct and all(isinstance(x,Tag) and x.name=='figure' for x in direct):return figure_group(direct)
    if node.name=='summary':return []
    out=[]
    for child in direct:out+=walk(child)
    return out

def bind_subhead_paragraphs(story):
    """Keep a short subheading with its first complete paragraph.

    Ordinary paragraphs are deliberately unsplit so repeating navigation does
    not interrupt their text or meaning. Explicitly bind heading + paragraph
    instead of relying on keepWithNext across a KeepTogether boundary.
    """
    result=[];i=0
    while i<len(story):
        current=story[i]
        if isinstance(current,Paragraph) and not isinstance(current,Heading) and current.style.name in ('h3','h4') and i+1<len(story):
            following=story[i+1]
            if isinstance(following,KeepTogether) and len(following._content)==1 and isinstance(following._content[0],Paragraph):
                current.keepWithNext=0
                result.append(KeepTogether([current,*following._content]));i+=2;continue
            if isinstance(following,Paragraph):
                current.keepWithNext=0
                result.append(KeepTogether([current,following]));i+=2;continue
        result.append(current);i+=1
    return result

class Edition(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=(WIDTH,HEIGHT),leftMargin=LEFT,rightMargin=RIGHT,topMargin=TOP,bottomMargin=BOTTOM,
            title='The Evidence Behind Our Joseph',author='focusChrist',subject='Historical evidence, artistic interpretation, and the adopted Joseph Smith portrait',pageCompression=1)
        self.addPageTemplates(PageTemplate(id='parchment',frames=[Frame(LEFT,BOTTOM,CONTENT_WIDTH,HEIGHT-TOP-BOTTOM,id='text',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.page_art))
        self.current_heading='An illustrated research edition';self.section_pages={}
    def page_art(self,c,doc):
        c.saveState();c.setFillColor(PAPER);c.rect(0,0,WIDTH,HEIGHT,fill=1,stroke=0)
        c.setFillColor(HexColor('#24483f'));c.roundRect(32,43,WIDTH-64,HEIGHT-115,12,fill=1,stroke=0)
        if doc.page==1:c.bookmarkPage('pdf-cover',fit='XYZ',left=0,top=HEIGHT,zoom=0)
        c.setStrokeColor(RULE);c.setLineWidth(.5);c.line(LEFT,HEIGHT-59,WIDTH-RIGHT,HEIGHT-59);c.line(LEFT,36,WIDTH-RIGHT,36)
        c.setFont('Text',7.5);c.setFillColor(MUTED);c.drawString(LEFT,HEIGHT-27,'FOCUSCHRIST  /  JOSEPH SMITH PORTRAIT RESEARCH')
        gap=5;button_width=(CONTENT_WIDTH-gap*5)/6;y=HEIGHT-53
        for index,(label,target) in enumerate(HEADER_NAV):
            x=LEFT+index*(button_width+gap)
            c.setStrokeColor(HexColor('#b6a16b'));c.setLineWidth(.45);c.roundRect(x,y,button_width,17,8.5,stroke=1,fill=0)
            c.setFillColor(TEAL);c.setFont('TextBold',7.0);c.drawCentredString(x+button_width/2,y+5.2,label)
            c.linkRect('',target,(x,y,x+button_width,y+17),relative=0,thickness=0)
        c.setFont('Text',7.5);c.setFillColor(MUTED)
        c.drawString(LEFT,22,'Illustrated research edition  •  3 October 2026')
        c.drawRightString(WIDTH-RIGHT,22,str(doc.page))
        if doc.page>1:
            c.setFont('TextBold',7.5);c.setFillColor(TEAL);c.drawCentredString(WIDTH/2,22,'CONTENTS');c.linkRect('', 'pdf-contents',(WIDTH/2-28,17,WIDTH/2+28,31),relative=0,thickness=0)
        c.restoreState()
    def afterFlowable(self,flow):
        if isinstance(flow,Heading):
            self.canv.bookmarkPage(flow.key,fit='XYZ',left=0,top=HEIGHT,zoom=0);self.canv.addOutlineEntry(flow.title,flow.key,level=flow.level,closed=False)
            if flow.key != 'pdf-contents':self.notify('TOCEntry',(flow.level,flow.title,self.page,flow.key))
            self.section_pages[flow.key]=self.page

def build(output):
    fonts();soup=BeautifulSoup(SOURCE.read_text(encoding='utf8'),'html.parser');root=soup.select_one('.joseph-research')
    sections=root.select('section.research-part')
    assert len(sections)==15
    global IDS
    IDS={n['id'] for n in root.select('[id]') if n['id'].startswith(('portrait-source-','portrait-section-','research-feature-'))}
    # Every actual section/feature gets its named destination, and source headings
    # are emitted inline. Link-only web controls are mapped to the owning webpage.
    IDS={x for x in IDS if not x.endswith('-title')}
    story=[Spacer(1,45),para('A FOCUSCHRIST RESEARCH EDITION','label'),Paragraph('The Evidence<br/>Behind Our Joseph',STYLES['h1']),
           para('History, interpretation, and the face we chose to remember','h3'),Spacer(1,15)]
    hero=ROOT/'assets/identities/joseph-smith-owner-approved-20260914.png'
    story+=[SourceImage(hero,340,315,target=urljoin(ORIGIN,'assets/identities/joseph-smith-owner-approved-20260914.png')),Spacer(1,14),
            para('The adopted focusChrist portrait is a modern artistic interpretation. This edition distinguishes the historical record, the choices visible in our artwork, and what remains uncertain.','body'),
            para('Independent faith-based study. Not an official publication of The Church of Jesus Christ of Latter-day Saints.','small'),PageBreak(),Heading('Contents','pdf-contents')]
    toc=TableOfContents();toc.levelStyles=[style('toc0',fontSize=10.1,leading=15,spaceBefore=7,leftIndent=0,textColor=TEAL),style('toc1',fontSize=8.8,leading=12.6,leftIndent=16,spaceBefore=3,textColor=TEAL)]
    story += [para('Use the six outlined buttons repeated at the top of every page to return to the cover, contents, evidence, facial features, creation, or sources. Source links appear in gold; a small outward arrow marks links that open online records. Contents titles and page numbers move within this PDF; source numbers lead to the source shelf. Select an image to open its complete source file.','small'),toc]
    for section in sections:
        key=section['id'];title=section.find('h2').get_text(' ',strip=True)
        RECEIPT['sections'].append({'id':key,'title':title});story += [CondPageBreak(400 if key in {'portrait-section-6','portrait-section-7','portrait-section-8','portrait-section-9'} else 220 if key=='portrait-section-2' else 270),Spacer(1,18),para('HISTORICAL EVIDENCE  /  '+key.rsplit('-',1)[-1].zfill(2),'label'),Heading(title,key)]
        for child in section.find_all(recursive=False):
            if child.name=='h2':continue
            if key=='portrait-section-2':
                # The source's web navigation table is retained, but adapted to
                # actual named PDF destinations rather than obsolete page numbers.
                pass
            story+=walk(child)
    closing_start=len(story)
    onward=root.select_one('.research-study-onward')
    if onward:
        story += [CondPageBreak(300),Spacer(1,18),Heading('Keep studying with care','pdf-continue')]
        for child in onward.find_all(recursive=False):
            if child.name in ('h2','nav'):continue
            story+=walk(child)
    story += [Spacer(1,20),para('About this edition','h3')]
    for disclosure in soup.select('footer [data-focuschrist-independence],footer [data-focuschrist-artwork-disclosure]'):
        p=para(disclosure,'small')
        if p:story.append(p)
    story[closing_start:]=[KeepTogether(story[closing_start:])]
    assert len(RECEIPT['features'])==16
    assert len(RECEIPT['figures'])==75
    assert len({x['original_id'] for x in RECEIPT['figures'] if x['original_id']})==10
    doc=Edition(output);doc.multiBuild(bind_subhead_paragraphs(story))
    RECEIPT['source_html_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    RECEIPT['pdf_sha256']=hashlib.sha256(output.read_bytes()).hexdigest();RECEIPT['section_pages']=doc.section_pages
    RECEIPT['repeating_header_navigation']=[{'label':label,'destination':key,'page':1 if key=='pdf-cover' else doc.section_pages[key]} for label,key in HEADER_NAV]
    RECEIPT['link_cues']={'color':'#f3cf83','external_marker':'↗','underlines':False,'header_buttons_each_page':6,'body_top_points':TOP,'header_button_bottom_from_top':53}
    return RECEIPT

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUTPUT);parser.add_argument('--receipt',type=Path);parser.add_argument('--copy',type=Path);parser.add_argument('--font-dir',type=Path)
    args=parser.parse_args()
    if args.font_dir:os.environ['JOSEPH_PDF_FONT_DIR']=str(args.font_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True);receipt=build(args.output)
    if args.receipt:args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if args.copy:args.copy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(args.output,args.copy)
    print(json.dumps({'output':str(args.output),'sections':len(receipt['sections']),'features':len(receipt['features']),'figures':len(receipt['figures']),'sha256':receipt['pdf_sha256']}))
