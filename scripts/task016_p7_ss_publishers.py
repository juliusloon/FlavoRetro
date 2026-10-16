"""Lawful public publisher originals/SI fallback for primary no-PMC sources."""
import json,sys,urllib.parse,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_ss_sources import OUT,request,rows,save,save_rows,now,sha

def execute():
    dois=['10.1007/s11103-013-0133-1','10.1111/tpj.12030','10.1080/09168451.2018.1491286','10.1007/s00253-015-6982-6','10.1007/s00425-025-04742-w']
    plan=[dict(query_id='SS-PUBLIC-PUBLISHER:'+str(i),doi_hint=doi,url='https://doi.org/'+doi,registered_at=now(),scope_freeze_sha256=sha(OUT/'scope_freeze.json'),reason='Lawful public publisher route after no official PMCID; request landing HTML and explicit public SI links only, no login/paywall/captcha circumvention') for i,doi in enumerate(dois)]
    if (OUT/'fresh_public_publisher_plan.jsonl').exists():raise RuntimeError('ALREADY_REGISTERED')
    save_rows('fresh_public_publisher_plan.jsonl',plan);out=[]
    for q in plan:
        res=request(q['url'],'publisher_html',q['reason'],phase='fresh',route='public_publisher_original_SI')
        pointers=[]
        if res['status_code']==200 and not res['error']:
            text=(ROOT/res['path']).read_text(errors='replace')
            for href in re.findall(r'href=[\"\']([^\"\']+)[\"\']',text):
                if any(k in href.lower() for k in ['moesm','suppl','suppinfo','supporting','s001','suppitem']):pointers.append(href)
        out.append(dict(q,response=res,public_attachment_pointers=sorted(set(pointers)),evidence_eligible=False,disposition='deferred_public_original_attachment_review' if pointers else 'deferred_no_open_machine_readable_original_or_SI',read_model_outcomes=False))
        save_rows('fresh_public_publisher_execution.jsonl',out)
    print(dict(planned=len(plan),executed=len(out),attachments=sum(len(r['public_attachment_pointers']) for r in out)))
if __name__=='__main__':execute()
