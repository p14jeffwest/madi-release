#!/usr/bin/env python3
"""run.py 가 남긴 분석기 출력을 같은 잣대로 채점한다 (10장 §3, 2026.10.8).

사용:
  python tools/compare/score.py GOLD.tsv A1 [A2 ...] [--out out/compare] [--errors N]   # 형태소 F1 표
  python tools/compare/score.py --disamb DIR A1 [A2 ...]                               # Kiwi 모호성 셋(DIR/*.txt)

잣대 (모든 분석기에 똑같이; 정답에도 같은 변환을 한다):
  태그 사상  각 분석기 태그 → 세종(모두의 말뭉치) 태그. Hannanum·Okt 는 세종으로 사상할 수 없어 '묶음'(N V M I J E X S U)만.
  엄격(strict)  사상 + 자모 정규화(첫가끝 → 호환) + 아/어 이형태를 세종 표기로(eval_kiwi.py --harmonize 와 같음).
  중립(neutral) 엄격 + 분석기마다 갈리는 관행을 양쪽에서 똑같이 지운다:
      ① 숫자: 1/SN ,/SP 000/SN → 1,000/SN (숫자 사이 . , 로 이은 것을 한 토큰으로)
      ② 글자 부류: 숫자만 → SN, 한자만 → SH, 로마자만 → SL (Kkma 의 NR·OH·OL, Hannanum 의 NN 등)
      ③ 어근+하: XR 하/XSA → X하/VA (말뭉치는 통째, 다른 분석기는 가름)
      ④ 명사 연쇄: 이어진 NNG·NNP 를 한 토큰(태그 NN)으로 (복합명사 단위 차이 — 국회/의원 vs 국회의원)
      ⑤ 기호: S* 태그는 글자로 다시 정한다(따옴표·괄호 SS, .?! SF, ,·:/ SP, … SE, -~ SO, 나머지 SW)
      ⑦ 준말 거/NNB → 것/NNB, ⑧ ㄹ 어간 뒤 은/을/음 → ㄴ/ㄹ/ㅁ (이형태 표기 차이)
      ⑥ 존재의 있: 있/VV·있/VA → 있/VA (말뭉치는 VA; 보조용언 VX 는 그대로)
      ⑨ (10.13) 종결 어미 + 요/JX → X요/EF, 이렇게·그렇게·어떻게/MAG → X/VA 게/EC (Kiwi 관행; MADI_NEUTRAL_J=0 이면 끔)
  분석기별 단위 맞춤: Kkma 의 더/EP ㄴ/ETM → 던/ETM, 는/EP 다/EF → 는다/EF.
  중립25(--std25, 정답이 2025 지침인 MP 2025 셋): neutral25.canon25 (통째 용언·명사 연쇄 넓히기·인용 어미·VCP 지움 …) 뒤 중립 — 2018 관행 분석기와 2025 정답 사이의 지침 차이만 지운다.
      확인: madi 2018 출력과 --std-2025 출력이 nx2023 에서 같은 값(0.9691) — 어느 관행에도 유리하지 않다.
  지표: 형태소(형태+태그) F1, 묶음(형태+묶음 태그) F1, 분절(형태만) F1 — 문장별 LCS(madi eval·eval_kiwi.py 와 같은 방식).
"""
import difflib, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VOWEL = json.load(open(os.path.join(HERE, 'vowel_map.json'), encoding='utf-8'))
J = {chr(0x11A7 + i): c for i, c in enumerate('\0ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ') if i}
CHO = {chr(0x1100 + i): c for i, c in enumerate('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')}


def norm_form(f): return ''.join(J.get(c, CHO.get(c, c)) for c in f)


# ---- 태그 사상 ----
SEJONG_COMMON = {'MMD': 'MM', 'MMN': 'MM', 'MMA': 'MM', 'NNBC': 'NNB', 'SSO': 'SS', 'SSC': 'SS', 'SC': 'SP', 'SY': 'SW',
                 'UNKNOWN': 'UN', 'UNA': 'UN', 'VSV': 'XSV', 'SWK': 'SW', 'ZN': 'UN', 'ZV': 'UN', 'ZZ': 'UN',
                 'W_URL': 'SW', 'W_EMAIL': 'SW', 'W_HASHTAG': 'SW', 'W_MENTION': 'SW', 'W_SERIAL': 'SW', 'SB': 'SW', 'XSM': 'XSN'}
KKMA = {'NNM': 'NNB', 'VXV': 'VX', 'VXA': 'VX', 'MDT': 'MM', 'MDN': 'MM', 'MAC': 'MAJ', 'JKM': 'JKB', 'JKI': 'JKV',
        'EPH': 'EP', 'EPT': 'EP', 'EPP': 'EP', 'EFN': 'EF', 'EFQ': 'EF', 'EFO': 'EF', 'EFA': 'EF', 'EFI': 'EF', 'EFR': 'EF',
        'ECE': 'EC', 'ECD': 'EC', 'ECS': 'EC', 'ETD': 'ETM', 'XPV': 'XPN', 'OH': 'SH', 'OL': 'SL', 'ON': 'SN', 'UN': 'UN'}
# Hannanum 22 태그·Okt 품사 → 묶음 (세종 태그로는 못 바꾼다: Hannanum JC 는 격조사 전체, Okt 는 어미를 안 가름)
HANNANUM_G = {'NC': 'N', 'NQ': 'N', 'NB': 'N', 'NN': 'N', 'NP': 'N', 'PV': 'V', 'PA': 'V', 'PX': 'V', 'JP': 'V', 'MM': 'M', 'MA': 'M',
              'II': 'I', 'JC': 'J', 'JX': 'J', 'EP': 'E', 'EF': 'E', 'EC': 'E', 'ET': 'E', 'XP': 'X', 'XS': 'X', 'F': 'S'}
OKT_G = {'Noun': 'N', 'Verb': 'V', 'Adjective': 'V', 'Adverb': 'M', 'Determiner': 'M', 'Conjunction': 'M', 'Modifier': 'M',
         'Exclamation': 'I', 'KoreanParticle': 'I', 'Josa': 'J', 'Eomi': 'E', 'PreEomi': 'E', 'Suffix': 'X', 'VerbPrefix': 'X',
         'Punctuation': 'S', 'Foreign': 'S', 'Alpha': 'S', 'Number': 'S', 'Hashtag': 'S', 'URL': 'S', 'Email': 'S', 'ScreenName': 'S', 'Unknown': 'U'}
GROUP_ONLY = {'hannanum', 'okt'}


def group(tag):
    if tag in ('NN',): return 'N'
    if tag.startswith('NN') or tag in ('NR', 'NP'): return 'N'
    if tag[:1] == 'V': return 'V'
    if tag in ('MM', 'MAG', 'MAJ'): return 'M'
    if tag == 'IC': return 'I'
    if tag[:1] == 'J': return 'J'
    if tag[:1] == 'E': return 'E'
    if tag[:1] == 'X': return 'X'
    if tag[:1] == 'S': return 'S'
    return 'U'


def map_tag(an, tag):
    t = tag.split('-')[0] if an.startswith('kiwi') or an.startswith('madi') else tag   # VV-R/VV-I → VV
    if an in GROUP_ONLY:
        if an == 'hannanum':
            if t[:1] == 'S': return 'S'
            return HANNANUM_G.get(t, 'U')
        return OKT_G.get(t, 'U')
    if an == 'kkma': t = KKMA.get(t, t)
    t = SEJONG_COMMON.get(t, t)
    if t[:1] == 'S' and t not in ('SF', 'SP', 'SS', 'SE', 'SO', 'SW', 'SL', 'SH', 'SN'): t = 'SW'
    return t


# ---- 이형태 (eval_kiwi.py 와 같음) ----
STEM = {'VV', 'VA', 'VX', 'XSV', 'XSA', 'VCP'}


def stem_class(form, tag):
    k = VOWEL.get(form + '/' + tag)
    if k: return k
    cs = list(form)
    if not cs: return 'e'

    def info(c):
        o = ord(c) - 0xAC00
        return None if o < 0 or o >= 11172 else ((o % 588) // 28, o % 28)
    last = info(cs[-1])
    if not last: return 'e'
    v, cd = last
    if v == 18 and len(cs) >= 2 and cd == 0:
        pv = info(cs[-2])
        if pv: v, cd = pv[0], -1
    yang = v in (0, 8)
    if yang and cd == 17 and len(cs) >= 2: return 'e'
    return 'a' if yang else 'e'


def harmonize(toks):
    out = []; prev = None
    for form, tag in toks:
        if tag in ('EP', 'EC', 'EF') and prev and prev[1] in STEM and form[:1] in '어었여였':
            a = stem_class(prev[0], prev[1]) == 'a'
            form = (('아' if a else '어') if form[0] in '어여' else ('았' if a else '었')) + form[1:]
        out.append((form, tag)); prev = (form, tag)
    return out


# ---- 중립화 ----
RE_NUM = re.compile(r'^[0-9]+$'); RE_HAN = re.compile(r'^[一-鿿豈-﫿㐀-䶿]+$'); RE_LAT = re.compile(r'^[A-Za-zＡ-Ｚａ-ｚ]+$')
RE_NUMX = re.compile(r'^[0-9][0-9.,]*[0-9]$|^[0-9]$')


def has_rieul(form):
    c = form[-1:]
    return bool(c) and 0xAC00 <= ord(c) <= 0xD7A3 and (ord(c) - 0xAC00) % 28 == 8


def sym_tag(f):
    c = f[:1]
    if c in '.?!': return 'SE' if f.startswith('..') else 'SF'
    if c in ',·:/ㆍ': return 'SP'
    if c in '"\'“”‘’()[]{}<>「」『』《》〈〉【】〔〕—―': return 'SS'
    if c in '…': return 'SE'
    if c in '-~_∼': return 'SO'
    return 'SW'


J_RULES = os.environ.get('MADI_NEUTRAL_J', '1') != '0'   # 0 이면 10.13 이전 중립 (비교용)
GE_ADV = {'이렇게': '이렇', '그렇게': '그렇', '저렇게': '저렇', '어떻게': '어떻'}


def neutral(toks, group_only):
    # ① 숫자 잇기
    out = []
    for f, t in toks:
        if out and RE_NUMX.match(f) and len(out) >= 2 and out[-1][0] in ('.', ',') and RE_NUMX.match(out[-2][0]):
            sep = out.pop(); p = out.pop(); out.append((p[0] + sep[0] + f, 'SN' if not group_only else 'S')); continue
        out.append((f, t))
    # ② 글자 부류
    o2 = []
    for f, t in out:
        if RE_NUMX.match(f): t = 'S' if group_only else 'SN'
        elif RE_HAN.match(f): t = 'S' if group_only else 'SH'
        elif RE_LAT.match(f): t = 'S' if group_only else 'SL'
        o2.append((f, t))
    if group_only: return o2
    # ⑤ 기호 태그는 글자로 (mecab 의 따옴표 SY 등) ⑥ 존재 '있' 의 VV/VA (말뭉치는 VA, 다른 분석기는 VV)
    o2 = [(f, sym_tag(f) if t[:1] == 'S' and t not in ('SL', 'SH', 'SN') else ('VA' if f == '있' and t in ('VV', 'VA') else t)) for f, t in o2]
    # ⑦ 준말 거/NNB ↔ 것/NNB (말뭉치는 표면형 '거', 다른 분석기는 '것' 으로 복원)
    # ⑧ ㄹ 탈락 어간 뒤 은/을/음 → ㄴ/ㄹ/ㅁ (만들/VV ㄴ/ETM — Kiwi 는 은)
    o5 = []
    for f, t in o2:
        if t == 'NNB' and f == '거': f = '것'
        if o5 and t in ('ETM', 'ETN') and f in ('은', '을', '음') and o5[-1][1] in STEM and has_rieul(o5[-1][0]):
            f = {'은': 'ㄴ', '을': 'ㄹ', '음': 'ㅁ'}[f]
        o5.append((f, t))
    o2 = o5
    # ⑨ (10.13 검토 §2-2) Kiwi 관행 차이 둘: 종결 어미 + 요/JX → X요/EF (거든/EF 요/JX ↔ 거든요/EF), 이렇게·그렇게·저렇게·어떻게/MAG → X/VA 게/EC
    if J_RULES:
        o6 = []
        for f, t in o2:
            if t == 'MAG' and f in GE_ADV:
                o6 += [(GE_ADV[f], 'VA'), ('게', 'EC')]; continue
            if o6 and t == 'JX' and f == '요' and o6[-1][1] == 'EF':
                o6[-1] = (o6[-1][0] + '요', 'EF'); continue
            o6.append((f, t))
        o2 = o6
    # ③ 어근+하
    o3 = []
    for f, t in o2:
        if o3 and o3[-1][1] == 'XR' and f == '하' and t in ('XSA', 'XSV'):
            p = o3.pop(); o3.append((p[0] + '하', 'VA')); continue
        o3.append((f, t))
    # ④ 명사 연쇄
    o4 = []
    for f, t in o3:
        if t in ('NNG', 'NNP', 'NN') and o4 and o4[-1][1] in ('NNG', 'NNP', 'NN'):
            p = o4.pop(); o4.append((p[0] + f, 'NN')); continue
        o4.append((f, t))
    return o4


KKMA_MERGE = {(('더', 'EP'), ('ㄴ', 'ETM')): ('던', 'ETM'), (('는', 'EP'), ('다', 'EF')): ('는다', 'EF'),
              (('ㄴ', 'EP'), ('다', 'EF')): ('ㄴ다', 'EF'), (('는', 'EP'), ('다', 'EC')): ('는다', 'EC')}


def parse_line(s, an=None):
    toks = parse_raw(s, an)
    if an == 'kkma':   # Kkma 는 회상 '더'·현재 '는' 을 선어말로 가른다(던 → 더/EP ㄴ/ETM) — 말뭉치 단위로 합친다
        out = []
        for x in toks:
            if out and (out[-1], x) in KKMA_MERGE: out[-1] = KKMA_MERGE[(out[-1], x)]
            else: out.append(x)
        toks = out
    return toks


def parse_raw(s, an=None):
    toks = []
    for w in s.split(' '):
        if not w or w == '|' or '/' not in w: continue
        f, t = w.rsplit('/', 1)
        if t.startswith('Z_'): continue
        toks.append((norm_form(f), map_tag(an, t) if an else SEJONG_COMMON.get(t, t)))
    return toks


def lcs(a, b): return sum(bl.size for bl in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks())


def f1(m, p, g):
    pr = m / p if p else 0; rc = m / g if g else 0
    return 2 * pr * rc / (pr + rc) if pr + rc else 0


def score_one(gold_lines, pred_lines, an, err=None, nerr=0, std25=False):
    """std25: 정답이 2025 지침(MP 2025)일 때 '중립25'(neutral25.canon25 → neutral)와 그 묶음 F1 을 더한다 (평가 2차 §1.3)"""
    go = an in GROUP_ONLY
    acc = {k: [0, 0, 0] for k in ('strict', 'neutral', 'group', 'form', 'n25', 'n25group')}
    if std25:
        sys.path.insert(0, HERE); import neutral25 as N25
    shown = 0
    for gl, pl in zip(gold_lines, pred_lines):
        g = harmonize(parse_line(gl)); p = harmonize(parse_line(pl, an)) if not go else parse_line(pl, an)
        gn = neutral(g, False); pn = neutral(p, go)
        gg = [(f, group(t)) for f, t in neutral(g, True)] if go else [(f, group(t)) for f, t in gn]
        pg = pn if go else [(f, group(t)) for f, t in pn]
        rows = [('group', gg, pg), ('form', [x[0] for x in gg], [x[0] for x in pg])]
        if not go: rows = [('strict', g, p), ('neutral', gn, pn)] + rows
        if std25 and not go:
            g5 = neutral(N25.canon25(g), False); p5 = neutral(N25.canon25(p), False)
            rows += [('n25', g5, p5), ('n25group', [(f, group(t)) for f, t in g5], [(f, group(t)) for f, t in p5])]
        for k, a, b in rows:
            acc[k][0] += lcs(a, b); acc[k][1] += len(b); acc[k][2] += len(a)
        if err and shown < nerr and not go and gn != pn:
            print(' '.join(f'{f}/{t}' for f, t in gn), file=err); print('  > ' + ' '.join(f'{f}/{t}' for f, t in pn), file=err); shown += 1
    return {k: (f1(*v) if v[1] or v[2] else None) for k, v in acc.items()}


def load_gold(path):
    rows = [l.rstrip('\n').split('\t') for l in open(path, encoding='utf-8') if l.strip()]
    return [r[1] for r in rows]


def main():
    args = sys.argv[1:]
    out_dir = 'out/compare'; nerr = 0
    if '--out' in args: i = args.index('--out'); out_dir = args[i + 1]; del args[i:i + 2]
    if '--errors' in args: i = args.index('--errors'); nerr = int(args[i + 1]); del args[i:i + 2]
    std25 = '--std25' in args
    if std25: args.remove('--std25')
    odd = '--odd' in args   # 홀수 번째 문장만 (nx2023·bareun2 의 짝수 문장은 가중 학습에 씀 — 공개 표는 홀수 반쪽)
    if odd: args.remove('--odd')
    if args[0] == '--disamb':
        return disamb(args[1], args[2:], out_dir)
    gold_path, ans = args[0], args[1:]
    gold = load_gold(gold_path)
    base = os.path.basename(gold_path).rsplit('.', 1)[0]
    n_all = len(gold)
    if odd: gold = gold[1::2]
    print(f'{base} ({len(gold)} 문장{", 홀수 반쪽" if odd else ""})')
    print('%-18s %8s %8s %8s %8s %9s' % ('분석기', '엄격', '중립', '묶음', '분절', 'KB/s') + (' %8s %8s' % ('중립25', '묶음25') if std25 else ''))
    for an in ans:
        p = os.path.join(out_dir, an, base + '.txt')
        if not os.path.exists(p): print('%-18s (출력 없음)' % an); continue
        pred = open(p, encoding='utf-8').read().rstrip('\n').split('\n')
        assert len(pred) == n_all, (an, len(pred), n_all)
        if odd: pred = pred[1::2]
        err = open(os.path.join(out_dir, an, base + '.err.txt'), 'w', encoding='utf-8') if nerr else None
        r = score_one(gold, pred, an, err, nerr, std25)
        tm = open(os.path.join(out_dir, an, base + '.time')).read().split()
        kbs = int(tm[2]) / 1024 / max(float(tm[0]), 1e-9)
        fmt = lambda v: '%8s' % '-' if v is None else '%8.4f' % v
        print('%-18s %s %s %s %s %9.0f' % (an, fmt(r['strict']), fmt(r['neutral']), fmt(r['group']), fmt(r['form']), kbs) + (' %s %s' % (fmt(r['n25']), fmt(r['n25group'])) if std25 else ''))


# ---- 모호성 해소 (kiwipiepy benchmark/disambiguate 와 같은 채점) ----
def conv(an, f, t):
    t = map_tag(an, t) if an else t
    if an in GROUP_ONLY: return (norm_form(f), t)
    return (norm_form(f), t[:2] if t.startswith('V') else t[:1])


def disamb(dirp, ans, out_dir):
    sets = sorted(glob.glob(os.path.join(dirp, '*.txt')))
    print('%-20s' % '셋' + ''.join('%14s' % a for a in ans))
    tot = {a: [0, 0] for a in ans}
    for sp in sets:
        ds = []
        for l in open(sp, encoding='utf-8'):
            l = l.rstrip('\n')
            if not l: continue
            a, e = l.split('\t'); f, t = a.split('/'); ds.append((f, t))
        base = os.path.basename(sp).rsplit('.', 1)[0]
        row = []
        for an in ans:
            p = os.path.join(out_dir, an, base + '.txt')
            pred = open(p, encoding='utf-8').read().rstrip('\n').split('\n')
            assert len(pred) == len(ds), (an, base, len(pred), len(ds))
            n = c = 0
            for (f, t), pl in zip(ds, pred):
                if an in GROUP_ONLY and t.startswith('VA'): continue     # Kiwi 와 같이: 동/형 구별 못 하는 분석기는 VA 문항 제외
                ans_k = (f, t[:2] if t.startswith('V') else t[:1])
                if an in GROUP_ONLY: ans_k = (f, 'V' if t.startswith('V') else group(t))
                toks = set()
                for w in pl.split(' '):
                    if '/' not in w: continue
                    ff, tt = w.rsplit('/', 1)
                    if an in GROUP_ONLY: toks.add((norm_form(ff), map_tag(an, tt)))
                    else: toks.add(conv(an, ff, tt))
                n += 1; c += ans_k in toks
            row.append(c / n if n else None); tot[an][0] += c; tot[an][1] += n
        print('%-20s' % base + ''.join('%14s' % ('-' if v is None else '%.4f' % v) for v in row))
    print('%-20s' % '전체' + ''.join('%14s' % ('%.4f (%d)' % (v[0] / v[1], v[1]) if v[1] else '-') for v in tot.values()))


if __name__ == '__main__':
    main()
