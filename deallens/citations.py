"""Request-local source passages: model selects IDs; code supplies exact evidence.

This guarantees only quote provenance, not entailment or legal completeness.
"""
import copy
import hashlib
import json

PROTOCOL = 'source-passage-ids-v1'
VALUE_PROTOCOL = 'typed-values-v1'

VALUE_SCHEMA = {'anyOf': [
    {'type': ['string', 'number', 'boolean', 'null']},
    {'type': 'object', 'additionalProperties': False,
     'properties': {'summary': {'type':'string'}, 'details': {'type':'array', 'items': {
         'type':'object', 'additionalProperties':False,
         'properties': {'label':{'type':'string'}, 'value':{'type':'string'}},
         'required':['label','value']}}},
     'required':['summary','details']}
]}

def typed_value(value):
    if value is None or type(value) in {str,int,float,bool}:
        return json.dumps(value,ensure_ascii=False,allow_nan=False)
    if not isinstance(value,dict) or set(value)!={'summary','details'} or not isinstance(value['summary'],str) or not isinstance(value['details'],list):
        raise ValueError('Invalid typed proposal value')
    for detail in value['details']:
        if not isinstance(detail,dict) or set(detail)!={'label','value'} or any(not isinstance(detail[k],str) for k in ('label','value')):
            raise ValueError('Invalid typed proposal value')
    return json.dumps(value,ensure_ascii=False,allow_nan=False)


def passage_catalog(chunks, max_chars=800):
    passages=[]
    for chunk in chunks:
        text=chunk['text'];start=0
        while start < len(text):
            end=min(start+max_chars,len(text))
            if end<len(text):
                boundary=text.rfind(' ',start+max_chars//2,end)
                if boundary>start:end=boundary
                if len(text)-end<20:end=len(text)
            quote=text[start:end]
            if len(quote)>=20 and text.count(quote)==1:
                passages.append({'citation_id':f'p{len(passages)}','chunk_id':chunk['chunk_id'],
                                 'page':chunk.get('page'),'start':start,'end':end,'text':quote})
            start=end
    return passages


def source_id_request(request, schema):
    passages=passage_catalog(request.get('chunks',[]))
    payload={k:v for k,v in request.items() if k not in {'system','tools','model','chunks'}}
    payload['passages']=passages
    payload['citation_protocol']=PROTOCOL
    schema=copy.deepcopy(schema)
    item=schema['properties']['proposals']['items']
    item['properties'].pop('normalized_value_json')
    item['properties']['normalized_value']=copy.deepcopy(VALUE_SCHEMA)
    item['required']=['normalized_value' if k=='normalized_value_json' else k for k in item['required']]
    payload['value_protocol']=VALUE_PROTOCOL
    id_type={'type':'string'}
    if passages:id_type['enum']=[p['citation_id'] for p in passages]
    schema['properties']['proposals']['items']['properties']['citations']['items']={
        'type':'object','additionalProperties':False,
        'properties':{'citation_id':id_type},'required':['citation_id']}
    digest=hashlib.sha256(json.dumps(passages,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return payload,schema,passages,digest


def resolve_citations(result,passages):
    if not isinstance(result,dict) or not isinstance(result.get('proposals'),list):
        raise ValueError('Invalid proposal envelope')
    resolved=copy.deepcopy(result);by_id={p['citation_id']:p for p in passages}
    for proposal in resolved['proposals']:
        if not isinstance(proposal,dict) or not isinstance(proposal.get('citations'),list):
            raise ValueError('Invalid citation object')
        if 'normalized_value' not in proposal or 'normalized_value_json' in proposal:
            raise ValueError('Invalid typed proposal value')
        proposal['normalized_value_json']=typed_value(proposal.pop('normalized_value'))
        citations=[]
        for citation in proposal['citations']:
            if not isinstance(citation,dict) or set(citation)!={'citation_id'} or not isinstance(citation['citation_id'],str):
                raise ValueError('Invalid citation passage selection')
            p=by_id.get(citation['citation_id'])
            if p is None:raise ValueError('Unknown citation passage ID')
            citations.append({'chunk_id':p['chunk_id'],'evidence':p['text']})
        proposal['citations']=citations
    return resolved
