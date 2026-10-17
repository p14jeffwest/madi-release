# madi (마디) — 배포 저장소

순수 Rust 로 만든 한국어 형태소 분석기 **madi** 의 공개 배포물(모델 파일, 설치 안내)을 두는 저장소입니다.

## 공개 범위
| 구분 | 무엇 | 어디 | 조건 |
|---|---|---|---|
| **공개하는 것** | 분석기 코드 `madi-core`·`madi-lm`·`madi`·`madi-cli`(+ 보조 `madi-news`·`madi-build`) | crates.io (소스 포함) | MIT OR Apache-2.0 |
| | Python 패키지 `madipy`(휠) | PyPI | MIT OR Apache-2.0 |
| | 모델·사전 파일(이 저장소 Release `models-kword5`), WASM 경량 모델 | GitHub Release | CC BY-SA 2.0 KR |
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

## 모델 파일 (Release `models-kword5`)

| 파일 | 내용 | 받기 | 풀면 |
|---|---|---|---|
| `madi.dict.xz` | 사전 (mecab-ko-dic 기반 + 확장) | 14.7 MB | 102.7 MB |
| `knlm.bin.xz` | 형태소 n-gram 언어모델 (KnLM) | 40.5 MB | 101.5 MB |
| `model.nlm.xz` | 신경망 언어모델 | 31.9 MB | 36.4 MB |
| `precise.tlm.xz` | 정밀 모드 교사 모델 | 27.3 MB | 37.9 MB |

Python 패키지가 받을 때 sha256 을 확인합니다. 손으로 받을 때의 sha256(풀린 파일):

```
25cb2121ebf199043bc4ac684b85feb18702173998790c61acbbd2fc07157a48  madi.dict
d7a71256f25ccd6609c104f891852ea9ef1046964a9fb93cb2276e496e3e6c37  knlm.bin
8c8e58897743eb976ae0ff286f72814ceebc8de99840e17a34c18854f838822d  model.nlm
c6d35a7f5514f3846673ed3c7544562832c5ee4dba0158b6a3956392b072369e  precise.tlm
```

### 모델 이용 조건
모델·사전 파일은 CC BY-SA 2.0 KR. 국립국어원 모두의 말뭉치(형태 분석 말뭉치 2018~2020, 형태 분석 말뭉치 2025, 어휘 의미 분석 말뭉치 2020)와 우리말샘을 활용하였음(국립국어원 공개 승인 2026-10-17). 말뭉치 원문을 담거나 복원할 수 없는 통계·가중치임. 신문 기사 원문으로 자기 라벨 학습.
- 사전은 mecab-ko-dic(Apache-2.0)을 바탕으로 합니다.
- 전문과 출처 표시 예: `LICENSE-MODELS.txt`(Release 에 함께 있음). 학습 입력 목록: [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md).
- 학습 말뭉치 원문은 포함하지 않습니다.

## 성능 요약 (공개판, 2026-10-17)

같은 잣대(세종 태그 사상, 관행 차이 정규화)로 다른 분석기와 비교했습니다. 차이는 Kiwi CoNg(kiwipiepy 0.24.0) 대비, 괄호는 95% 구간입니다.

| | madi 기본 | madi 정밀 | Kiwi CoNg |
|---|---|---|---|
| 모두의 말뭉치 형태 분석 2025 문어(학습과 독립, 6,953문장), 형태소 F1 | **0.9774** (+0.32p [+0.24, +0.39]) | 0.9784 (+0.42p) | 0.9742 |
| 같은 셋 구어(16,439문장) | **0.9640** (+0.53p [+0.44, +0.64]) | 0.9656 (+0.69p) | 0.9586 |
| 신문 1990~2025 평가셋(420문장, 손 교정), 중립 F1 | 0.9772 (+0.35p, 유의하지 않음) | 0.9786 (+0.49p) | 0.9737 |
| Kiwi 모호성 벤치마크 kiwi510, 정확도 | 0.7471 (**열세**, p 0.0002) | 0.8137 (차이 유의하지 않음) | 0.8275 |
| 속도(랩탑 1스레드, Python 바인딩, KB/s) | 284 | 26 | 268 |

- 기본 모드는 모호성 벤치마크에서 Kiwi 보다 낮고, 정밀 모드(`precise=True`)는 같은 수준입니다. 일반 문장의 형태소 F1 은 기본 모드도 앞섭니다.
- 공개판의 기본 설정은 위 측정 설정에 전후향 가지치기(τ 11)를 더한 것입니다. 측정 셋 1만 7천 문장 중 5문장만 출력이 달라지고, 2단계 LM 질의가 44% 줄어 랩탑 CLI 에서 약 17% 빨라집니다. 같은 정도의 시간 이득은 1단계 문턱(`--prefilter 6`)으로도 얻을 수 있으며, 전후향 가지치기의 몫은 LM 질의 수를 줄이는 데 있습니다.
- 자세한 표·방법은 논문(준비 중)에 싣습니다. 평가에는 국립국어원 모두의 말뭉치를 활용하였음.

## 코드 라이선스
분석기 코드는 MIT 또는 Apache-2.0 중 택일입니다.
