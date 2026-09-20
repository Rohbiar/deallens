"""HTTP smoke checks in one process; separate from browser visual QA."""
import json
import threading
import time
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from deallens.server import serve

root=Path(__file__).resolve().parents[1]
port=8876
threading.Thread(target=serve,args=(root,port),daemon=True).start()
base=f'http://127.0.0.1:{port}'
for _ in range(40):
    try:urlopen(base+'/api/manifest',timeout=1);break
    except OSError:time.sleep(.1)
results=[]
for path in ['/','/api/manifest','/api/review-packet','/api/bio_techne','/api/organon','/api/uber_delivery_hero','/source/bio_techne']:
    with urlopen(base+path,timeout=10) as r:
        data=r.read();assert r.status==200 and data
        if path=='/api/review-packet':
            packet=json.loads(data)
            assert packet['human_review_attested'] is False and packet['decisions']==[]
            assert packet['records'] and all(x['record']['record_id'] for x in packet['records'])
        results.append({'route':path,'status':r.status,'bytes':len(data)})
for doc,question,expected in [('bio_techne','consideration','73.0'),('uber_delivery_hero','consideration','sufficient source support')]:
    with urlopen(base+'/ask/'+doc+'?q='+quote(question)) as r:
        a=json.load(r);assert expected in a['answer'];results.append({'document':doc,'question':question,'answer':a['answer']})
try:
    urlopen(base+'/source/../../config/assumptions.json')
    raise AssertionError('Unexpected file access')
except HTTPError as e:
    assert e.code==404;results.append({'path_traversal':'rejected','status':404})
report={'checks':results,'browser_visual_test':'This script tests HTTP only. See docs/BROWSER_CHECKS.json for separately recorded browser inspection.'}
(root/'docs/RUNTIME_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
