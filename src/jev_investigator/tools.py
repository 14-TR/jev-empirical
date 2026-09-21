"""Closed, issue-derived selectors for real read-only tools."""
import ast
import re
from .source import git, safe_text, digest

STOP = set('the and with this that from have issue when then into does should would could return returns value wrong'.split())


def keywords(issue):
    words = re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,47}', issue['title'] + '\n' + issue['body'])
    return list(dict.fromkeys(w.lower() for w in words if w.lower() not in STOP))[:12]


def candidates(issue, snapshot, observations, used, allow_checks=False, profiles=()):
    result = []
    def add(tool, args, label):
        key = tool + ':' + repr(args)
        if key not in used: result.append({'id': 'c%02d' % len(result), 'tool': tool, 'args': args, 'label': label, 'key': key})
    words = keywords(issue)
    for word in words[:8]: add('search_text', {'term': word}, 'Find literal issue keyword: ' + word)
    hits = [ref['path'] for o in observations for ref in o.get('refs', []) if 'path' in ref and ref['path'] in snapshot.files]
    ranked = sorted(snapshot.files, key=lambda p: (-sum(w in p.lower() for w in words), p))
    paths = list(dict.fromkeys(hits + ranked))[:6]
    for path in paths:
        windows = [1] + [max(1, ref['start'] - 8) for o in observations for ref in o.get('refs', [])
                         if ref.get('path') == path and 'start' in ref]
        for start in list(dict.fromkeys(windows))[:2]:
            add('read_lines', {'path': path, 'start': start, 'end': start + 39}, 'Read ' + path + ':' + str(start))
        add('git_history', {'path': path}, 'Read immutable history of ' + path)
    for o in observations:
        if o['tool'] == 'git_history':
            for commit in o['commits'][:2]:
                add('git_diff', {'path': o['path'], 'commit': commit}, 'Inspect change ' + commit[:10] + ' / ' + o['path'])
    # Only named, operator-approved profiles may ever become executable candidates.
    if allow_checks:
        for profile in profiles: add('run_check', {'profile': profile}, 'Run trusted fixed check: ' + profile)
    # Round-robin preserves every available tool class within the provider's
    # 20-choice contract; checks/diffs cannot be crowded out by search terms.
    groups = {tool: [c for c in result if c['tool'] == tool]
              for tool in ('search_text', 'read_lines', 'git_history', 'git_diff', 'run_check')}
    result = []
    while len(result) < 18 and any(groups.values()):
        for group in groups.values():
            if group and len(result) < 18: result.append(group.pop(0))
    add('synthesize', {}, 'Ask local Qwen for a cited report of current evidence; not a fix or success claim')
    add('clarify', {}, 'Stop for operator clarification; missing scope or evidence')
    for index, candidate in enumerate(result): candidate['id'] = 'c%02d' % index
    return result


def reference(snapshot, path, start, end):
    return {'commit': snapshot.commit, 'path': path, 'start': start, 'end': end,
            'sha256': snapshot.files[path]['sha256']}


def execute(candidate, snapshot, timeout=20, check=None):
    tool, args = candidate['tool'], candidate['args']
    if tool == 'search_text':
        term = args['term']; hits = []; refs = []
        # Search implementation and test sources before generated exports/docs;
        # this is a repository-role heuristic, never an issue-specific answer.
        for path in sorted(snapshot.files, key=lambda p: (0 if p.startswith('src/') else 1 if p.startswith('tests/') else 2, p)):
            for line, text in enumerate(snapshot.read(path).splitlines(), 1):
                if term.casefold() in text.casefold():
                    hits.append({'path': path, 'line': line, 'text': text[:240]})
                    refs.append(reference(snapshot, path, line, line))
                    if len(hits) == 12: break
            if len(hits) == 12: break
        return {'tool': tool, 'term': term, 'hits': hits, 'refs': refs, 'limit': 12}
    if tool == 'read_lines':
        path = args['path']; text = snapshot.read(path); lines = text.splitlines()
        start, end = args['start'], min(args['end'], len(lines))
        if start < 1 or end < start or end - start >= 40: raise ValueError('line_range_denied')
        selected = '\n'.join('%d: %s' % (n, lines[n-1]) for n in range(start, end + 1))
        if len(selected.encode()) > 6000: raise ValueError('read_output_budget')
        symbols = []
        if path.endswith('.py'):
            try:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and start <= node.lineno <= end:
                        symbols.append({'name': node.name, 'kind': type(node).__name__,
                                        'source': reference(snapshot, path, node.lineno, node.end_lineno)})
            except (SyntaxError, ValueError, RecursionError): pass
        return {'tool': tool, 'text': selected, 'refs': [reference(snapshot, path, start, end)], 'symbols': symbols[:12]}
    if tool == 'git_history':
        path = args['path']
        if path not in snapshot.files: raise ValueError('path_denied')
        raw = git(snapshot.repo, ['log', '-5', '--format=%H', snapshot.commit, '--', path], timeout=timeout, cap=4096)
        commits = raw.decode().splitlines()
        from .source import SHA
        if not all(SHA.fullmatch(c) for c in commits): raise ValueError('history_invalid')
        return {'tool': tool, 'path': path, 'commits': commits, 'refs': [{'commit': snapshot.commit, 'path': path}]}
    if tool == 'git_diff':
        path = args['path']; commit = args['commit']
        from .source import SHA
        if path not in snapshot.files or not SHA.fullmatch(commit): raise ValueError('diff_selector_denied')
        raw = git(snapshot.repo, ['show', '--format=', '--no-ext-diff', '--no-textconv', '--unified=3', commit, '--', path], timeout=timeout, cap=8192)
        text = raw.decode('utf-8')
        if not safe_text(text): raise ValueError('sensitive_history')
        refs = []
        for match in re.finditer(r'^@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@', text, re.M):
            refs.append({'commit': commit, 'path': path, 'start': int(match[3]),
                         'end': int(match[3]) + max(0, int(match[4] or '1') - 1), 'diff_sha256': digest(raw)})
        return {'tool': tool, 'text': text, 'refs': refs, 'commit': commit, 'path': path}
    if tool == 'run_check' and check is not None: return check(args['profile'], timeout)
    raise ValueError('tool_denied')
