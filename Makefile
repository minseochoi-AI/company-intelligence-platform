.PHONY: help setup test spec export-all clean

help:
	@echo "========================================================================"
	@echo " [Company-Intel Platform] 사용 가능한 Make 명령 목록"
	@echo "========================================================================"
	@echo "  make setup       : 환경 자동 구성 (Poetry 설치, 의존성 설치, 스킬 등록)"
	@echo "  make spec        : 28대 API 및 21,000개 클러스터 사전 기준 설명문 출력"
	@echo "  make test        : 핵심 31개 단위 테스트 및 회귀 무결성 검증 실행"
	@echo "  make export-all  : 6대 IT경영 마스터 엑셀 워크북 전수 재생성 및 검증"
	@echo "  make clean       : 임시 캐시 및 파이썬 컴파일 아티팩트 정리"
	@echo "========================================================================"

setup:
	@bash ./setup.sh

spec:
	@poetry run company-intel cluster-spec

test:
	@poetry run pytest tests/test_job_cluster_signature.py tests/test_live_job_provenance.py tests/test_cli_cluster_jobs.py tests/test_six_workbooks_provenance.py tests/test_dynamic_report_compiler.py -v

export-all:
	@poetry run python scripts/generate_six_it_management_workbooks.py
	@poetry run pytest tests/test_six_workbooks_provenance.py -v

clean:
	@rm -rf .pytest_cache __pycache__ src/company_intel/__pycache__ tests/__pycache__
	@echo "[완료] 임시 캐시 파일이 삭제되었습니다."
