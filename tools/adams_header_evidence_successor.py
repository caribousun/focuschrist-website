"""Exact current evidence successor; never a release approval.

Historical evidence is validated against byte-exact archived helpers and the
verified CSS predecessor. New current evidence must be actual, independently
reviewed and explicitly pinned. This validator does not grant site release.
"""
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from adams_source_import_v9 import bound, canonical, local, require
import adams_integrated_source_import as prior
import adams_integrated_qa_evidence as qa_checks
from owner_integration_contract import validate_file

RECORD = 'docs/adams-header-evidence-successor/current-record.json'
# Actual completed provider evidence and three independently authored review
# receipts, bound to the exact reviewed spec. This does not grant site release.
APPROVED_RECORD_SHA256 = 'ee796d311d7cb5845a6c94e1bc845637ab08e01e59282bfad4ba54d719f1c110'
APPROVED_SPEC_SHA256 = '8f3e13f9de807b116ad82fcc17ccf98a9c3924413539ce7dccb76d7e9939352c'
APPROVED_PROVIDER_SHA256 = '6103d641393c6e9e0a9a1376c8fbba2b14c539a73ec7f23ab3769b2383bd1ec8'
# Actual task-specific role assignment, not a claim of identity authentication.
APPROVED_ASSIGNMENT_SHA256 = '4624118c89d927e838f1762c73b8a172d4b79f55778236ced9a16c4b382c9231'
REVIEW_ASSIGNMENTS = {'Fermi':'/root/repair_adams_hero_classification/independent_review','Newton':'/root/repair_adams_hero_classification/subsequent_qa/css_dependency_mapping/index_successor_review','Albert':'/root'}
CSS = {'path':'adams-integration.css','bytes':5292,'sha256':'3c8a2390e93e94f5d67d3b7a4356f018d78df7ea5c654a3841366549df76d131'}
OLD_CSS = {'path':'adams-integration.css','bytes':4965,'sha256':'d936516926aa47c12c634b11b15278e1590502d0491d9b1f17cd90a0210fdeb1'}
HELPER = {'path':'tools/adams_chart_browser_qa.js','bytes':32995,'sha256':'4ddd3122c6e013b03103d5e4ec0897ededbd713267a28e664b909a54020f2186'}
OWNER_CONTRACT = {'path':'tools/owner_integration_qa_contract.json','bytes':22584,'sha256':'5d7614c9cb585569788c260d8fc08545b579a245a2e2ee86dd617520e3a1ddef'}
ARCHIVES = {
 'tools/adams_chart_browser_qa.js':'docs/adams-header-evidence-successor/history/adams_chart_browser_qa.js.source',
 'tools/owner_integration_qa_contract.json':'docs/adams-header-evidence-successor/history/owner_integration_qa_contract.json.source',
}
QA_MUTABLE = frozenset({'helper','owner_contract','report','run_identity','capture_manifest','owner_report','owner_capture_manifest','producer'})


def historical_reader(root, item):
    """Only exact CSS/helper predecessor bytes; never current-render evidence."""
    name=item['path']
    if name == CSS['path']:
        require(item == OLD_CSS, 'historical CSS record drift')
        current=bound(root, CSS)
        validate_file(name,current,root)
        raw=current[:OLD_CSS['bytes']]
    elif name in ARCHIVES:
        archive=local(root,ARCHIVES[name]);raw=archive.read_bytes()
    else:
        return bound(root,item)
    require(len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'], 'historical predecessor drift: '+name)
    return raw


def validate_spec_delta(old_spec, current):
    """No change to assets, rights, old semantic contract, or other sources."""
    require(isinstance(current,dict), 'current specification missing')
    previous=copy.deepcopy(old_spec);new=copy.deepcopy(current)
    old_context=previous.pop('context');new_context=new.pop('context')
    require(isinstance(old_context,list) and isinstance(new_context,list) and len(old_context)==len(new_context)==5, 'context shape')
    old_by={x['path']:x for x in old_context};new_by={x['path']:x for x in new_context}
    require(len(old_by)==len(new_by)==5 and old_by.get(CSS['path'])==OLD_CSS and new_by.get(CSS['path'])==CSS, 'exact CSS successor context')
    del old_by[CSS['path']];del new_by[CSS['path']]
    require(old_by==new_by, 'non-CSS context changed')
    oldqa=previous.pop('qa');newqa=new.pop('qa')
    require(set(oldqa)==set(newqa), 'QA field set changed')
    require(newqa.get('helper')==HELPER and newqa.get('owner_contract')==OWNER_CONTRACT, 'current renderer/contract mismatch')
    evidence_keys=('report','run_identity','capture_manifest','owner_report','owner_capture_manifest')
    require(len({newqa[key]['path'] for key in evidence_keys})==len(evidence_keys), 'current evidence paths must be distinct')
    for key in evidence_keys:
        old_path=oldqa[key]['path'];new_path=newqa[key]['path']
        require(new_path!=old_path and new_path.startswith('docs/adams-header-evidence-successor/'), 'fresh evidence must not overwrite predecessor: '+key)
    require(newqa['producer']['run_id']!=oldqa['producer']['run_id'], 'fresh producer run required')
    for key in QA_MUTABLE:
        oldqa.pop(key);newqa.pop(key)
    require(oldqa==newqa and previous==new, 'unchanged reviewed requirements drifted')


def validate_current_reviews(root, record, spec_sha, spec, assignment):
    require(type(assignment.get('schema')) is int and assignment.get('schema')==1 and assignment.get('appointed_by')=='Albert' and assignment.get('author_id')=='/root' and assignment.get('roles')==REVIEW_ASSIGNMENTS and isinstance(assignment.get('scope'),str) and bool(assignment['scope'].strip()), 'review role assignment mismatch')
    require(len(set(REVIEW_ASSIGNMENTS.values()))==3, 'review authors must be distinct')
    rows=record.get('reviews');require(isinstance(rows,list) and len(rows)==3 and {x.get('reviewer') for x in rows}==set(REVIEW_ASSIGNMENTS), 'three independent current reviews required')
    for row in rows:
        role=row['reviewer'];author=REVIEW_ASSIGNMENTS[role]
        require(row.get('author_id')==author, 'review row author mismatch')
        own=json.loads(bound(root,row['receipt']))
        require(own.get('review_role')==role and own.get('author_id')==author and own.get('role_assignment_sha256')==APPROVED_ASSIGNMENT_SHA256 and isinstance(own.get('role_scope'),str) and bool(own['role_scope'].strip()), 'review role/actual author attribution mismatch')
        require(type(own.get('schema')) is int and own.get('schema')==1 and own.get('reviewer')==row['reviewer'] and own.get('decision')=='CONCUR' and own.get('spec_sha256')==spec_sha, 'current review mismatch')
        stamp=datetime.fromisoformat(own.get('reviewed_at',''));require(stamp.tzinfo is not None, 'review timestamp')
        require(own.get('source_rights_checked') is True and own.get('finished_pixels') is True and own.get('desktop_phone_inspected') is True, 'current review scope incomplete')
        mandate=own.get('mandate_readback')
        require(isinstance(mandate,dict) and isinstance(mandate.get('files'),list) and bool(mandate['files']) and isinstance(mandate.get('applicable_requirements'),list) and bool(mandate['applicable_requirements']), 'mandate readback incomplete')
        require(all(isinstance(x,dict) and isinstance(x.get('path'),str) and bool(x['path']) and isinstance(x.get('sha256'),str) and re.fullmatch(r'[0-9a-f]{64}',x['sha256']) is not None for x in mandate['files']), 'mandate file/revision missing')
        require(all(isinstance(x,str) and bool(x.strip()) for x in mandate['applicable_requirements']) and own.get('finished_candidate_follows_mandates') is True, 'mandate requirements or exact-candidate concurrence missing')
        require(own.get('observations') and own.get('limits') and own.get('evidence'), 'current review evidence incomplete')
        evidence_by_path={e['path']:e for e in own['evidence']}
        require(len(evidence_by_path)==len(own['evidence']), 'duplicate review evidence')
        for key in ('report','run_identity','capture_manifest','owner_report','owner_capture_manifest'):
            required=spec['qa'][key];require(evidence_by_path.get(required['path'])==required, 'current review lacks exact evidence: '+key)
        for evidence in own['evidence']:bound(root,evidence)


def validate_owner_provenance(root,spec,provider):
    """Cross-bind the owner run, checkout, capture identity and exact sources."""
    q=spec['qa'];identity=json.loads(bound(root,q['run_identity']));owner=json.loads(bound(root,q['owner_report']));capture=json.loads(bound(root,q['owner_capture_manifest']))
    producer=owner.get('producer',{})
    require(producer.get('sha')==identity.get('checkout_sha') and producer.get('run')==identity.get('run_id') and producer.get('event')=='pull_request', 'owner producer/checkout mismatch')
    require(capture.get('run_id')==identity.get('run_id'), 'owner capture run mismatch')
    for key in ('job_id','artifact_id'):
        require(isinstance(capture.get(key),str) and re.fullmatch(r'[1-9][0-9]*',capture[key]) is not None, 'owner capture identity '+key)
    require(type(capture.get('artifact_bytes')) is int and capture['artifact_bytes']>0, 'owner artifact byte size')
    require(capture.get('capture_count')==74, 'owner capture inventory')
    require(re.fullmatch(r'[0-9a-f]{64}',capture.get('artifact_sha256','')) is not None, 'owner artifact digest')
    require(provider.get('repository')=='caribousun/focuschrist-website' and provider.get('event')=='pull_request', 'provider identity')
    require(type(provider.get('pr_number')) is int and provider['pr_number']==531 and provider.get('ref')=='refs/pull/531/merge', 'provider PR/ref mismatch')
    for key in ('head_sha','checkout_sha','tree_sha','base_sha'):
        require(isinstance(provider.get(key),str) and re.fullmatch(r'[0-9a-f]{40}',provider[key]) is not None, 'invalid provider SHA '+key)
    require(provider.get('parents')==[provider['base_sha'],provider['head_sha']], 'provider merge parents mismatch')
    for key in ('run_id','timeline_job_id','timeline_artifact_id','owner_job_id','owner_artifact_id'):
        require(isinstance(provider.get(key),str) and re.fullmatch(r'[1-9][0-9]*',provider[key]) is not None, 'invalid provider ID '+key)
    for key in ('head_sha','checkout_sha','tree_sha','run_id'):
        require(provider.get(key)==identity.get(key), 'provider identity mismatch '+key)
    require(provider.get('timeline_job_id')==identity.get('job_id') and provider.get('timeline_artifact_id')==identity.get('artifact_id') and provider.get('timeline_artifact_bytes')==identity.get('artifact_bytes') and provider.get('timeline_artifact_sha256')==identity.get('artifact_sha256'), 'provider Timeline evidence mismatch')
    require(provider.get('owner_job_id')==capture.get('job_id') and provider.get('owner_artifact_id')==capture.get('artifact_id') and provider.get('owner_artifact_bytes')==capture.get('artifact_bytes') and provider.get('owner_artifact_sha256')==capture.get('artifact_sha256'), 'provider owner evidence mismatch')
    require(provider.get('timeline_job_id')!=provider.get('owner_job_id') and provider.get('timeline_artifact_id')!=provider.get('owner_artifact_id'), 'distinct producer jobs and artifacts required')
    require(provider.get('timeline_job_conclusion')=='success' and provider.get('owner_job_conclusion')=='success', 'provider job not successful')
    require(provider.get('source_blobs')=={'adams-integration.css':'70a3a767c87096dbc60fc4d01f469d9dd8e54a2a','tools/adams_chart_browser_qa.js':'03baf35e2b1525a343cd2bf23422df142dd16038','tools/owner_integration_qa_contract.json':'2fdb9f261db7af4e1213d243daefeac417eb5311'}, 'provider source tree differs')
    contract=json.loads(bound(root,OWNER_CONTRACT))
    require(contract.get('version')==1 and contract.get('ready') is True, 'current owner contract not ready')
    checked=owner.get('checked',[])
    require(checked==contract['sources']+contract['assets'], 'owner checked source/asset inventory differs from exact current contract')
    require([r for r in checked if r.get('path')==CSS['path']]==[CSS], 'owner did not render exact candidate stylesheet')


def validate(root, added, covered, rejected):
    # Current dispatch never falls back to old rendered approval.
    # Pin checks precede reading the new record.
    require(APPROVED_RECORD_SHA256 is not None and APPROVED_SPEC_SHA256 is not None and APPROVED_PROVIDER_SHA256 is not None, 'new actual review/provider evidence still pending')
    record=json.loads(local(root,RECORD).read_bytes())
    require(canonical(record)==APPROVED_RECORD_SHA256 and type(record.get('schema')) is int and record.get('schema')==1 and record.get('status')=='REVIEWED_EXACT_HEADER_SUCCESSOR', 'unreviewed successor record')
    spec=record['spec'];require(canonical(spec)==APPROVED_SPEC_SHA256, 'unreviewed successor spec')
    provider_item=record['provider_evidence'];require(provider_item['path'].startswith('docs/adams-header-evidence-successor/'), 'unsafe provider evidence location')
    provider=json.loads(bound(root,provider_item));require(canonical(provider)==APPROVED_PROVIDER_SHA256, 'independently verified provider identity pending or changed')
    assignment_item=record['role_assignment'];require(assignment_item['path']=='docs/adams-header-evidence-successor/review-role-assignment.json', 'role assignment path mismatch')
    assignment=json.loads(bound(root,assignment_item));require(canonical(assignment)==APPROVED_ASSIGNMENT_SHA256, 'review role assignment changed')
    old=json.loads(local(root,prior.MANIFEST).read_bytes())
    prior.validate_reviews(root,old)
    historical=json.loads(bound(root,old['spec']['historical_record']))
    from adams_source_import_v9 import validate_reviews as validate_historical_reviews
    validate_historical_reviews(root,historical)
    require(historical['spec']['assets']==old['spec']['assets'], 'historical 331 asset ownership changed')
    prior.validate_source(root,old,added,covered,rejected,context_reader=historical_reader)
    qa_checks.validate_qa(root,old['spec'],helper_reader=historical_reader)
    validate_spec_delta(old['spec'],spec)
    for item in spec['context']:bound(root,item)
    qa_checks.validate_qa(root,spec)
    validate_owner_provenance(root,spec,provider)
    validate_current_reviews(root,record,APPROVED_SPEC_SHA256,spec,assignment)
    return {r['path'] for r in spec['assets']}
