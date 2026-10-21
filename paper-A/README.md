# 논문 A 재현 묶음 (paper-A)

논문 **"madi: 순수 Rust 한국어 형태소 분석기와 관행 중립 비교 평가"** 의 수치를 낸 분석기 판(이하 **논문 판**)을 그대로 돌리기 위한 것입니다. 공개 판(madi 0.3.0, 모델 `models-kword6`)은 논문 판 이후 사전·언어 모델·가중치를 다시 학습한 판이라 출력이 조금 다릅니다. 논문 판은 공개 판 바이너리에 논문 판 모델과 옵션 둘을 주면 그대로 됩니다 — 새 바이너리는 필요 없습니다.

## 논문 판 = 공개 바이너리 0.3.0 + 모델 `models-kword5` + 옵션 둘

| | 값 |
|---|---|
| 분석기 | madi **0.3.0** (`pip install madipy==0.3.0` 또는 `cargo install madi-cli --version 0.3.0`). 0.2.1·0.2.2 도 같은 결과 |
| 모델 | Release [`models-kword5`](https://github.com/p14jeffwest/madi-release/releases/tag/models-kword5) 의 네 파일 (아래 표) |
| 옵션 | 점수 가중 **rev3p**, 전후향 가지치기 **끔** — CLI `--score-preset rev3p --fb-cutoff 0`, Python `score_preset='rev3p', fb_cutoff=0` |
| 엔진 판본 문자열 | CLI `0.3.0+decdb.r3p.f0.k838c.n15e6.s0968`, Python `0.3.0+decdb.r3p.f0.k838c.n15e6.s-` (`madi version …` / `Analyzer.version`). 머리의 판 번호만 다르고 `+` 뒤가 같으면 같은 모델·가중입니다 |
| 정밀 모드 | `--precise --tlm precise.tlm` (τ 2.0 · λ 0.3 기본값), Python `precise='precise.tlm'` |
| 두 언어 모델 가중 | KnLM 0.7 · NLM 0.3 (기본값) |

| 파일 | 풀면 | sha256 (풀린 파일) |
|---|---|---|
| `madi.dict` (사전 decdb) | 102,704,960 B | `25cb2121ebf199043bc4ac684b85feb18702173998790c61acbbd2fc07157a48` |
| `knlm.bin` (KnLM K2a, v1 형식) | 101,531,360 B | `d7a71256f25ccd6609c104f891852ea9ef1046964a9fb93cb2276e496e3e6c37` |
| `model.nlm` (신경망 LM) | 36,425,846 B | `8c8e58897743eb976ae0ff286f72814ceebc8de99840e17a34c18854f838822d` |
| `precise.tlm` (정밀 모드 교사 384×6) | 37,861,142 B | `c6d35a7f5514f3846673ed3c7544562832c5ee4dba0158b6a3956392b072369e` |

공개 판 0.3.0 바이너리가 이 설정으로 논문 때의 출력(신문 420문장·모두의 말뭉치 2025 문어 1,000문장)을 바이트까지 같게 내는 것을 0.3.0 공개 전에 확인했습니다.

## 빠른 재현 — `reproduce.py`

```
pip install "madipy>=0.3.0"
python reproduce.py                       # 모델 받기(165 MB) + sha256 확인 + 엔진 판본 문자열 확인
python reproduce.py --kiwi510 testset     # Kiwi 모호성 평가 자료 510문항 → 논문 표의 0.7471 (하위 셋 넷) 과 출력 md5 대조
python reproduce.py --analyze in.txt out.txt   # 한 줄 한 문장 → 형태/태그
```

`testset` 은 [kiwipiepy 저장소](https://github.com/bab2min/kiwipiepy) 의 `benchmark/disambiguate/testset` 폴더입니다(원거리 39 · 불규칙 157 · 명사·조사 176 · 동사·형용사 138).

## 채점기 — `eval/`

논문 4.2절(표 2)의 엄격·중립·중립25 잣대를 구현한 채점기입니다. 말뭉치 원문은 담고 있지 않습니다.

- `eval/score.py GOLD.tsv A1 [A2 …]` — 형태소 F1(엄격·중립·묶음·분절). `--std25` 를 주면 중립25 도. `--odd` 는 홀수 번째 문장만.
  정답 `GOLD.tsv` 는 `문장<TAB>형태/태그 형태/태그 | 형태/태그 …`(어절 사이 ` | `), 분석기 출력은 한 줄 한 문장 `형태/태그 …` 로, `out/compare/<분석기>/<GOLD 이름>.txt` 에 둡니다(`--out` 으로 바꿀 수 있음).
- `eval/score.py --disamb DIR A1 …` — Kiwi 모호성 평가 자료의 채점(Kiwi 와 같은 규칙).
- `eval/stats.py f1 GOLD.tsv REF A1 …` — 문장 단위 재표집 2,000회의 95% 구간과 REF 대비 차이 구간. `stats.py disamb DIR REF A1 …` — 문항 정확도 구간과 McNemar 정확 검정.
- `eval/neutral25.py` — 중립25 변환(2019·2025 지침 차이). `eval/vowel_map.json` — 아/어 이형태 표.

다른 분석기(Kiwi·mecab-ko·Khaiii·KoNLPy)의 태그 사상은 `score.py` 안의 `map_tag` 에 있습니다.

## 평가 자료
- **신문 420**, **모두의 말뭉치 2025**, **modu-amb**, **arg-amb** 는 말뭉치 원문을 담고 있어 공개하지 않습니다(논문 4.6절). 모두의 말뭉치 이용 승인을 받은 연구자에게는 문장 식별자와 어절 위치를 요청 시 제공합니다.
- **Kiwi 모호성 평가 자료**는 공개 자료라 위 `reproduce.py --kiwi510` 으로 논문 표의 수치가 그대로 나옵니다.

## 공개 판(0.3.0, kword6)과의 차이
같은 잣대로 두 판을 재면 독립 셋에서는 같거나 공개 판이 조금 높고, 개발 셋 원천의 모호 어절 셋에서는 논문 판이 조금 높습니다(논문 판의 사전·신경망 LM·교사가 개발 셋 문서를 학습에서 본 몫 — 논문 6.1절; 공개 판은 개발 셋이 사전·신경망 LM·교사 모두에서 독립입니다).

| 셋 (잣대) | 논문 판 | 공개 판 0.3.0 |
|---|---|---|
| 신문 420 F1 (엄격 / 중립) | 0.9736 / 0.9772 | 0.9733 / 0.9772 |
| 모두의 말뭉치 2025 문어, 홀수 반쪽 (중립25) | 0.9774 | 0.9772 |
| 모두의 말뭉치 2025 구어 (중립25) | 0.9640 | 0.9644 |
| Kiwi 모호성 평가 자료 510 | 0.7471 | 0.7588 |
| modu-amb 동형 대립 1,634 (엄격 / 중립) | 0.8641 / 0.8647 | 0.8635 / 0.8641 |
| arg-amb 1,302 | 0.9040 | 0.9025 |

## 이용 조건
코드(`reproduce.py`, `eval/`)는 MIT 또는 Apache-2.0. 모델 파일은 CC BY-SA 2.0 KR — 국립국어원 모두의 말뭉치·우리말샘 활용(`LICENSE-MODELS.txt`, `MODEL-PROVENANCE.md`).
