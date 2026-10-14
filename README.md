# madi (마디) — 배포 저장소

순수 Rust 로 만든 한국어 형태소 분석기 **madi** 의 공개 배포물(모델 파일, 설치 안내)을 두는 저장소입니다. 코드 저장소는 따로 있습니다.

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

## 이용 조건

- 프로그램(Python 패키지): MIT 또는 Apache-2.0.
- 사전: mecab-ko-dic(Apache-2.0) 을 바탕으로 합니다.
- 언어모델·교사 모델: 국립국어원 「모두의 말뭉치」로 학습했습니다. **[이용 조건 — 국립국어원 결과물 공개 승인 내용에 맞춰 적을 것]**
- 학습 말뭉치 원문은 포함하지 않습니다.

<!-- 공개 승인 뒤 주석을 푼다 (closeout 10.14 §2). 수치는 WikiDocs 9.2 'README 한 줄' 과 같아야 한다.
## 성능 요약 (평가 2차, 2026.10.13)
학습과 독립인 셋에서 Kiwi 대비 +0.4p(유의) · 모두의 말뭉치 지침 준수 최상 · Kiwi 보다 12~26% 빠르고 가벼움 · 모호성 벤치마크는 기본 모드 열세, 정밀 모드 동급 · 문장 분리 개선(0.805).

## 출처
국립국어원 모두의 말뭉치(형태 분석 말뭉치, 어휘 의미 분석 말뭉치)를 활용하였음.
-->
