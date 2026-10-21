#!/usr/bin/env python3
"""논문 A(madi: 순수 Rust 한국어 형태소 분석기와 관행 중립 비교 평가) 수치 재현 — 논문 판 모델 + 공개 판 madipy.

  python reproduce.py [--dir models-paper] [--kiwi510 DIR] [--analyze IN.txt OUT.txt]

하는 일:
  1. 논문 판 모델(`models-kword5` Release 의 네 파일)을 받아 sha256 을 확인하고 풉니다 (약 165 MB 받음, 308 MB 풀림).
     이미 있으면 다시 받지 않습니다.
  2. madipy(0.3.0 이상)를 논문 설정(점수 가중 rev3p, 전후향 가지치기 끔)으로 열고 엔진 판본 문자열이
     `…+decdb.r3p.f0.k838c.n15e6.s-` 인지 확인합니다. 이 문자열이 같으면 논문과 같은 사전·언어 모델·가중으로 돌고 있는 것입니다.
  3. (--kiwi510 DIR) Kiwi 모호성 평가 자료 510문항을 분석해 논문 표의 정확도(전체 0.7471: 원거리 0.6667 · 불규칙 0.7580 ·
     명사·조사 0.7443 · 동사·형용사 0.7609)를 다시 냅니다. DIR 은 kiwipiepy 저장소의 benchmark/disambiguate/testset 입니다.
     출력 네 파일의 md5 도 논문 때의 값과 맞춥니다.
  4. (--analyze IN OUT) 한 줄 한 문장인 파일을 분석해 `형태/태그 …` 꼴로 씁니다. 자기 정답 자료가 있으면 eval/score.py 로 채점합니다:
       python eval/score.py GOLD.tsv OUT   (GOLD.tsv: 문장<TAB>형태/태그 … ; 어절 사이는 ' | ')

설치:  pip install "madipy>=0.3.0"
"""
import argparse, hashlib, io, lzma, os, sys, urllib.request

TAG = 'models-kword5'
BASE = 'https://github.com/p14jeffwest/madi-release/releases/download/' + TAG + '/'
FILES = {  # 이름: (풀린 크기, 풀린 파일 sha256) — models-kword5 Release 와 같다
    'madi.dict': (102704960, '25cb2121ebf199043bc4ac684b85feb18702173998790c61acbbd2fc07157a48'),
    'knlm.bin': (101531360, 'd7a71256f25ccd6609c104f891852ea9ef1046964a9fb93cb2276e496e3e6c37'),
    'model.nlm': (36425846, '8c8e58897743eb976ae0ff286f72814ceebc8de99840e17a34c18854f838822d'),
    'precise.tlm': (37861142, 'c6d35a7f5514f3846673ed3c7544562832c5ee4dba0158b6a3956392b072369e'),
}
VERSION_TAIL = '+decdb.r3p.f0.k838c.n15e6.s-'
KIWI510 = {'distant': (26, 39, 'f714dc6a35507cdf09823e2ec03fa095'), 'irregular_verbs': (119, 157, '480873f76daee4848568a2999ec14cd2'),
           'nouns': (131, 176, '34740299ef20af654c7340f0b3c8a1cb'), 'verb_vs_adj': (105, 138, 'df10b0172b452dd4f65ac40e887e5341')}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def fetch(name, d):
    out = os.path.join(d, name)
    size, want = FILES[name]
    if os.path.exists(out) and os.path.getsize(out) == size:
        return out
    print(f'받는 중 {name}.xz …', flush=True)
    with urllib.request.urlopen(BASE + name + '.xz') as r:
        data = r.read()
    raw = lzma.decompress(data)
    with open(out, 'wb') as f:
        f.write(raw)
    return out


def check(d):
    ok = True
    for name, (size, want) in FILES.items():
        p = os.path.join(d, name)
        got = sha256(p)
        same = os.path.getsize(p) == size and got == want
        print(f'  {name:12s} {os.path.getsize(p):>11,d} B  sha256 {got[:16]}…  {"OK" if same else "!! 다름"}')
        ok &= same
    return ok


def open_analyzer(d):
    import madi
    a = madi.Analyzer(os.path.join(d, 'madi.dict'), lm=os.path.join(d, 'knlm.bin'), nlm=os.path.join(d, 'model.nlm'),
                      nlm_weight=0.3, score_preset='rev3p', fb_cutoff=0, tags='code')
    v = a.version
    print(f'엔진 판본: {v}  ({"논문 판과 같음" if v.endswith(VERSION_TAIL) else "!! 논문 판과 다름 — 기대: *" + VERSION_TAIL})')
    return a


def line(a, s):
    return ' '.join(f'{f}/{t}' for f, t, _, _ in a.tokenize(s))


def kiwi510(a, testset, outdir):
    """Kiwi 의 채점 방식 그대로: 정답 '형태/태그' 가 분석 결과에 있으면 맞음 (태그는 용언 VV·VA 는 두 글자, 그 밖은 첫 글자만 비교)."""
    os.makedirs(outdir, exist_ok=True)
    tot = [0, 0]
    for base, (want_ok, want_n, want_md5) in KIWI510.items():
        p = os.path.join(testset, base + '.txt')
        items = [l.rstrip('\n').split('\t') for l in open(p, encoding='utf-8') if l.strip()]
        outs, ok = [], 0
        for ans, s in items:
            f, t = ans.split('/')
            toks = [(x, y) for x, y, _, _ in a.tokenize(s)]
            outs.append(' '.join(f'{x}/{y}' for x, y in toks))
            key = t[:2] if t.startswith('V') else t[:1]
            ok += any(x == f and (y[:2] if y.startswith('V') else y[:1]) == key for x, y in toks)
        text = '\n'.join(outs) + '\n'
        open(os.path.join(outdir, base + '.txt'), 'w', encoding='utf-8', newline='\n').write(text)
        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        print(f'  {base:16s} {ok}/{len(items)} = {ok / len(items):.4f}  (논문 {want_ok}/{want_n} = {want_ok / want_n:.4f})  '
              f'출력 md5 {md5[:8]} {"OK" if md5 == want_md5 else "!! 논문 때와 다름"}')
        tot[0] += ok; tot[1] += len(items)
    print(f'  {"전체":16s} {tot[0]}/{tot[1]} = {tot[0] / tot[1]:.4f}  (논문 381/510 = 0.7471)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='models-paper', help='모델을 둘 폴더')
    ap.add_argument('--kiwi510', help='kiwipiepy/benchmark/disambiguate/testset 폴더')
    ap.add_argument('--analyze', nargs=2, metavar=('IN', 'OUT'), help='한 줄 한 문장 파일 → 형태/태그 출력')
    args = ap.parse_args()
    os.makedirs(args.dir, exist_ok=True)
    for name in FILES:
        fetch(name, args.dir)
    print('모델 파일:')
    if not check(args.dir):
        sys.exit('!! 모델 파일이 Release 와 다릅니다. 폴더를 지우고 다시 받으세요.')
    a = open_analyzer(args.dir)
    print('보기:', line(a, '나는 어제 학교에 갔다.'))
    if args.kiwi510:
        print('Kiwi 모호성 평가 자료 (510문항):')
        kiwi510(a, args.kiwi510, 'out-kiwi510')
    if args.analyze:
        src, dst = args.analyze
        with open(src, encoding='utf-8') as f, open(dst, 'w', encoding='utf-8', newline='\n') as g:
            for s in f:
                s = s.rstrip('\r\n')
                g.write((line(a, s) if s else '') + '\n')
        print(f'분석 결과: {dst}')


if __name__ == '__main__':
    main()
