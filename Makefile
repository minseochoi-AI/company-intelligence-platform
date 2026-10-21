.PHONY: help setup test spec export-instances

help:
	@echo 'make setup: uv workspace 설치; make test: 회귀 검증; make spec: 등록 capability 집계'
	@echo 'make export-instances INSTANCES=instances.json OUTPUT=artifacts/research: 명시 인스턴스 출력'

setup:
	uv sync --all-extras --locked

spec:
	uv run --locked --no-sync company-intel cluster-spec

test:
	uv run --locked --no-sync python -m pytest -q

export-instances:
	uv run --locked --no-sync python scripts/generate_six_it_management_workbooks.py --instances "$(INSTANCES)" --output "$(OUTPUT)"
