import asyncio
import esprima

FUNC_TYPES = ('FunctionDeclaration',
              'FunctionExpression',
              'ArrowFunctionExpression')


def iter_nodes(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from iter_nodes(v)
    elif isinstance(node, list):
        for item in node:
            yield from iter_nodes(item)


def node_text(node):
    t = node.get('type')
    if t == 'Identifier':
        return node.get('name') or ''
    if t == 'Literal':
        if node.get('raw') is not None:
            return node['raw']
        v = node.get('value')
        return '' if v is None else str(v)
    if t == 'TemplateElement':
        v = node.get('value') or {}
        return (v.get('cooked') or '') + (v.get('raw') or '')
    return ''


def collect_functions(tree):
    funcs, names = {}, {}
    for n in iter_nodes(tree):
        t = n.get('type')
        if t in FUNC_TYPES:
            funcs[tuple(n['range'])] = n
            if n.get('id'):
                names[tuple(n['range'])] = n['id']['name']
        elif t in ('Property', 'MethodDefinition'):
            val = n.get('value') or {}
            if val.get('type') in FUNC_TYPES:
                key = n.get('key') or {}
                names[tuple(val['range'])] = key.get('name') or str(key.get('value'))
        elif t == 'VariableDeclarator':
            init = n.get('init') or {}
            if init.get('type') in FUNC_TYPES and n.get('id'):
                names[tuple(init['range'])] = n['id']['name']
        elif t == 'AssignmentExpression':
            right, left = n.get('right') or {}, n.get('left') or {}
            if right.get('type') in FUNC_TYPES:
                name = left.get('name') \
                       or (left.get('property') or {}).get('name') \
                       or str((left.get('property') or {}).get('value') or '')
                if name:
                    names[tuple(right['range'])] = name
    return funcs, names


# ---------- 同步核心:纯 CPU 计算,保持同步 ----------
def _find_sync(code, keyword):
    tree = esprima.parseScript(code, {'range': True, 'loc': True,'tolerant': True}).toDict()
    funcs, names = collect_functions(tree)

    def make_hit(f):
        s, e = f['range']
        return {'name': names.get((s, e), '<anonymous>'),
                'line': f['loc']['start']['line'], # 1 起始
                'column': f['loc']['start']['column'],
                'range': (s, e),
                'source': code[s:e]}

    hits, stack = {}, []

    def walk(node):
        if isinstance(node, dict):
            is_func = node.get('type') in FUNC_TYPES
            if is_func:
                stack.append(node)
            if stack and keyword in node_text(node):
                rng = tuple(stack[-1]['range'])
                hits.setdefault(rng, make_hit(stack[-1]))
            for v in node.values():
                walk(v)
            if is_func:
                stack.pop()
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(tree)

    for rng, fname in names.items():
        if keyword in fname and rng not in hits:
            hits[rng] = make_hit(funcs[rng])

    return list(hits.values())

def _list_all_sync(code):
    tree = esprima.parseScript(
        code, {'range': True, 'loc': True, 'tolerant': True}
    ).toDict()
    funcs, names = collect_functions(tree)

    results = []
    for rng, f in funcs.items():
        s, e = rng
        results.append({
            'name': names.get(rng, '<anonymous>'),
            'line': f['loc']['start']['line'],
            'column': f['loc']['start']['column'],
            'range': (s, e),
            # 'source': code[s:e],
        })
    # 按出现位置排序,可读性更好
    results.sort(key=lambda x: x['range'][0])
    return results


# ---------- 异步封装 ----------
async def find_functions_by_keyword(code, keyword):
    """单个 JS 源码的异步查找(解析在线程池中跑,不阻塞事件循环)"""
    return await asyncio.to_thread(_find_sync, code, keyword)

async def list_functions(code, name_pattern=None):
    """列出所有函数;name_pattern 给定时按子串过滤名字"""
    funcs = await asyncio.to_thread(_list_all_sync, code)
    if name_pattern:
        funcs = [f for f in funcs if name_pattern in f['name']]
    return funcs