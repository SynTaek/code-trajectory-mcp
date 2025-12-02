# Code Trajectory MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue?style=flat&logo=anthropic)](https://modelcontextprotocol.io)
[![Python Version](https://img.shields.io/badge/python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/SynTaek/code-trajectory/graphs/commit-activity)
[![GitHub Stars](https://img.shields.io/github/stars/SynTaek/code-trajectory?style=social)](https://github.com/SynTaek/code-trajectory)

[![README](https://img.shields.io/badge/README-ENGLISH-blue)](README.md)
[![README_KR](https://img.shields.io/badge/README-KOREAN-blue)](README_ko.md)

> **LLM을 위한 "상태 기반(State-Based)"에서 "흐름 기반(Flow-Based)" 코딩으로의 진화**

**Code Trajectory MCP**는 거대 언어 모델(LLM)이 코드의 현재 상태뿐만 아니라 **진화의 역사**를 이해할 수 있도록 돕는 MCP(Model Context Protocol) 서버입니다. 자동화된 스냅샷을 추적하고 개발 패턴을 분석함으로써, LLM이 현재 개발자의 작업 속도, 의도, 그리고 아키텍처 방향성에 맞춰 코드를 작성할 수 있게 합니다.

## 🚀 왜 Code Trajectory인가?

기존의 LLM은 현재 위치는 알지만, 이동 방향이나 속도는 모르는 GPS처럼 작동합니다.

  * **Trajectory 미사용:** "이 함수 좀 고쳐줘." (LLM이 5분 전에 당신이 수행한 리팩토링과 모순되는 수정을 제안할 수 있음)
  * **Trajectory 사용:** "최근 3번의 수정 내역을 보니 SQL을 ORM으로 마이그레이션하고 있고, 에러는 `try-catch` 블록으로 처리하고 있군요. 그 패턴을 그대로 따라 이 함수를 수정하겠습니다."

## ✨ 핵심 기능

  * **⚡ 자동 섀도우 스냅샷 (Automated Shadow Snapshots):** 백그라운드 파일 감시자(`watchdog` 사용)가 파일을 저장할 때마다 **섀도우 Git 저장소**(`.trajectory`)에 마이크로 커밋(스냅샷)을 자동으로 생성합니다. 이를 통해 메인 Git 기록을 깔끔하고 독립적으로 유지할 수 있습니다.
  * **문맥 인식 검색 (Context-Aware Retrieval):**
      * **`get_file_trajectory`**: 특정 파일의 변경 이력을 서사적 흐름(과거 -\> 현재)으로 포맷팅합니다.
      * **`get_global_trajectory`**: 파일 간 의존성 및 최근 프로젝트 전반의 변경 사항(파급 효과)을 파악합니다.
  * **스마트 노이즈 필터링:** "시행착오(Trial & Error)" 루프를 자동으로 감지하고 요약합니다. 파일을 이전 상태로 되돌리면 `[Revert Detected]`라고 명시적으로 주석을 답니다.
  * **의도 기록 (Intent Recording):** LLM(혹은 사용자)이 현재 의도(예: "로그인 리팩토링 중")를 선언할 수 있으며, 이 의도는 더 나은 문맥 파악을 위해 이후 스냅샷들에 첨부됩니다.
  * **세션 연속성:** 이전 작업 내용을 요약하여 작업 세션 사이의 공백을 메워줍니다.

## 🛠️ 기술 스택 (Tech Stack)

  * **런타임:** Python 3.14+
  * **패키지 매니저:** [uv](https://github.com/astral-sh/uv) (매우 빠른 Python 패키지 설치 도구)
  * **핵심 라이브러리:** `mcp`, `gitpython`, `watchdog`

## 📦 설치 및 설정

### 1. 필수 조건

`uv`가 설치되어 있어야 합니다:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 구성

추적하려는 대상 프로젝트에 `git`이 초기화되어 있는지 확인하세요.

```bash
cd /path/to/your/project
git init
```

## 🔌 설정 (Configuration)

### Claude Desktop

`claude_desktop_config.json` 파일에 다음 내용을 추가하세요:

```json
{
  "mcpServers": {
    "code-trajectory": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/SynTaek/code-trajectory.git",
        "code-trajectory"
      ]
    }
  }
}
```

> **참고:** `--path` 인수는 선택 사항입니다. 생략할 경우, 서버는 **자동으로 현재 작업 디렉토리를 기본값으로 설정**합니다.

### Gemini (Google AI Studio / Vertex AI)

MCP 호환 Gemini 인터페이스를 사용하는 경우, 다음 명령 설정을 사용하세요:

  * **Command:** `uvx`
  * **Args:** `--from git+https://github.com/SynTaek/code-trajectory.git code-trajectory`

### VSCode 및 파생 에디터 (Cursor, Windsurf 등)

**VSCode**, **Cursor**, **Windsurf**, **Antigravity** 또는 기타 VSCode 기반 에디터에서 MCP 확장 프로그램을 사용하는 경우, `.vscode/settings.json` (또는 해당 에디터의 설정 파일)이나 전역 설정에 다음을 추가하세요:

```json
"mcp.servers": {
    "code-trajectory": {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/SynTaek/code-trajectory.git",
            "code-trajectory"
        ]
    }
}
```

## 🤖 에이전트 사용 가이드

이 MCP 서버는 AI 에이전트의 "문맥 파트너(Context Partner)"가 되도록 설계되었습니다. 에이전트를 위한 권장 워크플로우는 다음과 같습니다:

### 1. 초기화 (자동 설정)

서버는 시작 시 현재 작업 디렉토리에 맞춰 자동으로 설정됩니다. 다른 프로젝트 경로로 전환하려는 경우가 아니라면 `configure_project`를 호출할 필요가 **없습니다**.

### 2. "플로우(Flow)" 루프

에이전트로서, 고품질의 문맥을 유지하기 위해 다음 루프를 따르세요:

1.  **작업 시작:** 논리적인 작업 단위(예: "로그인 구현")를 시작할 때, `set_trajectory_intent("Implementing Login")`을 호출하세요.
      * *이유:* 이 의도(Intent)가 모든 자동 스냅샷에 첨부되어, 히스토리를 읽기 쉽고 의미 있게 만듭니다.
2.  **작업 수행:** 파일 편집(`write_to_file` 등)을 수행하세요.
      * *배경 동작:* 서버가 편집을 감지하고 섀도우 저장소에 `[AUTO-TRJ]` 스냅샷을 생성합니다.
3.  **정리(Consolidate):** 작업이 완료되거나 안정적인 상태에 도달하면 `consolidate("Completed Login Implementation")`를 호출하세요.
      * *효과:* 지저분한 `[AUTO-TRJ]` 스냅샷들을 당신이 작성한 메시지와 함께 하나의 깔끔한 커밋으로 압축(Squash)합니다.
      * *장점:* 작업 단계에서의 "생각 과정"은 보존하면서 히스토리는 깔끔하게 유지합니다.
      * **⚠️ 모범 사례:** 기능 구현이 완전히 **완료되었을 때만** 정리를 수행하세요. 디버깅 중에 정리를 수행하면, 무엇을 시도했고 실패했는지에 대한 상세한 기록을 잃게 됩니다.
      * **참고:** 정리는 메인 프로젝트의 Git 기록에 커밋을 생성하지 **않습니다**. 오직 섀도우 히스토리만 정리합니다.

### 3. 문맥 검색 도구

변경을 가하기 전에 코드베이스를 이해하기 위해 이 도구들을 사용하세요:

  * **`get_session_summary()`**: 세션에 진입할 때 가장 먼저 호출하세요. 최근에 무슨 일이 있었는지 알려줍니다.
  * **`get_file_trajectory(filepath)`**: 복잡한 파일을 편집하기 전에 호출하세요. 파일의 현재 상태뿐만 아니라 *어떻게* 진화해왔는지 보여줍니다.
  * **`get_global_trajectory(limit=20, since_consolidate=False)`**: 내 변경 사항이 다른 파일에 파급 효과를 일으키는지 확인할 때 호출하세요. `since_consolidate=True`를 사용하면 마지막 정리 이후의 모든 변경 사항을 확인할 수 있습니다.

## 🗺️ 워크플로우 예시

1.  **Agent:** `set_trajectory_intent("Refactoring auth logic")` (인증 로직 리팩토링 의도 설정)
2.  **Agent:** `auth.py` 편집 (저장 1) -> *서버가 [AUTO-TRJ] 스냅샷 생성*
3.  **Agent:** `user.py` 편집 (저장 2) -> *서버가 [AUTO-TRJ] 스냅샷 생성*
4.  **Agent:** `consolidate("Refactored auth logic to use JWT")` (JWT 사용으로 인증 로직 리팩토링 완료)
      * *서버:* 스냅샷들을 압축 -> `[CONSOLIDATE] Refactored auth logic to use JWT` 커밋 생성.

## 📊 궤적(Trajectory) 히스토리 보기

`.trajectory`는 표준 Git 저장소이므로, 선호하는 도구를 사용하여 코딩 세션의 상세한 "생각 과정"을 검사할 수 있습니다.

### 방법 A: VSCode (권장)

1.  VSCode에서 **새 창(New Window)**을 엽니다.
2.  **폴더 열기(Open Folder)**를 선택하고 프로젝트 내부의 `.trajectory` 폴더를 선택합니다.
3.  **Git Graph** 같은 확장 프로그램을 사용하여 히스토리 트리를 시각화합니다.

### 방법 B: 터미널

프로젝트 루트를 떠나지 않고 섀도우 저장소를 가리키는 git 명령어를 실행할 수 있습니다:

```bash
# 로그 그래프 보기
git --git-dir=.trajectory/.git log --graph --oneline --all

# 상세 변경 내역(diff) 보기
git --git-dir=.trajectory/.git log -p
```

### 방법 C: Git GUI 도구

선호하는 Git GUI(SourceTree, GitKraken, Fork 등)를 열고 `.trajectory` 폴더를 로컬 저장소로 추가하세요.

## 📄 라이선스

MIT