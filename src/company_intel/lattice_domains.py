"""Comprehensive multi-domain occupational lattice data registry covering KR NCS, CZ-ISCO, and US O*NET.

This module expands beyond IT/Data into the full national occupational spectrum across 12 major domains:
1. ICT / Software / Data / AI (NCS 20, 02 / ISCO 25, 133 / O*NET 15)
2. Semiconductor / Electronics / Hardware (NCS 19 / ISCO 215, 132 / O*NET 17)
3. Manufacturing / Mobility / Autonomous Robotics (NCS 15, 01 / ISCO 214, 132 / O*NET 17)
4. Bio / Pharma / Clinical Healthcare (NCS 17, 06 / ISCO 213, 226, 134 / O*NET 19, 11)
5. Chemical / Battery / Energy / Materials (NCS 17, 23, 16 / ISCO 214, 132 / O*NET 17)
6. Management / Strategy / Business / HR (NCS 01, 02 / ISCO 242, 112 / O*NET 13, 11)
7. Finance / Investment / Asset Mgmt / Fintech (NCS 03 / ISCO 241, 121 / O*NET 13, 11)
8. Marketing / Sales / GTM / Technical Sales (NCS 10 / ISCO 243, 122 / O*NET 41, 13)
9. Legal / IP / Patent / Compliance (NCS 05 / ISCO 261, 121 / O*NET 23, 11)
10. Construction / Architecture / Smart Civil (NCS 14 / ISCO 216, 214, 132 / O*NET 17, 11)
11. Culture / Design / Media / Content (NCS 08 / ISCO 216, 264, 122 / O*NET 27, 11)
12. Environment / Industrial Safety / ESG (NCS 23 / ISCO 214, 226, 134 / O*NET 17, 29)
13. Grand Unified Macro Occupational Lattice (cross-domain mobility DAG & value chains)
"""
from __future__ import annotations

from typing import Callable

from company_intel.lattice_models import (
    CareerEdge,
    LatticeDomainGraph,
    RoleNode,
    WorkflowConnection,
)


def build_ict_domain() -> LatticeDomainGraph:
    """Domain 1: ICT / Software / Data / AI."""
    graph = LatticeDomainGraph("ict_data_ai", "ICT / Software & Data / AI")
    roles = [
        RoleNode(
            role_id="2511-data-analyst",
            role_name="데이터 분석가 (Data Analyst)",
            isco_08="2511",
            kr_ncs="02010101",
            kr_keco="133101",
            cz_isco="25110",
            us_onet="15-1211.00",
            domain_id="ict_data_ai",
            career_level=1,
            salary_band={"krw_min": 42000000, "krw_max": 65000000, "czk_avg": 55000, "usd_avg": 85000},
            hiring_demand="increasing",
            skills=["SQL", "Python", "Tableau", "EDA", "A/B Testing"],
            value_chain_stage="OPS",
            headcount_share=12.5,
            peer_staffing_index=1.05,
            wage_inflation_rate=6.2,
            automation_exposure=0.55,
            rev_per_hc_leverage="standard",
            workflow_role_type="user",
            workflow_pain_points=["비정형 원천 데이터 수동 클렌징", "지표 정의 불일치에 따른 리포트 재작업"],
        ),
        RoleNode(
            role_id="2512-data-engineer",
            role_name="데이터 엔지니어 (Data Engineer)",
            isco_08="2512",
            kr_ncs="02010102",
            cz_isco="25120",
            us_onet="15-1252.00",
            domain_id="ict_data_ai",
            career_level=2,
            salary_band={"krw_min": 55000000, "krw_max": 85000000, "czk_avg": 75000, "usd_avg": 125000},
            hiring_demand="very-high",
            skills=["Spark", "Kafka", "Airflow", "DBT", "BigQuery", "Snowflake"],
            value_chain_stage="OPS",
            headcount_share=8.0,
            peer_staffing_index=0.92,
            wage_inflation_rate=8.8,
            automation_exposure=0.28,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["이종 데이터 소스 파이프라인 장애", "다국가 코드 매핑 수작업 병목"],
        ),
        RoleNode(
            role_id="2511-ml-engineer",
            role_name="ML/AI 엔지니어 (MLOps/Modeler)",
            isco_08="2511",
            kr_ncs="02010103",
            cz_isco="25110",
            us_onet="15-1221.00",
            domain_id="ict_data_ai",
            career_level=3,
            salary_band={"krw_min": 65000000, "krw_max": 110000000, "czk_avg": 90000, "usd_avg": 160000},
            hiring_demand="scarce",
            skills=["PyTorch", "MLOps", "vLLM", "Distributed Training", "CUDA"],
            value_chain_stage="RND",
            headcount_share=16.0,
            peer_staffing_index=1.45,
            wage_inflation_rate=14.2,
            automation_exposure=0.18,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["GPU 인프라 비용 과다", "모델 서빙 지연(Latency) 최적화 난항"],
        ),
        RoleNode(
            role_id="2512-fullstack-dev",
            role_name="풀스택 소프트웨어 엔지니어 (Fullstack Dev)",
            isco_08="2512",
            kr_ncs="02020101",
            cz_isco="25120",
            us_onet="15-1254.00",
            domain_id="ict_data_ai",
            career_level=2,
            salary_band={"krw_min": 50000000, "krw_max": 80000000, "czk_avg": 70000, "usd_avg": 120000},
            hiring_demand="very-high",
            skills=["TypeScript", "React", "Python", "FastAPI", "Docker", "PostgreSQL"],
            value_chain_stage="RND",
            headcount_share=24.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=7.5,
            automation_exposure=0.35,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["레거시 프론트-백엔드 동기화", "API 스키마 드리프트 및 변경 전파"],
        ),
        RoleNode(
            role_id="2529-sec-engineer",
            role_name="보안 프로그램 개발자 (SecOps/Engineer)",
            isco_08="2529",
            kr_ncs="02050101",
            cz_isco="25290",
            us_onet="15-1212.00",
            domain_id="ict_data_ai",
            career_level=3,
            salary_band={"krw_min": 60000000, "krw_max": 95000000, "czk_avg": 80000, "usd_avg": 140000},
            hiring_demand="scarce",
            skills=["Zero Trust", "IAM", "Cloud Security", "OAuth/SAML", "Vulnerability Scanning"],
            value_chain_stage="OPS",
            headcount_share=7.5,
            peer_staffing_index=0.85,
            wage_inflation_rate=11.5,
            automation_exposure=0.15,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["보안 감사 규정 준수 수동 증빙", "권한 오남용 및 이상 행위 탐지 지연"],
        ),
        RoleNode(
            role_id="1330-tech-lead",
            role_name="AI 플랫폼 테크 리드 (Tech Lead / VP)",
            isco_08="1330",
            kr_ncs="02010100",
            cz_isco="13300",
            us_onet="11-3021.00",
            domain_id="ict_data_ai",
            career_level=4,
            salary_band={"krw_min": 110000000, "krw_max": 180000000, "czk_avg": 130000, "usd_avg": 220000},
            hiring_demand="scarce",
            skills=["Technical Architecture", "Team Leadership", "Business Strategy", "Talent Retention"],
            value_chain_stage="RND",
            headcount_share=4.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=12.0,
            automation_exposure=0.10,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["개발자 채용/유지 비용 급등", "인프라 예산 초과 및 ROI 증명 압박"],
        ),
        RoleNode(
            role_id="1330-ciso",
            role_name="보안 담당 팀장 / CISO",
            isco_08="1330",
            kr_ncs="02050100",
            cz_isco="13300",
            us_onet="11-3021.00",
            domain_id="ict_data_ai",
            career_level=5,
            salary_band={"krw_min": 120000000, "krw_max": 200000000, "czk_avg": 150000, "usd_avg": 240000},
            hiring_demand="scarce",
            skills=["Security Governance", "Compliance (ISMS-P, GDPR)", "Crisis Management", "Vendor Risk"],
            value_chain_stage="CORP",
            headcount_share=2.0,
            peer_staffing_index=0.90,
            wage_inflation_rate=10.0,
            automation_exposure=0.08,
            rev_per_hc_leverage="high",
            workflow_role_type="payer",
            workflow_pain_points=["공급망 보안 리스크 증가", "외부 보안 감사 외주 비용 부담"],
        ),
        RoleNode(
            role_id="2433-solution-architect",
            role_name="솔루션즈 아키텍트 / 테크니컬 세일즈",
            isco_08="2433",
            kr_ncs="10010101",
            cz_isco="24330",
            us_onet="15-1299.08",
            domain_id="ict_data_ai",
            career_level=3,
            salary_band={"krw_min": 70000000, "krw_max": 120000000, "czk_avg": 85000, "usd_avg": 150000},
            hiring_demand="very-high",
            skills=["Enterprise Pre-sales", "Cloud Architecture", "Client PoC", "ROI Estimation"],
            value_chain_stage="GTM",
            headcount_share=15.0,
            peer_staffing_index=1.20,
            wage_inflation_rate=9.0,
            automation_exposure=0.20,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["고객사 맞춤형 PoC 환경 셋업 지연", "기술 제안서 수작업 작성"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2511-data-analyst", "2512-data-engineer", "vertical_promotion", ["Spark", "Kafka", "Airflow", "DBT"], ["Cloud DW Tuning"], "실무 2년 이상", 2, 30.0),
        CareerEdge("2511-data-analyst", "2511-ml-engineer", "specialization", ["PyTorch", "Linear Algebra", "MLOps"], ["Transformer Fine-tuning"], "수학/CS 심화", 4, 55.0),
        CareerEdge("2512-fullstack-dev", "2511-ml-engineer", "specialization", ["PyTorch", "Feature Store", "CUDA Kernel"], ["Model Distillation"], "머신러닝 이론", 4, 35.0),
        CareerEdge("2512-data-engineer", "2511-ml-engineer", "specialization", ["PyTorch", "Model Architecture"], ["Distributed Training"], "딥러닝 파이프라인", 3, 25.0),
        CareerEdge("2512-fullstack-dev", "2529-sec-engineer", "horizontal_transfer", ["Zero Trust", "OAuth/SAML", "IAM Policy"], ["CISSP/CISA"], "보안 체계", 3, 20.0),
        CareerEdge("2511-ml-engineer", "1330-tech-lead", "vertical_promotion", ["Technical Architecture", "Team Leadership"], ["Talent Retention"], "엔지니어링 리딩 5년", 5, 45.0),
        CareerEdge("2529-sec-engineer", "1330-ciso", "vertical_promotion", ["Security Governance", "Compliance (ISMS-P)"], ["Vendor Contract"], "정보보호 관리 경력", 5, 50.0),
        CareerEdge("2512-fullstack-dev", "2433-solution-architect", "horizontal_transfer", ["Enterprise Pre-sales", "Client PoC"], ["Public Speaking"], "B2B 고객 대응", 2, 25.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2511-data-analyst",
            "2512-data-engineer",
            "원천 데이터 정제 및 파이프라인 요건 전달",
            8.5,
            "스키마 변경 시 다운스트림 분석 쿼리 일괄 중단",
            {"product_name": "DataOps Contract Manager", "target_buyer": "Head of Data / VP", "estimated_wtp": "월 $2,000"},
        ),
        WorkflowConnection(
            "2511-ml-engineer",
            "1330-tech-lead",
            "모델 학습 클러스터 자원 배분 및 비용 승인",
            12.0,
            "GPU 유휴 인스턴스 발생 및 멀티 클라우드 비용 폭증",
            {"product_name": "ClusterFinOps Engine", "target_buyer": "Tech Lead / CTO", "estimated_wtp": "월 $5,000"},
        ),
        WorkflowConnection(
            "2529-sec-engineer",
            "1330-ciso",
            "인증 토큰 누출 및 보안 규정 준수 현황 보고",
            6.0,
            "수동 스프레드시트 감사 및 써드파티 SDK 권한 파악 불가",
            {"product_name": "Continuous Compliance Guard", "target_buyer": "CISO / 법무팀", "estimated_wtp": "월 $3,500"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_semiconductor_domain() -> LatticeDomainGraph:
    """Domain 2: Semiconductor / Electronics / Hardware (NCS 19)."""
    graph = LatticeDomainGraph("semiconductor_electronics", "Semiconductor & Hardware Electronics")
    roles = [
        RoleNode(
            role_id="2152-circuit-designer",
            role_name="반도체 회로설계 엔지니어 (IC/ASIC)",
            isco_08="2152",
            kr_ncs="19020101",
            cz_isco="21520",
            us_onet="17-2072.00",
            domain_id="semiconductor_electronics",
            career_level=2,
            salary_band={"krw_min": 60000000, "krw_max": 95000000, "czk_avg": 80000, "usd_avg": 130000},
            hiring_demand="scarce",
            skills=["Verilog/VHDL", "EDA Tools (Synopsys/Cadence)", "RTL Synthesis", "Timing Closure", "FPGA"],
            value_chain_stage="RND",
            headcount_share=18.0,
            peer_staffing_index=1.35,
            wage_inflation_rate=11.2,
            automation_exposure=0.15,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["PPA(Power, Performance, Area) 최적화 시뮬레이션 지연", "파운드리 PDK 버전 변경 대응"],
        ),
        RoleNode(
            role_id="2152-process-engineer",
            role_name="반도체 공정/수율 엔지니어 (Fab Process)",
            isco_08="2152",
            kr_ncs="19020102",
            cz_isco="21520",
            us_onet="17-2072.00",
            domain_id="semiconductor_electronics",
            career_level=2,
            salary_band={"krw_min": 55000000, "krw_max": 88000000, "czk_avg": 75000, "usd_avg": 120000},
            hiring_demand="very-high",
            skills=["Lithography", "Etch/Deposition", "SPC (Statistical Process Control)", "Yield Analysis", "Cleanroom Ops"],
            value_chain_stage="OPS",
            headcount_share=25.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=8.5,
            automation_exposure=0.20,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["웨이퍼 수율 결함 원인 추적 수작업 지연", "장비 챔버 간 공정 편차"],
        ),
        RoleNode(
            role_id="2152-embedded-firmware-eng",
            role_name="임베디드 펌웨어 엔지니어 (Firmware/SoC)",
            isco_08="2152",
            kr_ncs="19020201",
            cz_isco="21520",
            us_onet="17-2072.00",
            domain_id="semiconductor_electronics",
            career_level=2,
            salary_band={"krw_min": 52000000, "krw_max": 82000000, "czk_avg": 72000, "usd_avg": 115000},
            hiring_demand="increasing",
            skills=["C/C++", "RTOS", "Device Drivers", "I2C/SPI/CAN", "ARM Cortex", "JTAG Debugging"],
            value_chain_stage="RND",
            headcount_share=15.0,
            peer_staffing_index=0.95,
            wage_inflation_rate=7.2,
            automation_exposure=0.30,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["하드웨어 보드 출시 전 에뮬레이션 환경 부재", "메모리 누수 및 인터럽트 레이스"],
        ),
        RoleNode(
            role_id="2151-power-electronics-eng",
            role_name="전력전자/BMS 엔지니어 (Power Electronics)",
            isco_08="2151",
            kr_ncs="19010101",
            cz_isco="21510",
            us_onet="17-2071.00",
            domain_id="semiconductor_electronics",
            career_level=3,
            salary_band={"krw_min": 62000000, "krw_max": 98000000, "czk_avg": 82000, "usd_avg": 135000},
            hiring_demand="scarce",
            skills=["SiC/GaN Power Devices", "Inverter/Converter", "BMS Circuit", "Thermal Simulation", "EMC/EMI"],
            value_chain_stage="RND",
            headcount_share=12.0,
            peer_staffing_index=1.25,
            wage_inflation_rate=10.5,
            automation_exposure=0.12,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["고전압 발열 및 EMI 노이즈 디버깅 병목", "전력 효율 인증 규격 대응"],
        ),
        RoleNode(
            role_id="1321-fab-director",
            role_name="반도체 Fab 제조/수율 총괄 상무 (Fab Director)",
            isco_08="1321",
            kr_ncs="19020100",
            cz_isco="13210",
            us_onet="11-1021.00",
            domain_id="semiconductor_electronics",
            career_level=5,
            salary_band={"krw_min": 140000000, "krw_max": 250000000, "czk_avg": 180000, "usd_avg": 280000},
            hiring_demand="scarce",
            skills=["Fab Operations", "Yield Optimization Strategy", "CapEx Budgeting", "Supply Chain Management"],
            value_chain_stage="CORP",
            headcount_share=3.0,
            peer_staffing_index=1.05,
            wage_inflation_rate=9.8,
            automation_exposure=0.06,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["수천억 원대 클린룸 CapEx 대비 감가상각 부담", "공정 수율 1% 하락 시 수십억 손실"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2152-embedded-firmware-eng", "2152-circuit-designer", "specialization", ["Verilog", "RTL Synthesis"], ["EDA Tools"], "회로 설계 실무", 3, 25.0),
        CareerEdge("2152-process-engineer", "1321-fab-director", "vertical_promotion", ["Fab Operations", "Yield Strategy", "CapEx Mgmt"], ["Supply Chain"], "Fab 관리 10년 이상", 5, 60.0),
        CareerEdge("2152-circuit-designer", "1321-fab-director", "vertical_promotion", ["Product Roadmapping", "PPA Strategy"], ["Customer Executive"], "설계 총괄 리딩", 5, 55.0),
        CareerEdge("2151-power-electronics-eng", "1321-fab-director", "vertical_promotion", ["Operations Leadership", "Plant Safety"], ["Quality Cert"], "전력 소자 생산 총괄", 4, 45.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2152-circuit-designer",
            "2152-process-engineer",
            "테이프아웃(Tape-out) 및 PDK 룰 체크 핸드오프",
            14.0,
            "파운드리 DRC/LVS 룰 검증 반복으로 테이프아웃 일정 지연",
            {"product_name": "PDK Auto-Validator SaaS", "target_buyer": "Fab Director / Design VP", "estimated_wtp": "월 $8,000"},
        ),
        WorkflowConnection(
            "2152-process-engineer",
            "1321-fab-director",
            "주간 웨이퍼 수율 손실(Scrap) 보고 및 원인 브리핑",
            9.5,
            "수만 개 챔버 센서 시계열 데이터와 결함 이미지 간 매핑 부재",
            {"product_name": "Fab AI Yield Forensics", "target_buyer": "Fab Director / 생산본부장", "estimated_wtp": "월 $15,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_mobility_robotics_domain() -> LatticeDomainGraph:
    """Domain 3: Manufacturing / Mobility / Autonomous Robotics (NCS 15, 01)."""
    graph = LatticeDomainGraph("mobility_robotics", "Mobility, Robotics & Mechanical Engineering")
    roles = [
        RoleNode(
            role_id="2144-chassis-mechanical-eng",
            role_name="모빌리티 기계/샤시 설계 엔지니어",
            isco_08="2144",
            kr_ncs="15010101",
            cz_isco="21440",
            us_onet="17-2141.00",
            domain_id="mobility_robotics",
            career_level=2,
            salary_band={"krw_min": 52000000, "krw_max": 82000000, "czk_avg": 70000, "usd_avg": 115000},
            hiring_demand="increasing",
            skills=["3D CAD (CATIA/Creo)", "CAE/FEA", "NVH Analysis", "Crashworthiness", "GD&T"],
            value_chain_stage="RND",
            headcount_share=20.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=6.5,
            automation_exposure=0.25,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["구조 해석 시뮬레이션 대기 시간 과다", "설계 변경 시 BOM 전파 지연"],
        ),
        RoleNode(
            role_id="2144-autonomous-robotics-eng",
            role_name="자율주행/로보틱스 SW 엔지니어",
            isco_08="2144",
            kr_ncs="15020101",
            cz_isco="21440",
            us_onet="17-2199.08",
            domain_id="mobility_robotics",
            career_level=3,
            salary_band={"krw_min": 68000000, "krw_max": 115000000, "czk_avg": 92000, "usd_avg": 165000},
            hiring_demand="scarce",
            skills=["ROS/ROS2", "SLAM", "Sensor Fusion (LiDAR/Camera)", "Control Theory", "Path Planning", "C++"],
            value_chain_stage="RND",
            headcount_share=15.0,
            peer_staffing_index=1.40,
            wage_inflation_rate=13.5,
            automation_exposure=0.15,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["실차 주행 로그 데이터 인덱싱 및 엣지 케이스 재현 난항", "시뮬레이션-실차 갭(Sim2Real)"],
        ),
        RoleNode(
            role_id="2141-smart-factory-lead",
            role_name="스마트팩토리/생산기술 리드 (Smart Factory Lead)",
            isco_08="2141",
            kr_ncs="01020101",
            cz_isco="21410",
            us_onet="17-2112.00",
            domain_id="mobility_robotics",
            career_level=3,
            salary_band={"krw_min": 60000000, "krw_max": 92000000, "czk_avg": 78000, "usd_avg": 130000},
            hiring_demand="very-high",
            skills=["PLC/SCADA", "Industrial IoT", "Digital Twin", "Line Balancing", "Predictive Maintenance"],
            value_chain_stage="OPS",
            headcount_share=18.0,
            peer_staffing_index=1.15,
            wage_inflation_rate=8.2,
            automation_exposure=0.22,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["공정 라인 비계획 정지(Downtime)", "외산 로봇 제어기 프로토콜 비표준화"],
        ),
        RoleNode(
            role_id="1321-mobility-plant-vp",
            role_name="모빌리티 생산총괄 공장장 / 부사장 (Plant VP)",
            isco_08="1321",
            kr_ncs="15010100",
            cz_isco="13210",
            us_onet="11-1021.00",
            domain_id="mobility_robotics",
            career_level=5,
            salary_band={"krw_min": 130000000, "krw_max": 230000000, "czk_avg": 160000, "usd_avg": 250000},
            hiring_demand="scarce",
            skills=["Plant Management", "Lean Manufacturing", "Labor Relations", "Supply Chain Resiliency"],
            value_chain_stage="CORP",
            headcount_share=3.0,
            peer_staffing_index=0.95,
            wage_inflation_rate=8.0,
            automation_exposure=0.08,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["부품 협력사 공급망 결품 리스크", "노사 협상 및 안전 사고 책임"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2144-chassis-mechanical-eng", "2144-autonomous-robotics-eng", "specialization", ["ROS2", "SLAM", "Path Planning"], ["Sensor Fusion"], "SW 코딩 역량", 4, 35.0),
        CareerEdge("2141-smart-factory-lead", "1321-mobility-plant-vp", "vertical_promotion", ["Plant Strategy", "Labor Relations", "CapEx"], ["Supply Chain"], "공장 운영 8년 이상", 5, 55.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2144-autonomous-robotics-eng",
            "2141-smart-factory-lead",
            "물류 AMR/로봇 공장 라인 투입 및 관제 연동",
            11.0,
            "공장 무선 통신 음영 지역으로 인한 AGV 통신 두절 및 정체",
            {"product_name": "Industrial AMR Fleet Mesh QoS", "target_buyer": "생산기술팀장 / 공장장", "estimated_wtp": "월 $4,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_bio_healthcare_domain() -> LatticeDomainGraph:
    """Domain 4: Bio / Pharma / Healthcare (NCS 17, 06)."""
    graph = LatticeDomainGraph("bio_pharma_healthcare", "Bio, Pharma & Healthcare Sciences")
    roles = [
        RoleNode(
            role_id="2131-bio-discovery-scientist",
            role_name="바이오 신약 발굴 연구원 (Drug Discovery)",
            isco_08="2131",
            kr_ncs="17020101",
            cz_isco="21310",
            us_onet="19-1029.01",
            domain_id="bio_pharma_healthcare",
            career_level=2,
            salary_band={"krw_min": 55000000, "krw_max": 90000000, "czk_avg": 75000, "usd_avg": 130000},
            hiring_demand="very-high",
            skills=["Target Discovery", "Assay Development", "Protein Engineering", "CRISPR", "Bioinformatics"],
            value_chain_stage="RND",
            headcount_share=22.0,
            peer_staffing_index=1.30,
            wage_inflation_rate=9.5,
            automation_exposure=0.18,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["유효 물질 스크리닝 실패율 높음", "생물학적 실험 재현성 부족"],
        ),
        RoleNode(
            role_id="2262-clinical-trial-pm",
            role_name="임상시험 프로젝트 매니저 (Clinical Trial PM/CRA)",
            isco_08="2262",
            kr_ncs="06030101",
            cz_isco="22620",
            us_onet="11-9121.01",
            domain_id="bio_pharma_healthcare",
            career_level=3,
            salary_band={"krw_min": 65000000, "krw_max": 105000000, "czk_avg": 85000, "usd_avg": 145000},
            hiring_demand="scarce",
            skills=["GCP (Good Clinical Practice)", "Protocol Design", "IRB Submission", "EDC/CTMS", "CRO Management"],
            value_chain_stage="OPS",
            headcount_share=16.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=11.0,
            automation_exposure=0.25,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["환자 모집(Recruitment) 지연으로 인한 임상 비용 급증", "병원 IRB 승인 병목"],
        ),
        RoleNode(
            role_id="2141-gmp-qa-lead",
            role_name="의약품 GMP 품질보증 리드 (GMP QA Lead)",
            isco_08="2141",
            kr_ncs="17020102",
            cz_isco="21410",
            us_onet="19-4099.01",
            domain_id="bio_pharma_healthcare",
            career_level=3,
            salary_band={"krw_min": 60000000, "krw_max": 95000000, "czk_avg": 80000, "usd_avg": 135000},
            hiring_demand="scarce",
            skills=["cGMP", "FDA 21 CFR Part 11", "Validation (IQ/OQ/PQ)", "Audit Readiness", "Deviation Management"],
            value_chain_stage="OPS",
            headcount_share=14.0,
            peer_staffing_index=0.90,
            wage_inflation_rate=8.5,
            automation_exposure=0.15,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["수동 일탈(Deviation) 보고서 작성 및 승인 결재 병목", "배치 레코드 종이 서명 관리"],
        ),
        RoleNode(
            role_id="1342-clinical-development-vp",
            role_name="임상개발 본부장 / 부사장 (Clinical Dev VP)",
            isco_08="1342",
            kr_ncs="06010100",
            cz_isco="13420",
            us_onet="11-9111.00",
            domain_id="bio_pharma_healthcare",
            career_level=5,
            salary_band={"krw_min": 150000000, "krw_max": 280000000, "czk_avg": 190000, "usd_avg": 310000},
            hiring_demand="scarce",
            skills=["FDA/EMA Regulatory Strategy", "Pipeline Prioritization", "Licensing-Out Negotiations"],
            value_chain_stage="CORP",
            headcount_share=2.5,
            peer_staffing_index=1.00,
            wage_inflation_rate=12.5,
            automation_exposure=0.05,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["임상 2/3상 수백억 R&D 예산 소진 속도 대비 성공 불확실성", "글로벌 빅파마 LO 협상"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2131-bio-discovery-scientist", "2262-clinical-trial-pm", "specialization", ["GCP", "Clinical Protocol", "CRO Mgmt"], ["FDA Regulatory"], "임상 규정 학습", 3, 25.0),
        CareerEdge("2262-clinical-trial-pm", "1342-clinical-development-vp", "vertical_promotion", ["Regulatory Strategy", "Budget Mgmt"], ["Global Pharma Deal"], "임상 총괄 10년", 5, 60.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2262-clinical-trial-pm",
            "1342-clinical-development-vp",
            "글로벌 임상 환자 등록률 및 부작용(SAE) 즉시 보고",
            10.0,
            "다국가 병원별 이상반응 보고 포맷 불일치로 긴급 안전성 공시 지연",
            {"product_name": "Global e-Trial SAE Auto-Reporter", "target_buyer": "Clinical VP / 의학총괄", "estimated_wtp": "월 $10,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_battery_energy_domain() -> LatticeDomainGraph:
    """Domain 5: Chemical / Battery / Energy (NCS 17, 23, 16)."""
    graph = LatticeDomainGraph("chemical_battery_energy", "Chemical, Battery & Renewable Energy")
    roles = [
        RoleNode(
            role_id="2145-battery-materials-scientist",
            role_name="이차전지 양극/음극 신소재 연구원",
            isco_08="2145",
            kr_ncs="17010101",
            cz_isco="21450",
            us_onet="17-2041.00",
            domain_id="chemical_battery_energy",
            career_level=2,
            salary_band={"krw_min": 58000000, "krw_max": 92000000, "czk_avg": 76000, "usd_avg": 125000},
            hiring_demand="scarce",
            skills=["Cathode/Anode Chemistry", "Solid Electrolyte", "Half-cell Testing", "XRD/SEM", "Cyclability"],
            value_chain_stage="RND",
            headcount_share=18.0,
            peer_staffing_index=1.35,
            wage_inflation_rate=12.0,
            automation_exposure=0.15,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["새로운 배터리 소재 조성비 평가 수개월 소요", "화재/열폭주 안전성 검증"],
        ),
        RoleNode(
            role_id="2145-battery-cell-process-eng",
            role_name="배터리 셀 전극/조립 공정 엔지니어",
            isco_08="2145",
            kr_ncs="17010102",
            cz_isco="21450",
            us_onet="17-2041.00",
            domain_id="chemical_battery_energy",
            career_level=2,
            salary_band={"krw_min": 54000000, "krw_max": 86000000, "czk_avg": 72000, "usd_avg": 118000},
            hiring_demand="very-high",
            skills=["Slurry Mixing", "Coating/Calendering", "Notching/Stacking", "Formation & Aging", "Quality Control"],
            value_chain_stage="OPS",
            headcount_share=24.0,
            peer_staffing_index=1.15,
            wage_inflation_rate=9.0,
            automation_exposure=0.20,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["코팅 두께 불균일로 인한 불량률 발생", "에이징 기간 장기화로 재고 회전율 저하"],
        ),
        RoleNode(
            role_id="2143-renewable-energy-system-eng",
            role_name="신재생에너지/수소 그리드 엔지니어",
            isco_08="2143",
            kr_ncs="23010101",
            cz_isco="21430",
            us_onet="17-2199.11",
            domain_id="chemical_battery_energy",
            career_level=3,
            salary_band={"krw_min": 60000000, "krw_max": 95000000, "czk_avg": 78000, "usd_avg": 130000},
            hiring_demand="very-high",
            skills=["Microgrid", "ESS System", "Hydrogen Fuel Cell", "Power Grid Interconnection", "PPA Contract"],
            value_chain_stage="OPS",
            headcount_share=15.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=8.5,
            automation_exposure=0.18,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["기상 변동에 따른 신재생 발전량 예측 오차", "전력망 계통 연계 인허가 지연"],
        ),
        RoleNode(
            role_id="1321-battery-plant-director",
            role_name="배터리 기가팩토리 공장장 (Gigafactory Director)",
            isco_08="1321",
            kr_ncs="17010100",
            cz_isco="13210",
            us_onet="11-1021.00",
            domain_id="chemical_battery_energy",
            career_level=5,
            salary_band={"krw_min": 140000000, "krw_max": 260000000, "czk_avg": 175000, "usd_avg": 270000},
            hiring_demand="scarce",
            skills=["Gigafactory Ramp-up", "Yield Improvement", "Safety/Fire Standards", "OEM Tier-1 Contract"],
            value_chain_stage="CORP",
            headcount_share=3.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=10.0,
            automation_exposure=0.07,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["해외 공장 램프업 지연으로 인한 완성차 고객사 납기 패널티", "원자재(리튬/니켈) 가격 변동"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2145-battery-materials-scientist", "2145-battery-cell-process-eng", "horizontal_transfer", ["Coating/Calendering", "Formation"], ["Quality Eng"], "공정 엔지니어링 이해", 2, 15.0),
        CareerEdge("2145-battery-cell-process-eng", "1321-battery-plant-director", "vertical_promotion", ["Gigafactory Ramp-up", "OEM Relations"], ["Financial CapEx"], "공장 운영 10년", 5, 60.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2145-battery-cell-process-eng",
            "1321-battery-plant-director",
            "기가팩토리 라인별 수율 및 에이징 출하 보고",
            8.0,
            "전극 두께 미세 편차에 따른 불량 배치 조기 감지 실패",
            {"product_name": "Battery Cell In-line Quality AI", "target_buyer": "공장장 / 품질총괄", "estimated_wtp": "월 $8,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_business_strategy_domain() -> LatticeDomainGraph:
    """Domain 6: Management / Strategy / Business / HR (NCS 01, 02)."""
    graph = LatticeDomainGraph("management_business_hr", "Management, Strategy, Business & Human Resources")
    roles = [
        RoleNode(
            role_id="2421-strategy-analyst",
            role_name="경영기획/전략 애널리스트 (Strategic Planning)",
            isco_08="2421",
            kr_ncs="02011001",
            cz_isco="24210",
            us_onet="13-1111.00",
            domain_id="management_business_hr",
            career_level=2,
            salary_band={"krw_min": 48000000, "krw_max": 75000000, "czk_avg": 65000, "usd_avg": 105000},
            hiring_demand="increasing",
            skills=["Financial Modeling", "Corporate Strategy", "Market Sizing", "OKRs/KPIs", "M&A Screening"],
            value_chain_stage="CORP",
            headcount_share=10.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=5.5,
            automation_exposure=0.45,
            rev_per_hc_leverage="standard",
            workflow_role_type="user",
            workflow_pain_points=["각 사업부 실적 수작업 엑셀 취합", "경영진 보고용 장표 재가공 반복"],
        ),
        RoleNode(
            role_id="2423-talent-acquisition-lead",
            role_name="인재영입/인사기획 리드 (Talent Acquisition / HR)",
            isco_08="2423",
            kr_ncs="02021001",
            cz_isco="24230",
            us_onet="13-1071.00",
            domain_id="management_business_hr",
            career_level=2,
            salary_band={"krw_min": 45000000, "krw_max": 72000000, "czk_avg": 60000, "usd_avg": 95000},
            hiring_demand="very-high",
            skills=["Technical Recruiting", "Compensation & Benefits", "Labor Law Compliance", "Performance Review"],
            value_chain_stage="CORP",
            headcount_share=8.0,
            peer_staffing_index=1.05,
            wage_inflation_rate=6.8,
            automation_exposure=0.40,
            rev_per_hc_leverage="standard",
            workflow_role_type="user",
            workflow_pain_points=["핵심 기술 인재 소싱 난항", "헤드헌팅 수수료 예산 통제"],
        ),
        RoleNode(
            role_id="2421-bizops-program-pm",
            role_name="비즈옵스/프로그램 매니저 (BizOps / PM)",
            isco_08="2421",
            kr_ncs="01010201",
            cz_isco="24210",
            us_onet="11-9199.00",
            domain_id="management_business_hr",
            career_level=3,
            salary_band={"krw_min": 65000000, "krw_max": 105000000, "czk_avg": 82000, "usd_avg": 140000},
            hiring_demand="very-high",
            skills=["Cross-functional Orchestration", "Process Automation", "Cost Optimization", "SQL/Data Fluency"],
            value_chain_stage="OPS",
            headcount_share=12.0,
            peer_staffing_index=1.20,
            wage_inflation_rate=8.5,
            automation_exposure=0.30,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["사내 부서 간 업무 사일로(Silo)", "프로젝트 지연 원인 추적 난항"],
        ),
        RoleNode(
            role_id="1120-chief-operating-officer",
            role_name="최고운영책임자 (Chief Operating Officer - COO)",
            isco_08="1120",
            kr_ncs="02011000",
            cz_isco="11200",
            us_onet="11-1011.00",
            domain_id="management_business_hr",
            career_level=5,
            salary_band={"krw_min": 140000000, "krw_max": 250000000, "czk_avg": 170000, "usd_avg": 280000},
            hiring_demand="scarce",
            skills=["Enterprise Operations", "Resource Allocation", "P&L Ownership", "Executive Governance"],
            value_chain_stage="CORP",
            headcount_share=2.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=9.0,
            automation_exposure=0.08,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["부서 간 비효율 비용 증가", "전사 생산성 지표 가시성 부족"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2421-strategy-analyst", "2421-bizops-program-pm", "specialization", ["Cross-functional Orchestration", "Automation"], ["BizOps Metrics"], "실무 리딩", 2, 25.0),
        CareerEdge("2421-bizops-program-pm", "1120-chief-operating-officer", "vertical_promotion", ["P&L Ownership", "Executive Governance"], ["Board Comm"], "전사 운영 총괄", 5, 50.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2421-strategy-analyst",
            "1120-chief-operating-officer",
            "월간 전사 실적 마감 및 경영위원회 보고",
            6.5,
            "사업부별 지표 기준 불일치로 인한 경영진 회의 재작업",
            {"product_name": "Executive Unified Metrics Hub", "target_buyer": "COO / 기획조정실", "estimated_wtp": "월 $3,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_finance_investment_domain() -> LatticeDomainGraph:
    """Domain 7: Finance / Investment / Asset Mgmt / Fintech (NCS 03)."""
    graph = LatticeDomainGraph("finance_investment_fintech", "Finance, Investment & Fintech")
    roles = [
        RoleNode(
            role_id="2411-accounting-tax-manager",
            role_name="재무회계/세무 매니저 (Financial Accounting)",
            isco_08="2411",
            kr_ncs="02041001",
            cz_isco="24110",
            us_onet="13-2011.00",
            domain_id="finance_investment_fintech",
            career_level=2,
            salary_band={"krw_min": 48000000, "krw_max": 78000000, "czk_avg": 62000, "usd_avg": 100000},
            hiring_demand="increasing",
            skills=["IFRS/US-GAAP", "ERP (SAP)", "Tax Audit", "Consolidation", "Cash Flow"],
            value_chain_stage="CORP",
            headcount_share=12.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=5.0,
            automation_exposure=0.50,
            rev_per_hc_leverage="standard",
            workflow_role_type="user",
            workflow_pain_points=["분기 결산 전표 대사 수작업", "해외 자회사 연결 회계 시차"],
        ),
        RoleNode(
            role_id="2412-alternative-invest-analyst",
            role_name="대체투자/PE/VC 투자심사역 (Investment Analyst)",
            isco_08="2412",
            kr_ncs="03010101",
            cz_isco="24120",
            us_onet="13-2051.00",
            domain_id="finance_investment_fintech",
            career_level=3,
            salary_band={"krw_min": 65000000, "krw_max": 120000000, "czk_avg": 90000, "usd_avg": 160000},
            hiring_demand="very-high",
            skills=["LBO Modeling", "Due Diligence (DD)", "Valuation", "Term Sheet Negotiation", "Deal Sourcing"],
            value_chain_stage="RND",
            headcount_share=8.0,
            peer_staffing_index=1.30,
            wage_inflation_rate=10.0,
            automation_exposure=0.25,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["피투자사 실사 데이터 룸(VDR) 비정형 문서 검토 병목", "포트폴리오 사후 관리"],
        ),
        RoleNode(
            role_id="2413-fintech-quant-risk-lead",
            role_name="퀀트/리스크 모델링 리드 (Quant Risk Lead)",
            isco_08="2413",
            kr_ncs="03010201",
            cz_isco="24130",
            us_onet="13-2054.00",
            domain_id="finance_investment_fintech",
            career_level=3,
            salary_band={"krw_min": 75000000, "krw_max": 130000000, "czk_avg": 95000, "usd_avg": 175000},
            hiring_demand="scarce",
            skills=["Python/C++", "Monte Carlo", "VaR/Stress Testing", "Algorithmic Trading", "Credit Scoring"],
            value_chain_stage="RND",
            headcount_share=10.0,
            peer_staffing_index=1.20,
            wage_inflation_rate=12.0,
            automation_exposure=0.15,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["거시 경제 변동성 시뮬레이션 지연", "금융 당국 자본 적정성 규제 보고"],
        ),
        RoleNode(
            role_id="1211-chief-financial-officer",
            role_name="최고재무책임자 (Chief Financial Officer - CFO)",
            isco_08="1211",
            kr_ncs="03010100",
            cz_isco="12110",
            us_onet="11-3031.00",
            domain_id="finance_investment_fintech",
            career_level=5,
            salary_band={"krw_min": 150000000, "krw_max": 270000000, "czk_avg": 180000, "usd_avg": 300000},
            hiring_demand="scarce",
            skills=["Capital Allocation", "IPO/Fundraising Strategy", "Investor Relations (IR)", "Tax Optimization"],
            value_chain_stage="CORP",
            headcount_share=2.0,
            peer_staffing_index=0.95,
            wage_inflation_rate=9.5,
            automation_exposure=0.06,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["고금리 환경 하 자금 조달 비용 급증", "주주 및 감사인 감사 대응"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2411-accounting-tax-manager", "1211-chief-financial-officer", "vertical_promotion", ["Capital Allocation", "Fundraising", "IR"], ["M&A Financing"], "재무 총괄 10년", 5, 55.0),
        CareerEdge("2412-alternative-invest-analyst", "1211-chief-financial-officer", "vertical_promotion", ["Corporate Finance", "CapEx Strategy"], ["IR Strategy"], "투자 및 자본 조달", 4, 45.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2411-accounting-tax-manager",
            "1211-chief-financial-officer",
            "월간 자금 수지 및 차입금 상환 계획 보고",
            5.0,
            "환율 급변 시 다국적 환노출(FX Exposure) 실시간 집계 불가",
            {"product_name": "Treasury FX Realtime Hedge SaaS", "target_buyer": "CFO / 재경본부장", "estimated_wtp": "월 $5,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_marketing_sales_domain() -> LatticeDomainGraph:
    """Domain 8: Marketing / Sales / GTM / Technical Sales (NCS 10)."""
    graph = LatticeDomainGraph("marketing_sales_gtm", "Marketing, Sales & Go-To-Market")
    roles = [
        RoleNode(
            role_id="2431-performance-marketer",
            role_name="퍼포먼스/그로스 마케터 (Growth Marketer)",
            isco_08="2431",
            kr_ncs="10020101",
            cz_isco="24310",
            us_onet="13-1161.00",
            domain_id="marketing_sales_gtm",
            career_level=2,
            salary_band={"krw_min": 45000000, "krw_max": 72000000, "czk_avg": 58000, "usd_avg": 95000},
            hiring_demand="increasing",
            skills=["GA4", "SQL", "CAC/LTV Optimization", "Funnel Analytics", "Ad Spend Automation"],
            value_chain_stage="GTM",
            headcount_share=16.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=6.0,
            automation_exposure=0.45,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["광고 매체별 어트리뷰션 성과 왜곡", "서드파티 쿠키 차단에 따른 ROAS 하락"],
        ),
        RoleNode(
            role_id="2433-enterprise-sales-ae",
            role_name="엔터프라이즈 B2B 세일즈 AE (Account Executive)",
            isco_08="2433",
            kr_ncs="10010101",
            cz_isco="24330",
            us_onet="41-4011.00",
            domain_id="marketing_sales_gtm",
            career_level=3,
            salary_band={"krw_min": 65000000, "krw_max": 120000000, "czk_avg": 85000, "usd_avg": 150000},
            hiring_demand="very-high",
            skills=["MEDDPICC", "Enterprise Negotiation", "Contract Closing", "C-level Relationship", "Salesforce"],
            value_chain_stage="GTM",
            headcount_share=18.0,
            peer_staffing_index=1.15,
            wage_inflation_rate=8.5,
            automation_exposure=0.20,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="user",
            workflow_pain_points=["대기업 고객사 구매팀 결재 지연", "제안서 작성 수작업 병목"],
        ),
        RoleNode(
            role_id="1221-chief-revenue-officer",
            role_name="최고수익책임자 (Chief Revenue Officer - CRO)",
            isco_08="1221",
            kr_ncs="10010100",
            cz_isco="12210",
            us_onet="11-2022.00",
            domain_id="marketing_sales_gtm",
            career_level=5,
            salary_band={"krw_min": 140000000, "krw_max": 250000000, "czk_avg": 170000, "usd_avg": 270000},
            hiring_demand="scarce",
            skills=["Revenue Pipeline Modeling", "Territory Design", "Incentive Compensation", "Partner Ecosystem"],
            value_chain_stage="CORP",
            headcount_share=3.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=9.0,
            automation_exposure=0.08,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["분기별 세일즈 파이프라인 예측치 미달", "영업 인력 이직에 따른 고객 이탈"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2433-enterprise-sales-ae", "1221-chief-revenue-officer", "vertical_promotion", ["Revenue Modeling", "Territory Strategy"], ["Global Expansion"], "엔터프라이즈 세일즈 총괄", 4, 45.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2433-enterprise-sales-ae",
            "1221-chief-revenue-officer",
            "분기 엔터프라이즈 딜 파이프라인 예측 보고",
            5.5,
            "세일즈포스 수기 업데이트 누락으로 분기 마감 직전 파이프라인 급감",
            {"product_name": "Sales Activity Auto-Capture AI", "target_buyer": "CRO / 영업본부장", "estimated_wtp": "월 $3,500"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_legal_ip_domain() -> LatticeDomainGraph:
    """Domain 9: Legal / IP / Patent / Compliance (NCS 05)."""
    graph = LatticeDomainGraph("legal_ip_governance", "Legal, Intellectual Property & Compliance")
    roles = [
        RoleNode(
            role_id="2619-patent-attorney-ip",
            role_name="변리사 / 특허전략 스페셜리스트 (Patent Attorney)",
            isco_08="2619",
            kr_ncs="05010201",
            cz_isco="26190",
            us_onet="23-1012.00",
            domain_id="legal_ip_governance",
            career_level=3,
            salary_band={"krw_min": 70000000, "krw_max": 130000000, "czk_avg": 90000, "usd_avg": 165000},
            hiring_demand="scarce",
            skills=["Patent Prosecution", "Prior Art Search", "Freedom to Operate (FTO)", "IP Valuation", "Litigation"],
            value_chain_stage="RND",
            headcount_share=8.0,
            peer_staffing_index=1.20,
            wage_inflation_rate=9.0,
            automation_exposure=0.30,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["선행 기술 조사 및 특허 청구항 작성 수작업", "해외 특허 출원 비용 급증"],
        ),
        RoleNode(
            role_id="2611-corporate-counsel-lawyer",
            role_name="기업 사내변호사 (Corporate Legal Counsel)",
            isco_08="2611",
            kr_ncs="05010101",
            cz_isco="26110",
            us_onet="23-1011.00",
            domain_id="legal_ip_governance",
            career_level=3,
            salary_band={"krw_min": 75000000, "krw_max": 135000000, "czk_avg": 95000, "usd_avg": 170000},
            hiring_demand="very-high",
            skills=["Contract Review", "Regulatory Compliance", "M&A Legal Due Diligence", "Dispute Resolution"],
            value_chain_stage="CORP",
            headcount_share=10.0,
            peer_staffing_index=0.95,
            wage_inflation_rate=8.0,
            automation_exposure=0.35,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["매월 수백 건 영문 계약서 조항 검토 지연", "규제 변경 실시간 추적 곤란"],
        ),
        RoleNode(
            role_id="1219-general-counsel-clo",
            role_name="법무총괄 전무 (General Counsel / CLO)",
            isco_08="1219",
            kr_ncs="05010100",
            cz_isco="12190",
            us_onet="11-1011.00",
            domain_id="legal_ip_governance",
            career_level=5,
            salary_band={"krw_min": 140000000, "krw_max": 260000000, "czk_avg": 170000, "usd_avg": 290000},
            hiring_demand="scarce",
            skills=["Legal Risk Governance", "Board Advisory", "Cross-border Litigation", "Crisis Management"],
            value_chain_stage="CORP",
            headcount_share=2.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=8.5,
            automation_exposure=0.07,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["글로벌 소송 비용 통제", "주주 소송 및 반독점/공정위 리스크"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2611-corporate-counsel-lawyer", "1219-general-counsel-clo", "vertical_promotion", ["Board Advisory", "Risk Governance"], ["Crisis Mgmt"], "기업 법무 총괄 10년", 5, 50.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2611-corporate-counsel-lawyer",
            "1219-general-counsel-clo",
            "대규모 B2B 계약 면책 조항 및 법적 리스크 결재",
            4.0,
            "영문 계약서 표준 조항과의 차이점 수동 비교 지연",
            {"product_name": "Contract Redline Diff AI", "target_buyer": "법무팀장 / General Counsel", "estimated_wtp": "월 $3,000"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_construction_architecture_domain() -> LatticeDomainGraph:
    """Domain 10: Construction / Architecture / Smart Civil (NCS 14)."""
    graph = LatticeDomainGraph("construction_architecture", "Construction, Architecture & Civil Infrastructure")
    roles = [
        RoleNode(
            role_id="2161-bim-architect",
            role_name="BIM 건축설계사 (BIM Architect)",
            isco_08="2161",
            kr_ncs="14010101",
            cz_isco="21610",
            us_onet="17-1011.00",
            domain_id="construction_architecture",
            career_level=2,
            salary_band={"krw_min": 45000000, "krw_max": 75000000, "czk_avg": 62000, "usd_avg": 98000},
            hiring_demand="increasing",
            skills=["Revit/BIM", "AutoCAD", "Parametric Design (Grasshopper)", "Building Codes", "Sustainability"],
            value_chain_stage="RND",
            headcount_share=18.0,
            peer_staffing_index=1.00,
            wage_inflation_rate=5.8,
            automation_exposure=0.35,
            rev_per_hc_leverage="standard",
            workflow_role_type="user",
            workflow_pain_points=["설계 변경 시 MEP(배관/전기/공조) 간섭 충돌 체크 지연", "인허가 도면 수작업 수정"],
        ),
        RoleNode(
            role_id="2142-smart-civil-engineer",
            role_name="스마트 인프라 토목공학 엔지니어 (Civil Engineer)",
            isco_08="2142",
            kr_ncs="14020101",
            cz_isco="21420",
            us_onet="17-2051.00",
            domain_id="construction_architecture",
            career_level=3,
            salary_band={"krw_min": 52000000, "krw_max": 85000000, "czk_avg": 68000, "usd_avg": 110000},
            hiring_demand="very-high",
            skills=["Geotechnical Engineering", "Structural Analysis (MIDAS)", "Drone Surveying", "Smart Concrete"],
            value_chain_stage="OPS",
            headcount_share=22.0,
            peer_staffing_index=1.05,
            wage_inflation_rate=6.5,
            automation_exposure=0.25,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["지반 침하 위험 계측 데이터 실시간 알람 부재", "현장 시공 오차 누적"],
        ),
        RoleNode(
            role_id="1323-construction-pm-director",
            role_name="건설사업관리 총괄 상무 / 현장소장 (Construction Director)",
            isco_08="1323",
            kr_ncs="14010100",
            cz_isco="13230",
            us_onet="11-9021.00",
            domain_id="construction_architecture",
            career_level=5,
            salary_band={"krw_min": 120000000, "krw_max": 200000000, "czk_avg": 150000, "usd_avg": 220000},
            hiring_demand="scarce",
            skills=["Project Controls (Earned Value)", "Site Safety Compliance", "Subcontractor Management"],
            value_chain_stage="CORP",
            headcount_share=3.0,
            peer_staffing_index=0.95,
            wage_inflation_rate=7.0,
            automation_exposure=0.08,
            rev_per_hc_leverage="high",
            workflow_role_type="payer",
            workflow_pain_points=["공기(Schedule) 지연에 따른 지체상금 발생", "중대재해 발생 시 법적 처벌 위험"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2142-smart-civil-engineer", "1323-construction-pm-director", "vertical_promotion", ["Site Safety", "Project Controls"], ["Subcontractor Mgmt"], "현장 소장 10년", 4, 45.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2161-bim-architect",
            "2142-smart-civil-engineer",
            "3D BIM 구조 도면 및 배관 간섭 검토 핸드오프",
            7.0,
            "현장 설계 변경 사항이 본사 도면에 실시간 역반영되지 않아 재시공 발생",
            {"product_name": "Field-to-BIM Realtime Sync App", "target_buyer": "현장소장 / 시공사 PM", "estimated_wtp": "월 $2,500"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_culture_design_domain() -> LatticeDomainGraph:
    """Domain 11: Culture / Design / Media / Content (NCS 08)."""
    graph = LatticeDomainGraph("culture_design_media", "Culture, Design, Media & Content")
    roles = [
        RoleNode(
            role_id="2166-product-uiux-designer",
            role_name="프로덕트 UI/UX 디자이너 (Product Designer)",
            isco_08="2166",
            kr_ncs="08010101",
            cz_isco="21660",
            us_onet="27-1024.00",
            domain_id="culture_design_media",
            career_level=2,
            salary_band={"krw_min": 45000000, "krw_max": 75000000, "czk_avg": 60000, "usd_avg": 98000},
            hiring_demand="increasing",
            skills=["Figma", "Design Systems", "User Research", "Interaction Design", "Prototyping"],
            value_chain_stage="RND",
            headcount_share=14.0,
            peer_staffing_index=1.05,
            wage_inflation_rate=6.0,
            automation_exposure=0.40,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["디자인 시스템 컴포넌트와 개발 코드 간 괴리", "사용자 테스팅 리크루팅 지연"],
        ),
        RoleNode(
            role_id="2642-content-media-producer",
            role_name="디지털 콘텐츠/영상 프로듀서 (Media Producer)",
            isco_08="2642",
            kr_ncs="08020101",
            cz_isco="26420",
            us_onet="27-2012.00",
            domain_id="culture_design_media",
            career_level=2,
            salary_band={"krw_min": 42000000, "krw_max": 68000000, "czk_avg": 55000, "usd_avg": 88000},
            hiring_demand="increasing",
            skills=["Video Editing (Premiere/AfterEffects)", "Storyboarding", "Generative AI Video", "Motion Graphics"],
            value_chain_stage="GTM",
            headcount_share=12.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=5.5,
            automation_exposure=0.50,
            rev_per_hc_leverage="standard",
            workflow_role_type="user",
            workflow_pain_points=["다국어 현지화 영상 더빙/자막 수작업 병목", "콘텐츠 저작권 라이선스 관리"],
        ),
        RoleNode(
            role_id="1223-chief-creative-officer",
            role_name="최고크리에이티브책임자 (Chief Creative Officer - CCO)",
            isco_08="1223",
            kr_ncs="08010100",
            cz_isco="12230",
            us_onet="11-2011.00",
            domain_id="culture_design_media",
            career_level=5,
            salary_band={"krw_min": 130000000, "krw_max": 220000000, "czk_avg": 150000, "usd_avg": 240000},
            hiring_demand="scarce",
            skills=["Brand Identity Vision", "Creative Direction", "Intellectual Property Franchise"],
            value_chain_stage="CORP",
            headcount_share=2.5,
            peer_staffing_index=1.00,
            wage_inflation_rate=8.0,
            automation_exposure=0.10,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["브랜드 가치 하락 리스크", "크리에이티브 외주 비용 급증"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2166-product-uiux-designer", "1223-chief-creative-officer", "vertical_promotion", ["Brand Vision", "Creative Direction"], ["IP Franchise"], "디자인 디렉션 10년", 5, 55.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2166-product-uiux-designer",
            "1223-chief-creative-officer",
            "글로벌 브랜드 디자인 가이드라인 개정 승인",
            4.5,
            "수백 개 제품 서브브랜드 에셋 버전 동기화 실패",
            {"product_name": "Brand Asset Multi-Region Guardian", "target_buyer": "CCO / 디자인센터장", "estimated_wtp": "월 $2,500"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_environment_safety_domain() -> LatticeDomainGraph:
    """Domain 12: Environment / Industrial Safety / ESG (NCS 23)."""
    graph = LatticeDomainGraph("environment_safety_esg", "Environment, Industrial Safety & ESG")
    roles = [
        RoleNode(
            role_id="2143-carbon-neutral-eng",
            role_name="탄소중립/환경공학 엔지니어 (Environmental Engineer)",
            isco_08="2143",
            kr_ncs="23010101",
            cz_isco="21430",
            us_onet="17-2081.00",
            domain_id="environment_safety_esg",
            career_level=2,
            salary_band={"krw_min": 48000000, "krw_max": 78000000, "czk_avg": 65000, "usd_avg": 105000},
            hiring_demand="very-high",
            skills=["Carbon Accounting (Scope 1/2/3)", "LCA (Life Cycle Assessment)", "Clean Production", "Wastewater Treatment"],
            value_chain_stage="OPS",
            headcount_share=12.0,
            peer_staffing_index=1.25,
            wage_inflation_rate=8.5,
            automation_exposure=0.25,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["공급망 협력사 Scope 3 배출량 산정 데이터 누락", "탄소국경세(CBAM) 증빙 서류 작성"],
        ),
        RoleNode(
            role_id="2263-industrial-safety-manager",
            role_name="중대재해예방 산업안전보건 관리자 (Safety Manager)",
            isco_08="2263",
            kr_ncs="23020101",
            cz_isco="22630",
            us_onet="29-9011.00",
            domain_id="environment_safety_esg",
            career_level=3,
            salary_band={"krw_min": 55000000, "krw_max": 88000000, "czk_avg": 70000, "usd_avg": 115000},
            hiring_demand="scarce",
            skills=["Occupational Health & Safety (ISO 45001)", "Risk Assessment", "Hazard Identification", "Near-miss Reporting"],
            value_chain_stage="OPS",
            headcount_share=15.0,
            peer_staffing_index=1.10,
            wage_inflation_rate=10.0,
            automation_exposure=0.15,
            rev_per_hc_leverage="high",
            workflow_role_type="user",
            workflow_pain_points=["공장 현장 아차사고(Near-miss) 수기 보고 누락", "안전 보호구 미착용 실시간 적발 곤란"],
        ),
        RoleNode(
            role_id="1349-head-of-esg-sustainability",
            role_name="ESG 지속가능경영 총괄 임원 (Head of ESG)",
            isco_08="1349",
            kr_ncs="23010100",
            cz_isco="13490",
            us_onet="11-9199.00",
            domain_id="environment_safety_esg",
            career_level=5,
            salary_band={"krw_min": 130000000, "krw_max": 230000000, "czk_avg": 160000, "usd_avg": 250000},
            hiring_demand="scarce",
            skills=["ESG Disclosure (GRI/ISSB)", "EU CSRD Compliance", "Green Bond Issuance", "Board Reporting"],
            value_chain_stage="CORP",
            headcount_share=2.5,
            peer_staffing_index=1.15,
            wage_inflation_rate=9.5,
            automation_exposure=0.08,
            rev_per_hc_leverage="top-tier",
            workflow_role_type="payer",
            workflow_pain_points=["EU 공급망 실사법 위반 시 매출 5% 과징금 리스크", "글로벌 투자사 ESG 등급 하락"],
        ),
    ]
    for r in roles:
        graph.add_role(r)

    edges = [
        CareerEdge("2143-carbon-neutral-eng", "1349-head-of-esg-sustainability", "vertical_promotion", ["ESG Disclosure", "CSRD Compliance"], ["Board Reporting"], "ESG 총괄 8년", 5, 50.0),
    ]
    for e in edges:
        graph.add_career_edge(e)

    wf = [
        WorkflowConnection(
            "2143-carbon-neutral-eng",
            "1349-head-of-esg-sustainability",
            "공급망 Scope 3 탄소 배출량 연간 보고서 승인",
            6.0,
            "수백 개 협력사 배출량 데이터 취합 지연으로 글로벌 공시 기한 초과 위기",
            {"product_name": "Scope 3 Supply-Chain Carbon Ledger", "target_buyer": "ESG 본부장 / 지속가능경영실", "estimated_wtp": "월 $4,500"},
        ),
    ]
    for w in wf:
        graph.add_workflow_connection(w)

    return graph


def build_grand_unified_macro_graph() -> LatticeDomainGraph:
    """Domain 13: Grand Unified Macro Occupational Lattice connecting all 12 domains."""
    graph = LatticeDomainGraph("grand_unified", "Grand Unified National Occupational Macro Lattice")
    
    # Aggregate roles from all 12 domain graphs
    sub_graphs = [
        build_ict_domain(),
        build_semiconductor_domain(),
        build_mobility_robotics_domain(),
        build_bio_healthcare_domain(),
        build_battery_energy_domain(),
        build_business_strategy_domain(),
        build_finance_investment_domain(),
        build_marketing_sales_domain(),
        build_legal_ip_domain(),
        build_construction_architecture_domain(),
        build_culture_design_domain(),
        build_environment_safety_domain(),
    ]

    for g in sub_graphs:
        for r in g.roles.values():
            graph.add_role(r)
        for e in g.career_edges:
            graph.add_career_edge(e)
        for w in g.workflow_connections:
            graph.add_workflow_connection(w)

    # Add cross-domain mobility bridges that connect different industries!
    cross_bridges = [
        CareerEdge("2512-fullstack-dev", "2144-autonomous-robotics-eng", "horizontal_transfer", ["ROS2", "Robotics Sensors", "C++"], ["Sim2Real"], "로봇 SW 도메인 전이", 4, 30.0),
        CareerEdge("2511-data-analyst", "2413-fintech-quant-risk-lead", "horizontal_transfer", ["Financial Math", "Risk Modeling", "VaR"], ["Stochastic Calculus"], "금융 공학 도메인 전이", 4, 45.0),
        CareerEdge("2145-battery-materials-scientist", "2152-process-engineer", "horizontal_transfer", ["Cleanroom Fab", "Semiconductor Thin Film"], ["PDK Rules"], "소재-반도체 융합", 3, 20.0),
        CareerEdge("2131-bio-discovery-scientist", "2619-patent-attorney-ip", "horizontal_transfer", ["Patent Law", "Prior Art Search", "FTO"], ["Bar Exam"], "바이오 특허 변리사 전이", 4, 35.0),
        CareerEdge("2433-enterprise-sales-ae", "2433-solution-architect", "horizontal_transfer", ["Cloud Architecture", "Client PoC"], ["Hands-on Coding"], "기술 아키텍트 전이", 2, 20.0),
        CareerEdge("1330-tech-lead", "1120-chief-operating-officer", "vertical_promotion", ["P&L Ownership", "Enterprise Operations"], ["Executive Leadership"], "기술 총괄에서 전사 COO로 승진", 5, 40.0),
    ]
    for b in cross_bridges:
        graph.add_career_edge(b)

    return graph


DOMAIN_REGISTRY: dict[str, Callable[[], LatticeDomainGraph]] = {
    "ict": build_ict_domain,
    "ict_data_ai": build_ict_domain,
    "ict_software_ai": build_ict_domain,
    "semiconductor": build_semiconductor_domain,
    "semiconductor_electronics": build_semiconductor_domain,
    "mobility": build_mobility_robotics_domain,
    "mobility_robotics": build_mobility_robotics_domain,
    "manufacturing_mobility_robotics": build_mobility_robotics_domain,
    "bio": build_bio_healthcare_domain,
    "bio_pharma_healthcare": build_bio_healthcare_domain,
    "battery": build_battery_energy_domain,
    "chemical_battery_energy": build_battery_energy_domain,
    "chemical_energy_battery": build_battery_energy_domain,
    "business": build_business_strategy_domain,
    "management_business_hr": build_business_strategy_domain,
    "finance": build_finance_investment_domain,
    "finance_investment_fintech": build_finance_investment_domain,
    "marketing": build_marketing_sales_domain,
    "marketing_sales_gtm": build_marketing_sales_domain,
    "legal": build_legal_ip_domain,
    "legal_ip_governance": build_legal_ip_domain,
    "construction": build_construction_architecture_domain,
    "construction_architecture": build_construction_architecture_domain,
    "design": build_culture_design_domain,
    "culture_design_media": build_culture_design_domain,
    "environment": build_environment_safety_domain,
    "environment_safety_esg": build_environment_safety_domain,
    "all": build_grand_unified_macro_graph,
    "grand_unified": build_grand_unified_macro_graph,
}


DOMAIN_METADATA: dict[str, dict[str, str]] = {
    "ict_data_ai": {
        "name_ko": "정보통신·소프트웨어·데이터·인공지능",
        "kr_ncs_major": "20 정보통신, 02 경영·회계·사무",
        "cz_isco_major": "CZ-ISCO 25 (Specialisté v ICT), 13 (Řídící pracovníci)",
        "us_onet_major": "15-0000 Computer and Mathematical, 11-0000 Management",
    },
    "semiconductor_electronics": {
        "name_ko": "반도체·전자회로·하드웨어",
        "kr_ncs_major": "19 전기·전자",
        "cz_isco_major": "CZ-ISCO 21 (Specialisté v oblasti vědy a techniky), 13 (Řídící pracovníci)",
        "us_onet_major": "17-0000 Architecture and Engineering, 11-0000 Management",
    },
    "mobility_robotics": {
        "name_ko": "제조·기계·모빌리티·자율주행로보틱스",
        "kr_ncs_major": "15 기계, 01 사업관리",
        "cz_isco_major": "CZ-ISCO 21 (Inženýři v technice), 13 (Průmysloví ředitelé)",
        "us_onet_major": "17-0000 Architecture and Engineering, 11-0000 Management",
    },
    "bio_pharma_healthcare": {
        "name_ko": "바이오·제약·임상·의료헬스케어",
        "kr_ncs_major": "17 화학·바이오, 06 보건·의료",
        "cz_isco_major": "CZ-ISCO 21 (Biologové), 22 (Zdravotničtí specialisté), 13 (Zdravotničtí ředitelé)",
        "us_onet_major": "19-0000 Life Sciences, 29-0000 Healthcare Practitioners, 11-0000 Management",
    },
    "chemical_battery_energy": {
        "name_ko": "화학공학·이차전지·배터리·신재생에너지",
        "kr_ncs_major": "17 화학·바이오, 23 환경·에너지, 16 재료",
        "cz_isco_major": "CZ-ISCO 21 (Chemici a energetičtí inženýři), 13 (Průmysloví ředitelé)",
        "us_onet_major": "17-0000 Architecture and Engineering, 19-0000 Physical Sciences",
    },
    "management_business_hr": {
        "name_ko": "경영전략·사업관리·인사조직",
        "kr_ncs_major": "01 사업관리, 02 경영·회계·사무",
        "cz_isco_major": "CZ-ISCO 24 (Specialisté v obchodní sféře), 11 (Zákonodárci a ředitelé)",
        "us_onet_major": "13-0000 Business Operations, 11-0000 Management",
    },
    "finance_investment_fintech": {
        "name_ko": "금융·투자·자산운용·핀테크·재무회계",
        "kr_ncs_major": "03 금융·보험, 02 경영·회계·사무",
        "cz_isco_major": "CZ-ISCO 24 (Finanční a investiční specialisté), 12 (Finanční ředitelé)",
        "us_onet_major": "13-0000 Business and Financial, 11-0000 Management",
    },
    "marketing_sales_gtm": {
        "name_ko": "마케팅·B2B기술영업·GTM·수익창출",
        "kr_ncs_major": "10 영업·판매, 08 문화·예술·디자인·방송",
        "cz_isco_major": "CZ-ISCO 24 (Specialisté marketingu a obchodu), 12 (Obchodní ředitelé)",
        "us_onet_major": "41-0000 Sales, 13-0000 Market Research, 11-0000 Management",
    },
    "legal_ip_governance": {
        "name_ko": "법률·변리·특허·지식재산·컴플라이언스",
        "kr_ncs_major": "05 법률·경찰·소방",
        "cz_isco_major": "CZ-ISCO 26 (Právní specialisté), 12 (Právní ředitelé)",
        "us_onet_major": "23-0000 Legal, 11-0000 Management",
    },
    "construction_architecture": {
        "name_ko": "건축설계·스마트토목·도시인프라",
        "kr_ncs_major": "14 건설, 15 기계",
        "cz_isco_major": "CZ-ISCO 21 (Stavební architekti a inženýři), 13 (Stavební ředitelé)",
        "us_onet_major": "17-0000 Architecture and Engineering, 11-0000 Construction Managers",
    },
    "culture_design_media": {
        "name_ko": "프로덕트디자인·미디어·디지털콘텐츠",
        "kr_ncs_major": "08 문화·예술·디자인·방송",
        "cz_isco_major": "CZ-ISCO 21 (Grafici), 26 (Producenti), 12 (Kreativní ředitelé)",
        "us_onet_major": "27-0000 Arts, Design, Entertainment, 11-0000 Management",
    },
    "environment_safety_esg": {
        "name_ko": "탄소중립·환경공학·중대재해예방산업안전·ESG",
        "kr_ncs_major": "23 환경·에너지·안전, 06 보건·의료",
        "cz_isco_major": "CZ-ISCO 21 (Environmentální inženýři), 22 (Specialisté bezpečnosti), 13 (Ředitelé)",
        "us_onet_major": "17-0000 Environmental Engineering, 29-0000 Occupational Safety, 11-0000 Management",
    },
    "grand_unified": {
        "name_ko": "전체 국가 직무 대통합 매크로 격자망 (12대 산업 전수 통합)",
        "kr_ncs_major": "24개 대분류 전수 (01 사업관리 ~ 24 농림어업)",
        "cz_isco_major": "CZ-ISCO 1~9 전수 (Zákonodárci ~ Pomocní pracovníci)",
        "us_onet_major": "O*NET 23개 메이저 그룹 전수 (11-0000 ~ 55-0000)",
    },
}


def get_domain_graph(domain_id: str = "all") -> LatticeDomainGraph:
    """Resolve and build domain graph by canonical ID or alias."""
    builder = DOMAIN_REGISTRY.get(domain_id.lower().strip())
    if not builder:
        supported = ", ".join(sorted(set(DOMAIN_METADATA.keys())))
        raise ValueError(f"알 수 없는 직무 분야(domain)입니다: '{domain_id}'. 지원 분야: {supported}")
    return builder()
