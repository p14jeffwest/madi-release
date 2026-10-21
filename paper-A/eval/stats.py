#!/usr/bin/env python3
"""평가 2차 통계 (§1.2): 작은 셋의 부트스트랩 95% 구간과 기준 분석기 대비 쌍 비교.
  F1 셋:   python tools/compare/stats.py f1 GOLD.tsv REF A1 [A2 …] [--rubric strict|neutral|n25] [--odd] [--n 2000]
           문장 단위 재표집(2,000회)으로 형태소 F1 의 95% 구간, REF 와의 차이 구간·P(차이 ≤ 0)
  모호성:  python tools/compare/stats.py disamb DIR REF A1 [A2 …] [--conv]
           문항 정오 → 정확도 95% 구간(재표집) + McNemar 정확 검정(REF 대비), --conv 는 관행 도달 불가 17문항 제외
출력 캐시는 out/compare/<분석기>/ (run.py)."""
import glob, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S

args = sys.argv[1:]
def opt(name, default=None, flag=False):
    if flag:
        if name in args: args.remove(name); return True
        return False
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
N = int(opt('--n', '2000')); RUB = opt('--rubric', 'neutral'); ODD = opt('--odd', flag=True); CONV = opt('--conv', flag=True)
OUT = opt('--out', 'out/compare')
random.seed(20261013)


def per_sent(gold, pred, an):
    rows = []
    if RUB == 'n25':
        import neutral25 as N25
    for gl, pl in zip(gold, pred):
        g = S.harmonize(S.parse_line(gl)); p = S.harmonize(S.parse_line(pl, an))
        if RUB == 'neutral': g, p = S.neutral(g, False), S.neutral(p, False)
        elif RUB == 'n25': g, p = S.neutral(N25.canon25(g), False), S.neutral(N25.canon25(p), False)
        rows.append((S.lcs(g, p), len(p), len(g)))
    return rows


def f1_of(rows, idx):
    m = sum(rows[i][0] for i in idx); p = sum(rows[i][1] for i in idx); g = sum(rows[i][2] for i in idx)
    return S.f1(m, p, g)


def ci(xs):
    xs = sorted(xs); return xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs)) - 1]


def mcnemar(a, b):
    """정확 이항 검정 (양측): a 만 맞힘 vs b 만 맞힘"""
    n01 = sum(1 for x, y in zip(a, b) if x and not y); n10 = sum(1 for x, y in zip(a, b) if y and not x)
    n = n01 + n10
    if n == 0: return n01, n10, 1.0
    k = min(n01, n10)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n * 2
    return n01, n10, min(1.0, p)


mode = args.pop(0)
if mode == 'f1':
    gpath, ref, ans = args[0], args[1], args[2:]
    gold = S.load_gold(gpath); base = os.path.basename(gpath).rsplit('.', 1)[0]
    sel = list(range(1, len(gold), 2)) if ODD else list(range(len(gold)))
    R = {}
    for an in [ref] + ans:
        pred = open(os.path.join(OUT, an, base + '.txt'), encoding='utf-8').read().rstrip('\n').split('\n')
        rows = per_sent(gold, pred, an); R[an] = [rows[i] for i in sel]
    n = len(sel); boots = [[random.randrange(n) for _ in range(n)] for _ in range(N)]
    print(f'{base} ({n} 문장{", 홀수" if ODD else ""}, 잣대 {RUB}, 재표집 {N})')
    print('%-18s %8s %19s %9s %19s %9s' % ('분석기', 'F1', '95% 구간', f'−{ref}', '차이 95% 구간', 'P(≤0)'))
    rb = [f1_of(R[ref], b) for b in boots]
    for an in [ref] + ans:
        f = f1_of(R[an], range(n)); bs = [f1_of(R[an], b) for b in boots]
        lo, hi = ci(bs)
        if an == ref:
            print('%-18s %8.4f   [%.4f, %.4f]' % (an, f, lo, hi)); continue
        d = [x - y for x, y in zip(bs, rb)]; dl, dh = ci(d)
        print('%-18s %8.4f   [%.4f, %.4f] %+9.4f   [%+.4f, %+.4f] %9.3f' % (an, f, lo, hi, f - f1_of(R[ref], range(n)), dl, dh, sum(x <= 0 for x in d) / N))
elif mode == 'disamb':
    dirp, ref, ans = args[0], args[1], args[2:]
    excl = set()
    if CONV:
        recs = [json.loads(l) for l in open('out/b2/kiwi510.jsonl', encoding='utf-8')]
        un = {int(l.split('\t')[0]) for l in open('out/audit/audit1.tsv', encoding='utf-8').read().split('\n')[1:] if l and l.split('\t')[5] == 'unreach'}
        excl = {(recs[i]['set'].split('/')[1], recs[i]['s']) for i in un}
    items = []
    for sp in sorted(glob.glob(os.path.join(dirp, '*.txt'))):
        base = os.path.basename(sp)[:-4]
        for k, l in enumerate(x for x in open(sp, encoding='utf-8').read().split('\n') if x):
            a, s = l.split('\t'); items.append((base, k, a, s))
    HIT = {}
    for an in [ref] + ans:
        cache = {}
        hits = []
        for base, k, a, s in items:
            if base not in cache: cache[base] = open(os.path.join(OUT, an, base + '.txt'), encoding='utf-8').read().rstrip('\n').split('\n')
            f, t = a.split('/'); pl = cache[base][k]
            if an in S.GROUP_ONLY and t.startswith('VA'): hits.append(None); continue
            want = (f, 'V' if t.startswith('V') else S.group(t)) if an in S.GROUP_ONLY else (f, t[:2] if t.startswith('V') else t[:1])
            toks = set()
            for w in pl.split(' '):
                if '/' not in w: continue
                ff, tt = w.rsplit('/', 1)
                toks.add((S.norm_form(ff), S.map_tag(an, tt)) if an in S.GROUP_ONLY else S.conv(an, ff, tt))
            hits.append(want in toks)
        HIT[an] = hits
    keep = [i for i, (b, k, a, s) in enumerate(items) if (b, s) not in excl]
    print(f'kiwi510 ({len(keep)} 문항{", 관행 도달 불가 " + str(len(items) - len(keep)) + " 제외" if CONV else ""}, 재표집 {N})')
    print('%-18s %8s %19s %16s %9s' % ('분석기', '정확도', '95% 구간', f'{ref}만/이것만', 'McNemar p'))
    for an in [ref] + ans:
        idx = [i for i in keep if HIT[an][i] is not None and HIT[ref][i] is not None]
        h = [HIT[an][i] for i in idx]; n = len(h)
        acc = sum(h) / n
        bs = []
        for _ in range(N):
            smp = [h[random.randrange(n)] for _ in range(n)]; bs.append(sum(smp) / n)
        lo, hi = ci(bs)
        if an == ref:
            print('%-18s %8.4f   [%.4f, %.4f]' % (an, acc, lo, hi)); continue
        a, b, p = mcnemar([HIT[ref][i] for i in idx], h)
        print('%-18s %8.4f   [%.4f, %.4f] %8d / %-6d %9.4f%s' % (an, acc, lo, hi, a, b, p, '' if n == len(keep) else f'  (n={n})'))
