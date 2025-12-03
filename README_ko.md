# Code Trajectory MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue?style=flat&logo=anthropic)](https://modelcontextprotocol.io)
[![Python Version](https://img.shields.io/badge/python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/SynTaek/code-trajectory-mcp/graphs/commit-activity)
[![GitHub Stars](https://img.shields.io/github/stars/SynTaek/code-trajectory-mcp?style=social)](https://github.com/SynTaek/code-trajectory-mcp)

[![README](https://img.shields.io/badge/README-ENGLISH-blue)](README.md)
[![README_KR](https://img.shields.io/badge/README-KOREAN-blue)](README_ko.md)

> **AI 세션 간에도 코딩의 '흐름(Momentum)'을 유지하세요.**
>
> *"상태(State) 기반" 코딩을 "흐름(Flow) 기반" 개발로 전환합니다.*

**Code Trajectory MCP**는 거대 언어 모델(LLM)에게 여러분의 코딩 기록에 대한 영구적인 기억을 제공하는 Model Context Protocol (MCP) 서버입니다. 이 서버는 별도의 섀도우 리포지토리(Shadow Repository)에서 코드의 *진화 과정*을 추적하여, AI 채팅 세션이 바뀌더라도 작업의 모멘텀, 아키텍처 의도, 최근의 결정 사항들을 잃지 않게 해줍니다.

-----

## 🚀 왜 Code Trajectory인가요?

### 문제점: "새 세션 기억 상실증"

LLM을 사용하는 모든 개발자는 다음과 같은 어려움을 겪습니다.

1.  **컨텍스트 오버플로우:** 깊이 있는 코딩을 진행하던 중, 채팅 내용이 너무 길어집니다. LLM이 느려지거나 토큰 제한에 걸립니다.
2.  **강제 리셋:** 어쩔 수 없이 **New Chat(새 채팅)** 버튼을 눌러야 합니다.
3.  **컨텍스트 소실:** 새로운 AI 세션은 지난 2시간 동안의 작업 내용을 전혀 모릅니다. 여러분은 시간을 들여 다시 설명해야 합니다. *"지금 로그인 리팩토링 중인데... 아까 JWT 쓰기로 했던 거 기억나?"*

### 해결책: 지속적인 모멘텀 (Persistent Momentum)

**Code Trajectory**는 AI를 위한 외부 "해마(장기 기억 저장소)" 역할을 합니다.

  * **이전:** AI는 *현재* 상태의 코드만 볼 수 있었습니다.
  * **Code Trajectory 사용 시:** AI는 코드가 *어떻게* 발전해왔고, *어디서* 작업이 중단되었는지 볼 수 있습니다.
    > *"지난 세션에서 `auth.py`를 OAuth2로 마이그레이션 하던 중이셨군요. 중단된 부분부터 바로 이어서 진행하겠습니다."*

-----

## ✨ 핵심 기능

### 1\. ♾️ 세션의 연속성

이 도구의 핵심 능력입니다. 새로운 채팅을 시작할 때, AI는 이 MCP를 조회하여 **최근 작업의 궤적(trajectory)** 요약본을 불러올 수 있습니다. 단절된 채팅 세션들을 연결하여, "새 채팅" 버튼을 누르더라도 여러분의 아키텍처 결정 사항이 유지되도록 합니다.

### 2\. ⚡ 자동 섀도우 스냅샷

백그라운드 파일 감시자가 파일이 저장될 때마다 **숨겨진 섀도우 git 리포지토리**(`.trajectory`)에 마이크로 커밋을 자동으로 생성합니다.

  * **오염 방지 (Zero Pollution):** 메인 프로젝트의 `git` 기록은 깨끗하게 유지됩니다.
  * **완전한 세분성:** 모든 저장(Save)이 기록되므로, AI가 여러분의 시행착오 과정을 분석할 수 있습니다.

### 3\. 🌊 "흐름(Flow)" 인식

현재의 LLM은 위치는 알지만 속도는 모르는 GPS와 같습니다. 이 도구는 \*\*방향성(Vector)\*\*을 제공합니다.

  * **`get_file_trajectory`**: 파일의 변경 이력을 내러티브 스토리(과거 -\> 현재)로 변환합니다.
  * **`get_global_trajectory`**: 최근 한 파일의 변경이 다른 파일들에 미친 "파급 효과(Ripple Effect)"를 분석합니다.

### 4\. 🎯 의도 파악 및 노이즈 필터링

  * **의도(Intent) 기록:** 시스템에 명시적으로 알릴 수 있습니다. *"Auth 시스템을 리팩토링 중이야."* 이 의도는 변경될 때까지 이후의 모든 스냅샷에 태그로 지정됩니다.
  * **스마트 통합 (Consolidation):** 작업이 완료되면 `consolidate` 기능을 통해, 지저분한 "시행착오" 스냅샷들을 깔끔하고 의미 있는 하나의 히스토리 노드로 압축합니다.

-----

## 🛠️ 기술 스택

  * **런타임:** Python 3.14+
  * **패키지 매니저:** [uv](https://github.com/astral-sh/uv) (압도적으로 빠른 Python 패키지 설치 도구)
  * **핵심 라이브러리:** `mcp`, `gitpython`, `watchdog`

-----

## 📦 설치 및 설정

### 1\. 필수 조건

`uv`가 설치되어 있어야 합니다.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2\. 프로젝트 설정

대상 프로젝트가 git 리포지토리여야 합니다 (MCP는 이를 기준으로 루트를 잡습니다. 데이터는 `.trajectory`에 별도로 저장됩니다).

```bash
cd /path/to/your/project
git init
```

### 3\. AI 클라이언트 설정 (MCP 서버)

사용하시는 AI 도구의 설정 파일에 아래 내용을 추가하세요. `uvx`를 사용하므로 설정 내용은 동일합니다.

  * **Claude Desktop:** `claude_desktop_config.json`
  * **Cursor / 기타 IDE:** `settings.json` (또는 "MCP Servers" 설정 메뉴)

<!-- end list -->

```json
"mcpServers": {
    "code-trajectory": {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/SynTaek/code-trajectory-mcp.git",
            "code-trajectory-mcp"
        ]
    }
}
```

-----

## 🤖 에이전트 워크플로우 가이드

**Code Trajectory**를 최대한 활용하려면 다음 워크플로우를 따르세요. 이를 통해 세션 간에도 AI의 컨텍스트를 온전히 유지할 수 있습니다.

### 1단계: 초기화 (새 세션 시작 시)

\*\*새 채팅(New Chat)\*\*을 시작할 때 항상 다음과 같이 시작하세요.

1.  **구성:** `configure_project(path="/path/to/project")` 호출.
2.  **컨텍스트 복원:** `get_session_summary()` 또는 `get_global_trajectory()` 호출.
      * *결과:* AI가 이전 세션의 "기억"을 다운로드합니다 (예: *"마지막 수정은 5분 전 `User.ts`에서 있었으며, 의도는 'API 버그 수정'이었습니다"*).

### 2단계: 작업 루프

1.  **의도 설정:** `set_trajectory_intent("다크 모드 구현 중")`
      * *이유:* 모든 파일 저장에 이 목표를 태그하여, 히스토리에 의미를 부여합니다.
2.  **작업:** 여러분이나 AI가 파일을 편집합니다. 서버는 백그라운드에서 자동으로 `[AUTO-TRJ]` 스냅샷을 찍습니다.

### 3단계: 정리 및 통합 (작업 완료 시)

1.  **통합(Consolidate):** `consolidate("다크 모드 구현 완료")`
      * *이유:* 지저분한 중간 저장 과정들을 하나의 깔끔한 히스토리 노드로 정리하여, *다음* 세션을 위한 확실한 체크포인트를 만듭니다.

-----

## 📊 모멘텀 시각화하기

`.trajectory`는 표준 Git 리포지토리이므로, 기존 도구들을 사용하여 여러분의 "사고 과정"을 시각화할 수 있습니다.

  * **VSCode:** 새 창에서 `.trajectory` 폴더를 열고 **Git Graph** 확장을 사용하세요.
  * **터미널:**
    ```bash
    # 내러티브 로그 확인
    git --git-dir=.trajectory/.git log --graph --oneline --all
    ```

## 📄 라이선스

MIT