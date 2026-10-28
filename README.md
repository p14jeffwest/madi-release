# madi (마디) — 배포 저장소

순수 Rust 로 만든 한국어 형태소 분석기 **madi** 의 공개 배포물(모델 파일, 설치 안내)을 두는 저장소입니다.

## 공개 범위
| 구분 | 무엇 | 어디 | 조건 |
|---|---|---|---|
| **공개하는 것** | 분석기 코드 `madi-core`·`madi-lm`·`madi`·`madi-cli`(+ 보조 `madi-news`·`madi-build`) | crates.io (소스 포함, 지금 0.3.0) | MIT OR Apache-2.0 |
| | Python 패키지 `madipy`(휠) | PyPI | MIT OR Apache-2.0 |
| | 모델·사전 파일(이 저장소 Release `models-kword6`(기본), `models-kword6-fast1`(fast·balanced 모드의 패턴 모델); 0.2.x 는 `models-kword5`), WASM 경량 모델 | GitHub Release | CC BY-SA 2.0 KR |
| **바이너리로만 제공하는 것** | 맞춤법 검사기(`madi-lsp` 실행 파일, VS Code 확장) | GitHub Release, VS Code 마켓 | 무료 이용 조건(확장의 `LICENSE.txt`) |
| **제공하지 않는 것** | 학습·평가 도구, 개발·평가 셋, 말뭉치 원문, 맞춤법 검사기 소스 | — | — |

## Python

```
pip install madipy          # import 는 madi
```
```python
import madi
m = madi.Analyzer()          # 처음 한 번 이 저장소의 Release 에서 모델을 받는다
m.pos('아버지가 방에 들어가신다')
f = madi.Analyzer(mode='fast')     # 빠른 모드 (0.4.0, 아래 '모드' 절)
```
자세한 사용법: https://pypi.org/project/madipy/ · 변경 기록: [CHANGELOG.md](CHANGELOG.md)

## Rust

```
cargo add madi               # 라이브러리 (Engine)
cargo install madi-cli       # 명령 `madi`
```
모델 파일은 아래 Release 에서 받아 경로를 줍니다(https://docs.rs/madi). Rust 크레이트(`madi`·`madi-cli`)의 crates.io 판은 아직 0.3.0 이라 fast·balanced 모드가 없습니다. 이 두 모드는 지금 Python 패키지(madipy 0.4.0)에서 씁니다.

## 모델 파일 (Release `models-kword6`, madi 0.3.0)

| 파일 | 내용 | 받기 | 풀면 |
|---|---|---|---|
| `madi.dict.xz` | 사전 (mecab-ko-dic 기반 + 확장) | 14.7 MB | 102.6 MB |
| `knlm.bin.xz` | 형태소 n-gram 언어모델 (KnLM, v2 형식) | 48.3 MB | 130.1 MB |
| `model.nlm.xz` | 신경망 언어모델 | 32.9 MB | 36.4 MB |
| `precise.tlm.xz` | 정밀 모드 교사 모델 | 28.0 MB | 37.9 MB |

Python 패키지가 받을 때 sha256 을 확인합니다. 손으로 받을 때의 sha256(풀린 파일):

```
1fa233b2b979b928c5303913373cab00c070abfac0ef656252bb338e86557c81  madi.dict
54bbccadab89ba8cfb0605cd829ce839aa43b33ae527600dd532204c08a71c2a  knlm.bin
c07db979e6d510b6484ee97ccacbced4380192d4aef5c47eec3a3bc6867e2ef5  model.nlm
83333f5f58504015113f1568eadbc3c98815d237be0d3e9113f925b522ee0919  precise.tlm
```

- kword6 는 개발용 문서를 모든 모델 입력에서 뺀 묶음입니다(사전 어휘·신경망 LM·교사를 문서 단위 학습 풀에서 다시 만듦 — [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md) §5).
- `knlm.bin` 은 v2 형식(완성된 해시 표를 그대로 메모리에 사상)이라 madi 0.3.0 이상이 읽습니다. 0.2.x 는 Release `models-kword5` 를 그대로 씁니다(그 Release 는 남겨 둡니다).

### 패턴 모델 (Release `models-kword6-fast1`, madi 0.4.0)

fast·balanced 모드가 씁니다. fast 는 `fast-rl.mfm` 하나만, balanced 는 위 기본 묶음에 두 파일을 더 씁니다.

| 파일 | 내용 | 받기 | 풀면 |
|---|---|---|---|
| `fast-rl.mfm.xz` | 패턴 모델 (오른쪽→왼쪽) | 12.9 MB | 38.1 MB |
| `fast-lr.mfm.xz` | 패턴 모델 (왼쪽→오른쪽) | 13.3 MB | 39.2 MB |

```
f8171847599e92a01d637df1cde7c2690dece8bdb512710e13fd95b5306877dd  fast-rl.mfm
71d05b27a53e541f7d8cdee2317123782a4a5b2b0f9336cac166c9db3d03bcda  fast-lr.mfm
```

- 학습 입력은 형태 분석 말뭉치 v1.1 학습 풀과 kword6 사전 항목뿐입니다. 말뭉치 문장을 담거나 문장을 복원할 수 있는 형태가 아닙니다([MODEL-PROVENANCE.md](MODEL-PROVENANCE.md) §6).

### 모델 이용 조건
모델·사전 파일은 CC BY-SA 2.0 KR. 국립국어원 모두의 말뭉치(형태 분석 말뭉치 2018~2020, 형태 분석 말뭉치 2025, 어휘 의미 분석 말뭉치 2020)와 우리말샘을 활용하였음(국립국어원 공개 승인 2026-10-14). 말뭉치 원문을 담거나 복원할 수 없는 통계·가중치임. 신문 기사 원문으로 자기 라벨 학습.
- 사전은 mecab-ko-dic(Apache-2.0)을 바탕으로 합니다. 표준국어대사전(국립국어원, CC BY-SA 2.0 KR) 표제어·품사를 사전 어휘 확인에 활용했습니다.
- 전문과 출처 표시 예: `LICENSE-MODELS.txt`(Release 에 함께 있음). 학습 입력 목록: [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md).
- 학습 말뭉치 원문은 포함하지 않습니다.
- 패턴 모델(`models-kword6-fast1`)은 형태 분석 말뭉치 2018~2020 만 활용하였고, 사전 항목(씨앗)의 출처와 조건은 `models-kword6` 의 `madi.dict` 와 같습니다.

## 성능 요약 (madi 0.3.0 공개판, 2026-10-21)

같은 잣대(세종 태그 사상, 관행 차이 정규화)로 다른 분석기와 비교했습니다. 차이는 Kiwi CoNg(kiwipiepy 0.24.0) 대비, 괄호는 95% 구간입니다. madi 는 공개판 기본 설정(4p 가중, 전후향 가지치기 11) 그대로입니다.

| | madi 기본 | madi 정밀 | Kiwi CoNg |
|---|---|---|---|
| 모두의 말뭉치 형태 분석 2025 문어(학습과 독립, 6,953문장), 형태소 F1 (%) | **97.72%**<br>(+0.30p [+0.22, +0.38]) | 97.85%<br>(+0.43p) | 97.42% |
| 같은 셋 구어(16,439문장) | **96.44%**<br>(+0.58p [+0.48, +0.68]) | 96.59%<br>(+0.73p) | 95.86% |
| 신문 1990~2025 평가셋(420문장, 손 교정), 중립 F1 (%) | 97.72%<br>(+0.35p, 유의하지 않음) | 97.92%<br>(+0.55p [+0.15, +0.95]) | 97.37% |
| Kiwi 모호성 벤치마크 kiwi510, 정확도 (%) | 75.88%<br>(**열세**, p 0.0013) | 81.37%<br>(차이 유의하지 않음) | 82.75% |

- 기본 모드는 모호성 벤치마크에서 Kiwi 보다 낮고, 정밀 모드(`precise=True`)는 같은 수준입니다. 일반 문장의 형태소 F1 은 기본 모드도 앞섭니다.
- 0.2.x(kword5)와 비교하면 일반 문장 F1 은 같은 수준(문어 −0.02p, 구어 +0.04p, 신문 같음)이고 kiwi510 기본이 +1.2p 입니다. 0.2.x 의 수치는 논문 판(전후향 가지치기 끔, fb 0)으로 남깁니다.
- MP 2025 문어는 홀수 번째 문장으로 평가했고, 같은 기사의 짝수 번째 문장은 점수 가중 학습에 썼습니다(0.2.x 와 같은 조건).
- 속도·메모리는 소개 페이지의 표를 보세요. 0.3.0 은 KnLM 을 읽을 때 복사·삽입이 없어 시작이 약 0.3초 빠르고 메모리를 약 90 MB 덜 씁니다.
- 자세한 표·방법은 논문(준비 중)에 싣습니다. 평가에는 국립국어원 모두의 말뭉치를 활용하였음.

## 모드 (madipy 0.4.0)

Rust 크레이트(`madi`·`madi-cli`)의 crates.io 판은 아직 0.3.0 이라 fast·balanced 모드가 없습니다. 이 두 모드는 지금 Python 패키지(madipy 0.4.0)에서 씁니다.

| 모드 | 만드는 법 | 무엇이 다른가 | 신문 420 F1 (%) | 속도 (MB/s) | 메모리 (MB) | 받는 파일 |
|---|---|---|---|---|---|---|
| **fast** | `madi.Analyzer(mode='fast')` | 패턴 모델 하나로만 분석 (사전·언어 모델 없음) | 95.03 | 8.02 | 36 | 13 MB |
| **balanced** | `madi.Analyzer(mode='balanced')` | 두 방향 패턴 분석이 어긋난 어절만 기본 분석으로 다시 분석 | 97.05 | 1.06 | 429 | 96 + 26 MB |
| **기본** | `madi.Analyzer()` | 사전 + n-gram 언어 모델 + 신경망 언어 모델 | 97.33 | 0.30 | 399 | 96 MB |
| **n-gram만** (`nlm=False`) | `madi.Analyzer(nlm=False)` | 신경망 언어 모델 없이 n-gram 만 | 97.04 | 0.38 | 249 | 63 MB |
| **정밀** | `madi.Analyzer(precise=True)` | 기본 결과 가운데 애매한 어절을 작은 교사 모델이 다시 채점 | 97.46 | 0.025 | 461 | 96 + 28 MB |

(노트북 1스레드, 명령줄 분석기, 모델 읽기 시간을 뺀 분석 속도(신문 1 MB), 0.4.0 판 2026-10 측정. 신문 420 은 신문 1990~2025 평가셋 420문장, 엄격 잣대. 받는 파일은 압축된 크기.)

- fast 는 기본 모드보다 약 2%p 낮은 정확도로 약 27배 빠릅니다. balanced 는 `nlm=False` 와 같은 정확도로 그보다 2~3배(기본 모드보다 2.5~3.5배) 빠릅니다(메모리·받는 파일은 기본 모드보다 조금 큽니다).
- fast·balanced 에서는 사용자 사전·한자 독음·정밀 모드·출력 옵션을 쓸 수 없습니다(만들 때 오류). 여러 후보는 하나(점수 NaN)만 돌려줍니다.
- 끝 부호 없이 이어 쓴 글(메신저·댓글 등)을 문장으로 나눌 때는 기본 모드가 낫습니다. fast 는 그런 글에서 문장 끝을 덜 찾고, balanced 도 조금 덜 찾습니다.
- 판본 문자열이 같으면 같은 입력에 같은 결과(1-best)를 냅니다. 신경망 언어 모델을 쓰는 여러 후보(`top_n` > 1)의 점수와 동점 순서는 CPU 에 따라 다를 수 있습니다.
- 위 성능 요약의 기본·정밀 값은 0.3.0 공개판 측정이며, 0.4.0 기본 모드의 출력은 0.3.0 과 같습니다.

## 코드 라이선스
분석기 코드는 MIT 또는 Apache-2.0 중 택일입니다.
