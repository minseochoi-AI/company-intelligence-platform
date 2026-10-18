#!/usr/bin/env bash
# ==============================================================================
# Company Intelligence Platform & Antigravity One-Click Setup Script
# 이 스크립트는 비개발자도 명령어 1회 실행으로 안티그래비티 및 플랫폼 환경을 자동 구성합니다.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo " [Company-Intel Platform] 원클릭 통합 환경 설정 시작"
echo " 대상 경로: $SCRIPT_DIR"
echo "========================================================================"

# 1. Python 및 시스템 필수 도구 점검
echo ">> 1단계: Python 런타임 및 필수 도구 점검..."
if ! command -v python3 &>/dev/null; then
    echo "[오류] Python 3이 설치되어 있지 않습니다. Python 3.11 이상을 먼저 설치해주세요."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "   - 감지된 Python 버전: $PY_VERSION"

# 2. Poetry 패키지 관리자 설치 확인 및 자동 설치
echo ">> 2단계: Poetry 의존성 관리자 점검..."
if ! command -v poetry &>/dev/null; then
    echo "   - Poetry가 설치되어 있지 않습니다. 공식 인스톨러로 자동 설치를 진행합니다..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "   - Poetry 준비 완료: $(poetry --version)"

# 3. 프로젝트 가상환경 및 Python 패키지 설치
echo ">> 3단계: 가상환경 생성 및 필수 라이브러리 설치 (poetry install)..."
poetry install --no-interaction

# 4. API 보안 키 파일 (.env) 점검
echo ">> 4단계: API 인증 키(.env) 구성 확인..."
if [ -f ".env" ]; then
    echo "   - [확인] .env 파일이 이미 준비되어 있습니다."
else
    if [ -f ".env.example" ]; then
        echo "   - [주의] .env가 없어 .env.example을 복사합니다. 필요한 API 키를 입력해주세요."
        cp .env.example .env
    fi
fi

# 5. 안티그래비티 (Antigravity) 스킬 자동 등록
echo ">> 5단계: 안티그래비티(AGY) 스킬 자동 바인딩..."
mkdir -p "$SCRIPT_DIR/.agents/skills"

# .codex 및 글로벌 스킬 동기화
if [ -d "$HOME/.gemini/config/skills/company-intelligence-career-research" ]; then
    cp -r "$HOME/.gemini/config/skills/company-intelligence-career-research" "$SCRIPT_DIR/.agents/skills/"
fi
if [ -d "$SCRIPT_DIR/.codex/skills/company-intel-cli" ]; then
    cp -r "$SCRIPT_DIR/.codex/skills/company-intel-cli" "$SCRIPT_DIR/.agents/skills/"
fi
if [ -d "$SCRIPT_DIR/.codex/skills/company-intelligence-analysis" ]; then
    cp -r "$SCRIPT_DIR/.codex/skills/company-intelligence-analysis" "$SCRIPT_DIR/.agents/skills/"
fi
if [ -d "$SCRIPT_DIR/.codex/skills/kr-defensible-venture-discovery" ]; then
    cp -r "$SCRIPT_DIR/.codex/skills/kr-defensible-venture-discovery" "$SCRIPT_DIR/.agents/skills/"
fi

# 글로벌 ~/.gemini/config/skills에도 역방향 등록 (전역 사용 지원)
if [ -d "$HOME/.gemini/config" ]; then
    mkdir -p "$HOME/.gemini/config/skills"
    for skill in "$SCRIPT_DIR/.agents/skills"/*; do
        if [ -d "$skill" ]; then
            sname="$(basename "$skill")"
            rm -rf "$HOME/.gemini/config/skills/$sname"
            cp -r "$skill" "$HOME/.gemini/config/skills/$sname"
        fi
    done
    echo "   - [확인] 안티그래비티 전역 스킬(~/.gemini/config/skills) 및 워크스페이스 스킬(.agents/skills) 동기화 완료."
fi

# 6. 플랫폼 핵심 검증 실행
echo ">> 6단계: 플랫폼 및 사전 기준 설명문 자가 진단 실행..."
poetry run pytest tests/test_dynamic_report_compiler.py -q
echo "   - [합격] 3-계층 동적 엑셀 컴파일러 및 사전 설명문 단위 테스트 통과."

echo ""
echo "========================================================================"
echo " [설치 완료] 안티그래비티 및 플랫폼 준비가 100% 완료되었습니다!"
echo "========================================================================"
echo " 바로 사용 가능한 명령어:"
echo "   1) 사전 설명문 출력 : poetry run company-intel cluster-spec"
echo "   2) 채용 공고 엑셀 추출: poetry run company-intel export-cluster-jobs --interactive"
echo "   3) 안티그래비티 채팅창: '체코 국영기업 IT 채용공고 엑셀 뽑아줘' 등 자연어로 질의"
echo "========================================================================"
