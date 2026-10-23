#!/bin/sh
# One graded run of an eval case. Appends one line to results.jsonl.
# Usage: run-one.sh <eval> <case> <profile> <run-label>
#   e.g. run-one.sh easy wordpress wp-17b-16k 17b-easy-wordpress-1
#
# A case with an `input` (the easy tier) is the committed model input: its
# hash is checked against SHA256SUMS, then it goes to the eval's role through
# `darkmux dispatch --message-from-file`, so nothing on this machine fetches
# or converts the site. Needs DARKMUX_HOME pointing at a home for eval runs
# (the fixture's pinned role is installed into it),
# darkmux on PATH, and python3 (for this harness and the grader).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
eval_id=$1 case=$2 profile=$3 label=$4
manifest=$here/evals/$eval_id.json
field() {
  python3 -c "import json,sys
e=json.load(open(sys.argv[1])); c=[c for c in e['cases'] if c['id']==sys.argv[2]][0]
print({**e, **c}.get(sys.argv[3], ''))" "$manifest" "$case" "$1"
}
role=$(field role) input=$(field input)
[ -n "$input" ] || { echo "case $case of $eval_id has no committed input" >&2; exit 2; }

# The input must be the committed bytes, or the run proves nothing.
sha=$(python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$here/$input")
grep -q "^$sha  $input\$" "$here/SHA256SUMS" || { echo "$input does not match SHA256SUMS" >&2; exit 2; }

# The role's prompt and schema decide the score, so the run uses the fixture's
# own copy, pinned by hash in the eval, installed into the run's darkmux home.
[ -n "${DARKMUX_HOME:-}" ] && python3 -c "import os,sys;sys.exit(os.path.realpath(sys.argv[1])==os.path.realpath(os.path.expanduser('~/.darkmux')))" "$DARKMUX_HOME" ||
  { echo "set DARKMUX_HOME to a home for eval runs (not ~/.darkmux): the role is installed there" >&2; exit 2; }
role_sha=$(python3 -c "import hashlib,json,sys,pathlib
here=pathlib.Path(sys.argv[1]); pins=json.load(open(sys.argv[2]))['role_sha256']; dest=pathlib.Path(sys.argv[3])/'roles'
dest.mkdir(parents=True, exist_ok=True); both=hashlib.sha256()
for rel,want in sorted(pins.items()):
    b=(here/rel).read_bytes(); got=hashlib.sha256(b).hexdigest()
    if got!=want: sys.exit(f'{rel} does not match the eval pin ({got})')
    (dest/pathlib.Path(rel).name).write_bytes(b); both.update(got.encode())
print(both.hexdigest())" "$here" "$manifest" "$DARKMUX_HOME")

# Reply room is the machine's to give: the profile's context window, less the
# prompt (system prompt plus input, overestimated at 3 bytes a token).
room=$(python3 -c "import json,sys,pathlib
home=pathlib.Path(sys.argv[1]); prof=json.load(open(home/'profiles.json'))['profiles'][sys.argv[2]]
n=[m.get('n_ctx') for m in prof['models'] if m.get('n_ctx')]
if not n: sys.exit('profile '+sys.argv[2]+' declares no n_ctx: the run needs a context window')
prompt=sum((home/'roles'/f).stat().st_size for f in ('web-probe.md',))+pathlib.Path(sys.argv[3]).stat().st_size
print(n[0], max(1024, n[0]-(prompt+2)//3))" "$DARKMUX_HOME" "$profile" "$here/$input")
n_ctx=${room% *} cap=${room#* }

mkdir -p "$here/runs"
raw=$here/runs/$label.json answer=$here/runs/$label.answer.json
rm -f "$raw" "$answer"

start=$(date +%s)
set +e
darkmux dispatch "$role" --message-from-file "$here/$input" --profile "$profile" --max-completion-tokens "$cap" --json > "$raw" 2> "$here/runs/$label.log"
code=$?
set -e
secs=$(( $(date +%s) - start ))

# The answer is the envelope's final_assistant (or the whole output when it is not an envelope).
if [ -s "$raw" ]; then
  python3 -c "import json,sys
t=open(sys.argv[1]).read()
try:
    d=json.loads(t); t=d['final_assistant'] if isinstance(d,dict) and isinstance(d.get('final_assistant'),str) else t
except ValueError: pass
open(sys.argv[2],'w').write(t)" "$raw" "$answer"
  grade=$(python3 "$here/grade.py" "$case" "$answer" | python3 -c 'import json,sys;print(json.dumps(json.load(sys.stdin)))') || true
else
  grade='{"passed": false, "error": "no answer written"}'
fi
printf '{"label":"%s","eval":"%s","case":"%s","profile":"%s","input_sha256":"%s","role_sha256":"%s","n_ctx":%s,"max_completion_tokens":%s,"dispatch_exit":%s,"seconds":%s,"grade":%s}\n' \
  "$label" "$eval_id" "$case" "$profile" "$sha" "$role_sha" "$n_ctx" "$cap" "$code" "$secs" "$grade" | tee -a "$here/results.jsonl"
