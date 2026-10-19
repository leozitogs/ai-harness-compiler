"""Synthetic repository, real failing/passing pytest, simulated human decision."""
import json
import sys
from pathlib import Path

sys.path.insert(0,str(Path.cwd()/'tests'))
from test_qa_runtime import repo_request,git
from test_qa import finding
from ai_harness_compiler.models.qa import FACETS,QAInspection
from ai_harness_compiler.qa import review_report
from ai_harness_compiler.qa_collection import capture
from ai_harness_compiler.qa_runner import run_checks
from ai_harness_compiler.cli import main

area=Path('.factory/qa-resolution-fixture-final2').resolve()
area.mkdir(exist_ok=False)
root,initial=repo_request(area)
(root/'.gitignore').write_text('.factory/\n__pycache__/\n',encoding='utf-8',newline='\n')
(root/'tests').mkdir()
(root/'pyproject.toml').write_text('[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',encoding='utf-8',newline='\n')
(root/'tests/test_approval.py').write_text('from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path.cwd()/"src"))\nfrom approval import authorize\ndef test_rejects_unapproved_request():\n    assert authorize(False) is False\n',encoding='utf-8',newline='\n')
git(root,'add','.')
git(root,'commit','-m','add business regression fixture')
before=git(root,'rev-parse','HEAD')
sources=['src/approval.py','tests/test_approval.py']
old=capture(root,initial.snapshot,before,before,'fixture-author',sources,check_ids=['tests'])
previous=review_report(old,QAInspection(findings=[finding()],inspected_facets=list(FACETS),limitations=['Synthetic known bug; analyst inspection, no model.']),run_checks(old,root,before),engine='provided-inspection',inspection_status='completed')
assert previous.checks[0].status=='failed'
(root/'src/approval.py').write_text('def authorize(approved):\n    return approved\n',encoding='utf-8',newline='\n')
git(root,'add','.')
git(root,'commit','-m','fix business approval fixture')
after=git(root,'rev-parse','HEAD')
new=capture(root,initial.snapshot,before,after,'fixture-author',sources,check_ids=['tests'])
current=review_report(new,QAInspection(inspected_facets=list(FACETS),limitations=['Synthetic known fix; analyst inspection, no model.']),run_checks(new,root,after),engine='provided-inspection',inspection_status='completed')
assert current.checks[0].status=='passed'
for name,data in [('previous.json',previous.model_dump()),('current.json',current.model_dump()),('evidence.json',dict(finding_id='approval-bypass',citations=[dict(path='src/approval.py',line=2,quote='return approved')],check_ids=['tests'],rationale='Known fixture previously returned True for False; same real regression now passes after fix.'))]:
 (area/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
common=['--repository',str(root)]
assert main(['qa','propose-resolution',str(area/'previous.json'),str(area/'current.json'),'--evidence',str(area/'evidence.json'),*common,'--output',str(area/'proposal.json')])==0
assert main(['qa','compare',str(area/'previous.json'),str(area/'current.json'),*common,'--team-output',str(area/'pending-team'),'--output',str(area/'pending-comparison.json')])==0
assert main(['qa','review-resolution',str(area/'proposal.json'),*common,'--decision','confirm','--actor','simulated-fixture-human','--comment','SIMULATION ONLY: not the PO decision on the real project.','--output',str(area/'simulated-decision.json')])==0
assert main(['qa','compare',str(area/'previous.json'),str(area/'current.json'),*common,'--resolution',str(area/'simulated-decision.json'),'--team-output',str(area/'confirmed-team'),'--output',str(area/'confirmed-comparison.json')])==0
inventory={'synthetic_repository':True,'human_confirmation_simulated':True,'real_project_acceptance':False,'model_calls':0,'old_tests':previous.checks[0].status,'new_tests':current.checks[0].status,'global_semantic_acceptance':'not-established','runs':[]}
for name in ['pending','confirmed']:
 team=json.loads((area/f'{name}-team/team-report.json').read_text(encoding='utf-8'))
 nexo=next(r for r in team['reports'] if r['agent_id']=='delivery')['observations'][-1]['data']
 comp=json.loads((area/f'{name}-comparison.json').read_text(encoding='utf-8'))
 inventory['runs'].append(dict(id=name,status=team['status'],recommendation=nexo['combined_review_recommendation'],blockers=len(nexo['combined_blocking_findings']),pending=comp['pending_previous_findings'],resolved=comp['resolved_previous_findings']))
assert inventory['runs'][0]['blockers']==1
assert inventory['runs'][1]['blockers']==0
(area/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(inventory,indent=2))
