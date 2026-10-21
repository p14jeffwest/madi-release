#!/usr/bin/env python3
"""중립 잣대의 2018↔2025 지침 항목 (평가 2차 §1.3, 2026-10-13).

MP 2025(nx2023·sx2023) 정답은 2025 지침(통째 용언·명사 연쇄·인용 JKQ …), 다른 분석기는 2018 관행이다.
양쪽에 같은 변환 `canon25` 를 해서 **지침 차이만** 지운다 (score.neutral 다음에 적용; 명사 연쇄 ④ 는 neutral 이 이미 함).
방향은 '합치는 쪽'(두 관행 중 토큰이 적은 쪽)을 기본으로 하고, 합칠 수 없는 것(이라/JKQ ↔ 이/VCP 라)은 2018 쪽으로 가른다.
항목 (madi 의 2018→2025 변환 `convert_2025`(6.F) 에서 '태그·분절 관행'만 골라 옮김):
  A 체언·어근·부사(다·더·잘·함께) + 하/XSV·XSA·VV, 되/XSV, 받/XSV, 시키/XSV, 당하/XSV → 통째 용언 (말하/VV, 다양하/VA, 진행되/VV)
  B 명사 + 적·성·화·형·별·용·상·간·급/XSN, 접두사 + 명사, 명사 + 숫자 → 명사 연쇄에 넣음 (지속적, 비대면, 코로나19)
  C 인용·관형: X/EF 고/JKQ → X고/EC (더라/EF 고/JKQ 와 더라고/EF 도 X고/EC 로), X/EF 는/ETM → X는/ETM, X/EF 며/EC → X며/EC
  K '_' 다단어 단위는 갈라 같은 태그로, L 홑따옴표·《》 안(제목)은 한 토큰, M 로마자·숫자 사이 - & + . / 잇기, 로마자·숫자도 명사 연쇄에 (D램, T1, 808베이스) — 10.13 검토 §2-1 표본 분류 뒤
  N (2차 표본 뒤) 명사·숫자 + 단위 의존명사(계묘년·인가일·1무; 문법 의존명사 제외) → 명사 연쇄, 명사·명사 가운데점 잇기, 인용 X/EF + 는데·는지 잇기, 제목 안은 '□' 로 비교 안 함
  O 용언 + 아/어/EC + 지/VX → 통째 '-어지' 용언(흔한 축약만: 강하+아+지 → 강해지)
  J (분석기 관행, 2025 셋에서 크게 보여 함께) 종결 어미 + 요/JX → X요/EF (거든/EF 요/JX ↔ 거든요/EF), 이렇게·그렇게·어떻게/MAG → X/VA 게/EC
  D 이라/JKQ·라/JKQ → 이/VCP 라/EC 꼴로 가름 (이라며 = 이/VCP 라며/EC, 이라고 = 이/VCP 라고/EC)
  E 번/NNB 째/XSN → 번째/NNB, 수 + 월/NNB → N월/NN
  F 게·어야·아야 뒤의 되/VV·VX → 되/VX
  G 두 글자 이상 로마자 단어: SL·NNG·NNP → 명사 연쇄 (2025 는 NNG/NNP, 2018 은 SL)
  H ㅂ 불규칙 어간 뒤 은·을·음 ↔ ㄴ·ㄹ·ㅁ → ㄴ·ㄹ·ㅁ (madi 2018 은 ㄴ, 2025 정답은 은, Kiwi 는 은)
  I 표기: MP 2025 원문의 다단어 표지 '_' 를 정답 형태에서 지움(입력 문장은 '_' → 공백), 따옴표 모양, 준말 조사(ㄹ/JKO·ㄴ/JX),
    표면형 대명사(내·네·제 → 나·너·저, 그거·이거 → 그것·이것), 이/VCP 는 양쪽에서 지움(2025 는 표면에 '이' 가 없으면 VCP 를 안 씀)
  A' 명사(연쇄) 바로 뒤의 파생 용언은 명사째 (압수수색하/VV) — 명사 연쇄 ④ 처럼 공백을 보지 않는다(분석기 출력에 어절 경계가 없음)
"""
import re

NUMX = re.compile(r'^[0-9][0-9.,]*[0-9]$|^[0-9]$')
RE_LAT2 = re.compile(r'^[A-Za-zＡ-Ｚａ-ｚ][A-Za-zＡ-Ｚａ-ｚ]+$')
NOUN = {'NNG', 'NNP', 'NN'}
ADV_HA = {'다', '더', '잘', '함께', '못', '안'}
XSN_JOIN = {'적', '성', '화', '형', '별', '용', '상', '간', '급', '권', '자', '계', '력', '감', '제', '식', '률', '율'}
VSUF = {('하', 'XSV'): 'VV', ('하', 'XSA'): 'VA', ('되', 'XSV'): 'VV', ('받', 'XSV'): 'VV', ('시키', 'XSV'): 'VV', ('당하', 'XSV'): 'VV',
        ('하', 'VV'): 'VV', ('되', 'VV'): 'VV'}
QUOTE_EF = {'다', '라', 'ㄴ다', '는다', '자', '냐', '느냐', '으냐', '으라', '니', '요', '래', '대', '더라', '았다', '었다', '겠다', 'ㄴ다더라'}
GE_ADV = {'이렇게': '이렇', '그렇게': '그렇', '저렇게': '저렇', '어떻게': '어떻'}


def b_irregular(stem):
    # ㅂ 받침이 빠진 꼴인지: 정답(2025)은 '무덥/VA 은/ETM', madi 2018 은 '무덥/VA ㄴ/ETM' — 어간 끝이 ㅂ 받침이면 같게 본다
    c = stem[-1:]
    return bool(c) and 0xAC00 <= ord(c) <= 0xD7A3 and (ord(c) - 0xAC00) % 28 == 17


QUOTE_FORM = {'‘': "'", '’': "'", '“': '"', '”': '"', '＂': '"', '＇': "'"}
PRON = {('내', 'NP'): '나', ('네', 'NP'): '너', ('제', 'NP'): '저', ('그거', 'NP'): '그것', ('이거', 'NP'): '이것', ('저거', 'NP'): '저것', ('그게', 'NP'): '그것', ('이게', 'NP'): '이것'}
CONTR = {('ㄹ', 'JKO'): '를', ('ㄴ', 'JX'): '는'}
VSUF.update({('스럽', 'XSA'): 'VA', ('롭', 'XSA'): 'VA', ('답', 'XSA'): 'VA', ('드리', 'VV'): 'VV', ('드리', 'XSV'): 'VV', ('되', 'XSA'): 'VA'})


TITLE_OPEN = {"'": "'", '‘': '’', '「': '」', '『': '』', '《': '》', '〈': '〉', '<': '>'}
TITLE_CLOSE = {"'", '’', '」', '』', '》', '〉', '>'}
GRAM_NNB = {'것', '수', '거', '줄', '데', '바', '듯', '뿐', '때문', '만큼', '대로', '채', '척', '지', '터', '리', '등', '중', '간', '번', '적', '분', '이', '년', '월', '일'}
JOIN_SYM = {'-', '&', '+', '.', '/', '十'}


def eo_join(stem, e):
    """어간 + 아/어 의 흔한 축약 (하+아 → 해, 리+어 → 려, 크+어 → 커, 오+아 → 와, 우+어 → 워, 받침 있으면 그대로 이음)"""
    c = stem[-1:]
    if not c or not (0xAC00 <= ord(c) <= 0xD7A3):
        return stem + e
    o = ord(c) - 0xAC00; cho, jung, jong = o // 588, (o % 588) // 28, o % 28
    if jong:
        return stem + ('아' if e == '여' else e)
    if c == '하': return stem[:-1] + '해'
    m = {20: 6, 18: 4, 8: 9, 13: 14, 0: 0, 4: 4}     # ㅣ→ㅕ, ㅡ→ㅓ, ㅗ→ㅘ, ㅜ→ㅝ, ㅏ·ㅓ 그대로
    if jung in m:
        return stem[:-1] + chr(0xAC00 + cho * 588 + m[jung] * 28)
    return stem + e


def canon25(toks):
    # K '_' 다단어 단위(정답의 사업_분야/NNG, 좀_더/MAG)는 '_' 에서 갈라 같은 태그로 (입력은 '_' → 공백이라 분석기는 따로 낸다) — 10.13 검토 §2-1
    tk = []
    for f, t in toks:
        if '_' in f and f.strip('_'):
            tk += [(x, t) for x in f.split('_') if x]
        else:
            tk.append((f, t))
    toks = tk
    # L 홑낫표·홑따옴표·꺾쇠 안(제목·이름: '3일의 휴가', 《…》)은 한 토큰으로 — 2025 는 제목을 통째 명사로 적는 일이 많다 (12토큰 이하만)
    tq, k = [], 0
    while k < len(toks):
        f, t = toks[k]
        if f in TITLE_OPEN and t.startswith('S'):
            close = TITLE_OPEN[f]
            j = next((j for j in range(k + 1, min(len(toks), k + 14)) if toks[j][0] in TITLE_CLOSE and toks[j][1].startswith('S')), None)
            if j is not None and j - k - 1 >= 1:
                tq.append((f, 'SS')); tq.append(('□', 'NN')); tq.append((toks[j][0], 'SS')); k = j + 1; continue   # 안의 형태는 비교하지 않음(정답은 표면, 분석기는 원형이라)
        tq.append((f, t)); k += 1
    toks = tq
    # M 로마자·숫자 사이의 - & + . / 는 잇는다 (T-50, M&A, n.SSign)
    tm = []
    for f, t in toks:
        if len(tm) >= 2 and tm[-1][0] in JOIN_SYM and tm[-1][1].startswith('S') and t in ('SL', 'SN', 'NN', 'NNG', 'NNP') and tm[-2][1] in ('SL', 'SN', 'NN', 'NNG', 'NNP') \
                and (re.match(r'^[A-Za-z0-9]', f) or re.search(r'[A-Za-z0-9]$', tm[-2][0])):
            sep = tm.pop(); q = tm.pop(); tm.append((q[0] + sep[0] + f, 'NN')); continue
        if t.startswith('S') and re.match(r'^[A-Za-z0-9][A-Za-z0-9&+.\-/]*[A-Za-z0-9]$', f) and not NUMX.match(f):
            t = 'NN'                                  # 11-10, R&D, 2022/23 (SL·SW·NN 로 갈리는 것을 한 부류로)
        tm.append((f, t))
    toks = tm
    # 숫자 잇기 (score.neutral ① 과 같음 — 명사+숫자 잇기 전에)
    tn = []
    for f, t in toks:
        if tn and len(tn) >= 2 and NUMX.match(f) and tn[-1][0] in ('.', ',') and NUMX.match(tn[-2][0]):
            sep = tn.pop(); q = tn.pop(); tn.append((q[0] + sep[0] + f, 'SN')); continue
        tn.append((f, t))
    toks = tn
    # 0 표기: 묶음 표지 '_' (MP 2025 원문의 다단어 표지 — 입력에서는 공백으로 바꿔 넣는다), 따옴표 모양, 준말 조사·대명사, 이/VCP 지움
    t00 = []
    for f, t in toks:
        if '_' in f:
            f = f.replace('_', '')
            if not f: continue
        if t == 'SS': f = ''.join(QUOTE_FORM.get(c, c) for c in f)
        f = PRON.get((f, t), f); f = CONTR.get((f, t), f)
        if t == 'VCP' and f == '이': continue          # 2025 는 표면에 '이' 가 없으면 VCP 를 안 씀 → 양쪽에서 지움
        t00.append((f, t))
    toks = t00
    # D: 이라/JKQ·라/JKQ 가르기 (이 는 VCP 라 위에서처럼 지움)
    t0 = []
    for f, t in toks:
        if t == 'JKQ' and f in ('이라', '이라고', '라', '라고'):
            t0.append((f.lstrip('이'), 'EC'))
            continue
        t0.append((f, t))
    # C: 인용 어미 잇기 (+ J: 종결 어미 + 요/JX 잇기, 이렇게/MAG 가르기 — Kiwi 관행)
    t1 = []
    for f, t in t0:
        if t == 'MAG' and f in GE_ADV:
            t1 += [(GE_ADV[f], 'VA'), ('게', 'EC')]; continue
        if t1 and t == 'JX' and f == '요' and t1[-1][1] == 'EF':
            t1[-1] = (t1[-1][0] + '요', 'EF'); continue
        if t == 'EF' and f.endswith('고') and f[:-1] in QUOTE_EF:
            t1.append((f, 'EC')); continue
        if t1:
            pf, pt = t1[-1]
            if pt in ('EF', 'EC') and (pf in QUOTE_EF or pf in ('라', '이라')) and ((t == 'JKQ' and f == '고') or (t == 'EC' and f in ('며', '면서', '고'))):
                t1[-1] = (pf + f, 'EC'); continue
            if pt == 'EF' and pf in QUOTE_EF and t == 'EC' and f in ('는데', '는지', '니까'):
                t1[-1] = (pf + f, 'EC'); continue
            if pt in ('EF', 'EC') and (pf in QUOTE_EF or pf == '라') and t == 'ETM' and f in ('는', 'ㄴ'):
                t1[-1] = (pf + f if f == '는' else {'라': '란', '다': '단', '자': '잔', '냐': '냔'}.get(pf, pf + f), 'ETM'); continue
        t1.append((f, t))
    # F 되/VX, H ㅂ 불규칙, E 번째·N월
    t2 = []
    for f, t in t1:
        if f == '되' and t in ('VV', 'VX') and t2 and t2[-1][1] == 'EC' and t2[-1][0] in ('게', '어야', '아야', '여야'):
            t = 'VX'
        if f == '째' and t == 'XSN' and t2 and t2[-1] == ('번', 'NNB'):
            t2[-1] = ('번째', 'NNB'); continue
        if f == '월' and t in ('NNB', 'NNG') and t2 and t2[-1][1] in ('SN', 'NR'):
            p = t2.pop(); t2.append((p[0] + f, 'NN')); continue
        t2.append((f, t))
    # O 용언 + 아/어/EC + 지/VX → 통째 '-어지-' 용언 (Kiwi 는 가르고 2025 정답은 강해지/VV·밝혀지/VV) — 흔한 축약만 되살린다
    tO = []
    for f, t in t2:
        if f == '지' and t == 'VX' and len(tO) >= 2 and tO[-1][1] == 'EC' and tO[-1][0] in ('아', '어', '여') and tO[-2][1] in ('VV', 'VA', 'XSV', 'XSA'):
            e = tO.pop(); st = tO.pop()
            tO.append((eo_join(st[0], e[0]) + '지', 'VV')); continue
        tO.append((f, t))
    t2 = tO
    # B0 접미사·접두사를 명사에 먼저 붙인다 (최소/NNG 화/XSN 하/XSV ↔ 최소화하/VV, 불/XPN 가능/NNG 하/XSA ↔ 불가능하/VA)
    tB = []
    for f, t in t2:
        if t in NOUN: t = 'NN'
        if tB:
            pf, pt = tB[-1]
            if (pt in ('NN', 'NNB') and t == 'XSN' and f != '들') or (pt == 'XPN' and t == 'NN') or \
               (pt in ('NN', 'SN') and t == 'NNB' and f not in GRAM_NNB):
                tB[-1] = (pf + f, 'NN'); continue
            if len(tB) >= 2 and pt == 'SP' and pf == '·' and tB[-2][1] == 'NN' and t == 'NN':
                tB.pop(); q = tB.pop(); tB.append((q[0] + '·' + f, 'NN')); continue
        tB.append((f, t))
    t2 = tB
    # A 통째 용언: 명사(연쇄)·어근·의존명사(것·수 제외) + 하/되/받/시키/당하/스럽/롭/답/드리, 부사 + 파생 접미사, 다/더/잘/함께 + 하/VV, 접두사 + 용언
    tA = []
    for f, t in t2:
        if t in NOUN: t = 'NN'
        if tA:
            pf, pt = tA[-1]
            v = VSUF.get((f, t))
            if v:
                if (pt == 'NN' or pt == 'XR' or (pt == 'NNB' and pf not in ('것', '수', '거'))) and t != 'VV' or \
                   (pt == 'NN' and f in ('드리', '하', '되') and t == 'VV' and False) or \
                   (pt == 'MAG' and t in ('XSV', 'XSA')) or (pt == 'MAG' and pf in ADV_HA and t == 'VV' and f == '하') or \
                   (pt == 'NN' and (f, t) == ('드리', 'VV')):
                    tA[-1] = (pf + f, v); continue
            if pt == 'XPN' and t in ('VV', 'VA'):
                tA[-1] = (pf + f, t); continue
        tA.append((f, t))
    # A' 명사(연쇄) 바로 뒤의 파생 용언은 명사째 (2025: 압수수색하/VV·지속가능하/VA; 띄어 쓴 '적극 지원하' 도 같게 — 명사 연쇄 ④ 처럼 공백을 보지 않는다)
    VEND = ('하', '되', '받', '시키', '당하', '스럽', '롭', '답', '드리')
    tA2 = []
    for f, t in tA:
        if t in ('VV', 'VA') and f.endswith(VEND) and tA2 and tA2[-1][1] == 'NN':
            p = tA2.pop()
            while tA2 and tA2[-1][1] == 'NN':
                p = (tA2.pop()[0] + p[0], 'NN')
            tA2.append((p[0] + f, t)); continue
        tA2.append((f, t))
    tA = tA2
    # H ㅂ 불규칙 어간(통째 용언을 만든 뒤 — 다채/XR 롭/XSA 은/ETM 도) 뒤 은·을·음 → ㄴ·ㄹ·ㅁ
    for i in range(1, len(tA)):
        f, t = tA[i]
        if t in ('ETM', 'ETN') and f in ('은', '을', '음') and tA[i - 1][1] in ('VA', 'VV', 'XSA') and b_irregular(tA[i - 1][0]):
            tA[i] = ({'은': 'ㄴ', '을': 'ㄹ', '음': 'ㅁ'}[f], t)
    # B·G 명사 연쇄 넓히기
    t4 = []
    for f, t in tA:
        if t == 'SL' and RE_LAT2.match(f): t = 'NN'
        if t in NOUN: t = 'NN'
        if t4:
            pf, pt = t4[-1]
            if (pt == 'NN' and (t == 'NN' or (t == 'XSN' and f != '들') or t == 'SN' or t == 'SL')) or (pt in ('SL', 'SN') and t == 'NN'):
                t4[-1] = (pf + f, 'NN'); continue
            if pt == 'XPN' and t == 'NN':
                t4[-1] = (pf + f, 'NN'); continue
        t4.append((f, t))
    return t4
