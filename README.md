# madi (마디) — 배포 저장소

순수 Rust 로 만든 한국어 형태소 분석기 **madi** 의 공개 배포물(모델 파일, 설치 안내)을 두는 저장소입니다.

## 공개 범위
| 구분 | 무엇 | 어디 | 조건 |
|---|---|---|---|
| **공개하는 것** | 분석기 코드 `madi-core`·`madi-lm`·`madi`·`madi-cli`(+ 보조 `madi-news`·`madi-build`) | crates.io (소스 포함) | MIT OR Apache-2.0 |
| | Python 패키지 `madipy`(휠) | PyPI | MIT OR Apache-2.0 |
| | 모델·사전 파일(이 저장소 Release `models-kword6`; 0.2.x 는 `models-kword5`), WASM 경량 모델 | GitHub Release | CC BY-SA 2.0 KR |
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
```
자세한 사용법: https://pypi.org/project/madipy/

## Rust

```
cargo add madi               # 라이브러리 (Engine)
cargo install madi-cli       # 명령 `madi`
```
모델 파일은 아래 Release 에서 받아 경로를 줍니다(https://docs.rs/madi).

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

### 모델 이용 조건
모델·사전 파일은 CC BY-SA 2.0 KR. 국립국어원 모두의 말뭉치(형태 분석 말뭉치 2018~2020, 형태 분석 말뭉치 2025, 어휘 의미 분석 말뭉치 2020)와 우리말샘을 활용하였음(국립국어원 공개 승인 2026-10-17). 말뭉치 원문을 담거나 복원할 수 없는 통계·가중치임. 신문 기사 원문으로 자기 라벨 학습.
- 사전은 mecab-ko-dic(Apache-2.0)을 바탕으로 합니다. 표준국어대사전(국립국어원, CC BY-SA 2.0 KR) 표제어·품사를 사전 어휘 확인에 활용했습니다.
- 전문과 출처 표시 예: `LICENSE-MODELS.txt`(Release 에 함께 있음). 학습 입력 목록: [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md).
- 학습 말뭉치 원문은 포함하지 않습니다.

## 성능 요약 (madi 0.3.0 공개판, 2026-10-21)

같은 잣대(세종 태그 사상, 관행 차이 정규화)로 다른 분석기와 비교했습니다. 차이는 Kiwi CoNg(kiwipiepy 0.24.0) 대비, 괄호는 95% 구간입니다. madi 는 공개판 기본 설정(4p 가중, 전후향 가지치기 11) 그대로입니다.

| | madi 기본 | madi 정밀 | Kiwi CoNg |
|---|---|---|---|
| 모두의 말뭉치 형태 분석 2025 문어(학습과 독립, 6,953문장), 형태소 F1 | **0.9772** (+0.30p [+0.22, +0.38]) | 0.9785 (+0.43p) | 0.9742 |
| 같은 셋 구어(16,439문장) | **0.9644** (+0.58p [+0.48, +0.68]) | 0.9659 (+0.73p) | 0.9586 |
| 신문 1990~2025 평가셋(420문장, 손 교정), 중립 F1 | 0.9772 (+0.35p, 유의하지 않음) | 0.9792 (+0.55p [+0.15, +0.95]) | 0.9737 |
| Kiwi 모호성 벤치마크 kiwi510, 정확도 | 0.7588 (**열세**, p 0.0013) | 0.8137 (차이 유의하지 않음) | 0.8275 |

- 기본 모드는 모호성 벤치마크에서 Kiwi 보다 낮고, 정밀 모드(`precise=True`)는 같은 수준입니다. 일반 문장의 형태소 F1 은 기본 모드도 앞섭니다.
- 0.2.x(kword5)와 비교하면 일반 문장 F1 은 같은 수준(문어 −0.02p, 구어 +0.04p, 신문 같음)이고 kiwi510 기본이 +1.2p 입니다. 0.2.x 의 수치는 논문 판(전후향 가지치기 끔, fb 0)으로 남깁니다.
- MP 2025 문어는 홀수 번째 문장으로 평가했고, 같은 기사의 짝수 번째 문장은 점수 가중 학습에 썼습니다(0.2.x 와 같은 조건).
- 속도·메모리는 소개 페이지의 표를 보세요. 0.3.0 은 KnLM 을 읽을 때 복사·삽입이 없어 시작이 약 0.3초 빠르고 메모리를 약 90 MB 덜 씁니다.
- 자세한 표·방법은 논문(준비 중)에 싣습니다. 평가에는 국립국어원 모두의 말뭉치를 활용하였음.

## 코드 라이선스
분석기 코드는 MIT 또는 Apache-2.0 중 택일입니다.
