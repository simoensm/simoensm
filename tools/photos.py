"""Turn photos-inbox/<category>/* into web-sized photos/<category>/* plus photos/photos.json."""
import json, os, re, sys, unicodedata
from PIL import Image, ImageOps
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX=os.path.join(ROOT,'photos-inbox'); OUT=os.path.join(ROOT,'photos')
CATS=['sports','motorsports','events','portraits','drone','realestate','macro','products']
ALIAS={'automotive':'motorsports','aerial':'drone','night':'events','realestate':'realestate','real-estate':'realestate'}
EXT=('.jpg','.jpeg','.png','.webp','.tif','.tiff','.heic')
def slug(s): return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',os.path.splitext(s)[0]).encode('ascii','ignore').decode().lower()).strip('-')
man={c:[] for c in CATS}; man['videos']=[]
old=os.path.join(OUT,'photos.json')
if os.path.exists(old):
    try: man['videos']=json.load(open(old)).get('videos',[])
    except Exception: pass
for folder in sorted(os.listdir(INBOX)) if os.path.isdir(INBOX) else []:
    src=os.path.join(INBOX,folder)
    if not os.path.isdir(src) or folder=='videos': continue
    cat=ALIAS.get(folder,folder)
    if cat not in CATS: print('skip folder',folder); continue
    os.makedirs(os.path.join(OUT,cat),exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith(EXT): continue
        name=slug(f); big=f'photos/{cat}/{name}.jpg'; th=f'photos/{cat}/{name}-t.jpg'
        try:
            im=ImageOps.exif_transpose(Image.open(os.path.join(src,f))).convert('RGB')
        except Exception as e: print('cannot open',f,e); continue
        w,h=im.size
        if not os.path.exists(os.path.join(ROOT,big)):
            b=im.copy(); b.thumbnail((2200,2200),Image.LANCZOS); b.save(os.path.join(ROOT,big),'JPEG',quality=80,optimize=True,progressive=True)
            t=im.copy(); t.thumbnail((720,720),Image.LANCZOS); t.save(os.path.join(ROOT,th),'JPEG',quality=74,optimize=True,progressive=True)
        b=Image.open(os.path.join(ROOT,big))
        man[cat].append({'src':big,'thumb':th,'w':b.width,'h':b.height,'alt':cat.capitalize()})
json.dump(man,open(old,'w'),indent=1)
print({k:len(v) for k,v in man.items()})
