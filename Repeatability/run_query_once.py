import sys, os
sys.path.append('.')
from query_engine import process_query

q = ' '.join(sys.argv[1:]).strip()
res = process_query(q)

if isinstance(res, dict) and 'error' in res:
    print('ERROR:', res['error']); raise SystemExit
if isinstance(res, str):
    print(res); raise SystemExit

lens = res.get('strategicThinkingLens') or res.get('Strategic Thinking Lens') or ''
fu = res.get('followUpPrompts') or res.get('Follow-up Prompts') or []
concepts = res.get('conceptsToolsPractice') or res.get('Concepts/Tools') or []

print('Strategic Thinking Lens:\n' + lens)
print('\nFollow-up Prompts:')
for p in fu: print('- ' + p)
print('\nConcepts/Tools:')
if isinstance(concepts, str):
    print(concepts)
else:
    for c in concepts[:4]:
        if isinstance(c, dict):
            term = c.get('term',''); definition = c.get('definition','')
        else:
            term = c[0]; definition = c[1] if len(c)>1 else ''
        print(f'- {term}: {definition}')
