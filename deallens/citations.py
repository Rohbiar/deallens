"""Request-local source passages: model selects IDs; code supplies exact evidence.

This guarantees only quote provenance, not entailment or legal completeness.
"""
import copy
import hashlib
import json

PROTOCOL = 'source-passage-ids-v1'


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
        citations=[]
        for citation in proposal['citations']:
            if not isinstance(citation,dict) or set(citation)!={'citation_id'} or not isinstance(citation['citation_id'],str):
                raise ValueError('Invalid citation passage selection')
            p=by_id.get(citation['citation_id'])
            if p is None:raise ValueError('Unknown citation passage ID')
            citations.append({'chunk_id':p['chunk_id'],'evidence':p['text']})
        proposal['citations']=citations
    return resolved
