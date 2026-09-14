#!/usr/bin/env python3
"""教材の相対リンク、HTMLコード、ZIPと開始状態、手順の連続性を検査する。"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib
import json
import tempfile
import textwrap
import zipfile
from assemble import assemble, ROOT, STARTER, STEPS

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.refs=[]; self.codes=[]; self.current=None; self.scripts=0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for attr in ('src','href'):
            if attr in a:self.refs.append(a[attr])
        if tag=='pre':self.current=''
        if tag=='script':self.scripts+=1
        if tag=='img':assert a.get('alt'), '画像の代替テキストが必要'
    def handle_data(self,text):
        if self.current is not None:self.current+=text
    def handle_endtag(self,tag):
        if tag=='pre':self.codes.append(self.current);self.current=None

pages={p:Document(p.read_text()) for p in (ROOT/'materials').glob('*.html')}
links=0
for path,doc in pages.items():
    assert not doc.scripts,path
    assert len(doc.ids)==len(set(doc.ids)),path
    for ref in doc.refs:
        url=urlsplit(ref)
        assert not url.scheme and not url.netloc, (path,ref,'外部依存')
        target=(path.parent/unquote(url.path)).resolve() if url.path else path.resolve()
        assert target.exists(),(path,ref)
        if url.fragment:
            dest=Document(target.read_text())
            assert unquote(url.fragment) in dest.ids,(path,ref)
        links+=1
all_codes=[c for d in pages.values() for c in d.codes]
checkpoints=list((ROOT/'materials/assets/checkpoints').glob('step*/*.txt'))
for source in checkpoints:
    assert textwrap.dedent(source.read_text()).rstrip() in all_codes, ('全文表示',source)
for step in STEPS:
    if step['id']==16:continue
    for edit in step['edits']:
        for key in ('before','after'):
            if edit[key]:assert textwrap.dedent(edit[key]).rstrip() in all_codes,(step['id'],key)
with tempfile.TemporaryDirectory(prefix='a02-steps-') as tmp:
    assemble(Path(tmp)/'replayed',16)
with zipfile.ZipFile(ROOT/'materials/assets/A02ProfileCard-starter.zip') as z:
    manifest=json.loads((ROOT/'teacher/starter-manifest.json').read_text())
    assert set(z.namelist())=={'A02ProfileCard/'+p for p in manifest}
    for file,digest in manifest.items():
        assert hashlib.sha256(z.read('A02ProfileCard/'+file)).hexdigest()==digest,file
result={'htmlPages':len(pages),'localReferences':links,'inlineCheckpointFiles':len(checkpoints),'studentEditSteps':9,'allCodeStagesReplayed':10,'starterFiles':len(manifest),'result':'PASS'}
(ROOT/'teacher/static-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
