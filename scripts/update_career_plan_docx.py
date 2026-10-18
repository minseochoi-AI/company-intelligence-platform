"""
Script: update_career_plan_docx.py
Purpose: Update 'docs/99. 진로계획서.docx' with high-density, rigorously grounded
career plan content for Track 1 (Public ICT/Cloud) and Track 2 (Big Data/Energy Risk),
integrating the 6 master Excel datasets, patent strategy, and dual-market employment roadmap.
"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path('/home/ubuntu/root/company-intelligence-platform')
DOCX_PATH = PROJECT_ROOT / 'docs/99. 진로계획서.docx'
BACKUP_PATH = PROJECT_ROOT / 'docs/99. 진로계획서_backup.docx'

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"

NAMESPACES = {
    'w': W_NS,
    'w14': W14_NS
}

# Register namespaces so ET doesn't generate ns0/ns1 prefixes
ET.register_namespace('w', W_NS)
ET.register_namespace('w14', W14_NS)


def make_p(text: str, bold=False, size_pt=9, align='left', color=None, space_after=60):
    """Create a Word paragraph element."""
    p = ET.Element(f'{{{W_NS}}}p')
    pPr = ET.SubElement(p, f'{{{W_NS}}}pPr')
    
    if align != 'left':
        jc = ET.SubElement(pPr, f'{{{W_NS}}}jc')
        jc.attrib[f'{{{W_NS}}}val'] = align
        
    sp = ET.SubElement(pPr, f'{{{W_NS}}}spacing')
    sp.attrib[f'{{{W_NS}}}after'] = str(space_after)
    sp.attrib[f'{{{W_NS}}}line'] = '240'
    sp.attrib[f'{{{W_NS}}}lineRule'] = 'auto'
    
    r = ET.SubElement(p, f'{{{W_NS}}}r')
    rPr = ET.SubElement(r, f'{{{W_NS}}}rPr')
    
    fonts = ET.SubElement(rPr, f'{{{W_NS}}}rFonts')
    fonts.attrib[f'{{{W_NS}}}ascii'] = 'Malgun Gothic'
    fonts.attrib[f'{{{W_NS}}}eastAsia'] = 'Malgun Gothic'
    fonts.attrib[f'{{{W_NS}}}hAnsi'] = 'Malgun Gothic'
    
    if bold:
        ET.SubElement(rPr, f'{{{W_NS}}}b')
        
    sz = ET.SubElement(rPr, f'{{{W_NS}}}sz')
    sz.attrib[f'{{{W_NS}}}val'] = str(int(size_pt * 2))
    
    if color:
        c = ET.SubElement(rPr, f'{{{W_NS}}}color')
        c.attrib[f'{{{W_NS}}}val'] = color
        
    t = ET.SubElement(r, f'{{{W_NS}}}t')
    t.text = text
    return p


def make_heading(text: str, level=1):
    """Create a heading paragraph."""
    size = 14 if level == 1 else (12 if level == 2 else 10.5)
    color = "1F4E78" if level == 1 else "2E75B6"
    return make_p(text, bold=True, size_pt=size, align='left', color=color, space_after=120)


def populate_table_cell(tc, lines, size_pt=8.5, bold_first=False):
    """Clear text paragraphs in cell and insert new formatted paragraphs."""
    tcPr = tc.find(f'{{{W_NS}}}tcPr')
    # Keep tcPr and remove everything else
    children = list(tc)
    for ch in children:
        if ch != tcPr:
            tc.remove(ch)
            
    for idx, line in enumerate(lines):
        is_bold = bold_first and (idx == 0)
        p = make_p(line, bold=is_bold, size_pt=size_pt, align='left', space_after=40)
        tc.append(p)


def update_docx():
    # Ensure backup exists
    if not BACKUP_PATH.exists():
        shutil.copy(DOCX_PATH, BACKUP_PATH)

    # Read document.xml from docx zip
    with zipfile.ZipFile(DOCX_PATH, 'r') as zin:
        xml_bytes = zin.read('word/document.xml')
        all_files = {item.filename: zin.read(item.filename) for item in zin.infolist()}

    tree = ET.fromstring(xml_bytes)
    body = tree.find('.//w:body', NAMESPACES)

    # Update Title and Info Paragraphs
    paragraphs = body.findall('w:p', NAMESPACES)
    if len(paragraphs) >= 2:
        # P0: Title
        p0 = paragraphs[0]
        for t in p0.iter(f'{{{W_NS}}}t'):
            t.text = "공기업(국내·체코·슬로바키아) IT경영 듀얼트랙 진로계획서"

        # P1: Info Header
        p1 = paragraphs[1]
        p1_r = p1.find(f'{{{W_NS}}}r')
        if p1_r is not None:
            for t in p1_r.iter(f'{{{W_NS}}}t'):
                t.text = (
                    "학부 전공: IT경영학부 (학사형 기본 / 한국공학대 경영대학원 석박사 확장형)   |   성명: 지원자\n"
                    "목표기업: [트랙 1] 한전KDN, NIA, 한국도로공사 / 체코 기술청(TA ČR), 슬로바키아 NASES\n"
                    "          [트랙 2] 전력거래소(KPX), 한국전력공사 / 체코 ČEZ, OTE, 슬로바키아 SEPS\n"
                    "지원직무: 공공 ICT·클라우드 인프라(트랙 1) 및 빅데이터·에너지리스크 분석(트랙 2)"
                )

    # Get Table 0
    table = body.find('.//w:tbl', NAMESPACES)
    rows = table.findall('w:tr', NAMESPACES)

    # Table 0 Content Matrix (Row 1 to 15)
    # Each row maps to [요구사항, 현재 상황, Gap, 해결방안]
    table_data = {
        1: { # 전공능력
            'req': [
                "• IT경영(MIS) + 분산 클라우드 아키텍처 및 전력망 계통 데이터 분석 융합 역량",
                "• 공공 전산망 ERP 운영 및 대규모 시계열 트랜잭션 처리 구조 이해"
            ],
            'cur': [
                "• IT경영학부 전공으로 경영정보 및 기본 프로그래밍/데이터베이스 원론 이수"
            ],
            'gap': [
                "• 공공 클라우드(DevOps/K8s) 엔터프라이즈 실무 및 전력시장(KPX/ENTSO-E) 정산 공식 지식 부족"
            ],
            'sol': [
                "• 'KPX-ENTSO-E 듀얼 전력거래비용 멀티에이전트' 프로젝트 직접 개발",
                "• 한국공학대 경영대학원(MOT/데이터사이언스) 연계를 통한 전문성 심화"
            ]
        },
        2: { # 자격증
            'req': [
                "• 한국: 정보처리기사(필수 가점), CISA(전문자격 최고 가점), SQLD, 한국사 1급, 컴활 1급",
                "• 유럽: AWS SAA / CKA (DevOps 필수 우대), CISA (EU NIS2 보안지침 법정 필수 우대)"
            ],
            'cur': [
                "• 기본 공통 자격증 및 학부 전공 학점 이수 진행 중"
            ],
            'gap': [
                "• 양국 공기업 서류 만점 가산점 및 유럽 보안책임자 법정 자격(CISA) 미보유"
            ],
            'sol': [
                "• 상반기: 정보처리기사 + AWS SAA 취득 (양국 트랙 1·2 서류 가점 완성)",
                "• 하반기: CISA(IT감사/정보보안) 취득으로 한전KDN/NIA 및 유럽 NIS2 보안자격 동시 석권"
            ]
        },
        3: { # 어학능력
            'req': [
                "• 한국: TOEIC 850점 이상 (공기업 서류전형 만점선)",
                "• 유럽: 실무 비즈니스 영어 B2/C1 (ČEZ, TA ČR 기술면접 필수) + 체코어 A2 (거주증 및 공공결재 우대)"
            ],
            'cur': [
                "• 기초 공인영어 성적 보유 및 일반 일상 회화 가능"
            ],
            'gap': [
                "• 기술 아키텍처 PT용 비즈니스 영어 유창성 및 체코어 행정소통 기초 능력 부족"
            ],
            'sol': [
                "• 3개월 내 TOEIC 850+ 달성으로 국내 공기업 서류 만점 확보",
                "• 영어 기술면접 스크립트 숙달 및 체코어 초급(A2) 자격 취득으로 현지 면접 차별화"
            ]
        },
        4: { # 실무경험
            'req': [
                "• 공공 전산망/에너지 공기업 실시간 API 연동 파이프라인 구축 경험",
                "• 15분 단위 실시간 시장 시계열 결측치 보정 및 멀티에이전트 오케스트레이션"
            ],
            'cur': [
                "• 학부 캡스톤 프로젝트 수준의 웹/DB 구축 경험 보유"
            ],
            'gap': [
                "• 국가 기간망급 실시간 데이터 파이프라인 및 원전 기저부하 연계 실증 프로젝트 부재"
            ],
            'sol': [
                "• KPX ↔ ENTSO-E/OTE 듀얼 전력거래비용 & 탄소배출권 멀티에이전트 오픈소스 구축",
                "• Modbus 가상 스마트 전력계측(AMI) 엣지 레이어 연동으로 하드웨어 Moat 확보"
            ]
        },
        5: { # 컴퓨터능력
            'req': [
                "• Python (FastAPI, Celery), PostgreSQL (시계열), Docker/Kubernetes, LangGraph",
                "• 리눅스 서버(Ubuntu/CentOS) 환경 제어 및 공공 보안 프로토콜 운용"
            ],
            'cur': [
                "• Python 기본 문법 및 SQL 쿼리 작성 가능"
            ],
            'gap': [
                "• 컨테이너 오케스트레이션(K8s) 및 분산 상태 머신(State Graph) 실무 구현력 부족"
            ],
            'sol': [
                "• CKA 자격증 실기 환경에서 Docker/K8s 클러스터 직접 구축 및 에이전트 서비스 배포",
                "• GitOps 기반 CI/CD 파이프라인 자동화"
            ]
        },
        6: { # 기타 (지식재산권/특허)
            'req': [
                "• 역공학 및 코드 도용을 원천 차단하고 기술적 독창성을 입증하는 지식재산권(특허)",
                "• 학술 연구 실적 (KCI/학회 논문)"
            ],
            'cur': [
                "• 지식재산권 및 논문 실적 전무"
            ],
            'gap': [
                "• 공기업 서류·면접 시 타 지원자를 압도할 수 있는 독점적 기술 증빙 수단 부재"
            ],
            'sol': [
                "• '체코 원전 기저부하-시장가격 감응형 섹터커플링 차익거래 멀티에이전트' 국내 특허 출원",
                "• 출원번호 확보 후 한국정보처리학회/KCI 등재지에 논문 게재하여 연구 공인 획득"
            ]
        },
        7: { # 성격/자질
            'req': [
                "• 공공 인프라를 지탱하는 투철한 직업윤리, 데이터 무결성 추구, 위기대응 탄력성"
            ],
            'cur': [
                "• 성실한 과제 수행력 및 원만한 대인관계 보유"
            ],
            'gap': [
                "• 공공 서비스 장애 및 감사 지적 상황에서의 시스템적 리질리언스(회복력) 마인드셋 부족"
            ],
            'sol': [
                "• 공공 데이터 무결성 검증 프로토콜(SHA-256 감사추적) 구현을 통해 꼼꼼함 체화",
                "• IT 변경관리(Change Control) 절차 숙지"
            ]
        },
        8: { # 인재상
            'req': [
                "• 한국: 한전KDN 창의인재, NIA 디지털혁신인재, KPX 스마트융합인재",
                "• 유럽: ČEZ 지속가능성 혁신가, TA ČR R&D 정책 추진가"
            ],
            'cur': [
                "• 단순 기술 구현 중심의 사고방식"
            ],
            'gap': [
                "• 공공 정책 목표(에너지 안보, 디지털 정부)와 소프트웨어 기술을 연결하는 거시적 안목 부족"
            ],
            'sol': [
                "• 공공기관 경영평가 보고서 및 체코 국가에너지계획(SEK) 분석을 통한 기관 맞춤형 가치관 수립"
            ]
        },
        9: { # 기업문화
            'req': [
                "• 청렴/보안 규정(개인정보보호법, NIS2 지침) 준수 및 글로벌 다문화 협업 마인드"
            ],
            'cur': [
                "• 국내 학부 중심의 문화적 경험에 국한"
            ],
            'gap': [
                "• 유럽 공기업의 수평적/자율적 업무 문화 및 EU 법정 규제 실무 이해 미흡"
            ],
            'sol': [
                "• 글로벌 오픈소스 커뮤니티 기여 및 체코/슬로바키아 현지 공기업 인터뷰 사례 분석"
            ]
        },
        10: { # 기타 태도
            'req': [
                "• 이종 산업(원자력-IT-전력금융) 간 장벽을 허무는 융합적 탐구 태도"
            ],
            'cur': [
                "• IT 전공 내 지식 습득에 치중"
            ],
            'gap': [
                "• 에너지 기저부하 물리적 특성과 금융 파생/배출권 시장 메커니즘 융합 능력 부족"
            ],
            'sol': [
                "• 한국공학대 경영대학원 MOT(기술경영) 산학 세미나 참여를 통해 융합 시야 확장"
            ]
        },
        11: { # 졸업여부어학/학점
            'req': [
                "• 학사형: 4년제 IT경영학 학사 (한국 423건 / 체코 175건 / 슬로바키아 10건 지원 가능)",
                "• 석박사 확장형: 한국공학대 경영대학원 석사 이상 (한국 107건 / 체코 21건 / 슬로바키아 5건 국가연구소)"
            ],
            'cur': [
                "• 학부 4년제 졸업 예정 (학점 3.8/4.5 수준)"
            ],
            'gap': [
                "• 석박사 전용 국가 연구기관(체코 ÚTIA, 슬로바키아 SAV 등) 지원 자격 미충족"
            ],
            'sol': [
                "• 학사 졸업 즉시 트랙 1·2 공기업 공채 합격 목표",
                "• 입사 후 한국공학대 경영대학원(석박사 MOT) 진학으로 EU Blue Card 연구원 트랙 병행"
            ]
        },
        12: { # 서류전형
            'req': [
                "• 직무기술서(NCS/CZ-ISCO) 키워드 100% 매칭, 가산점 만점, 포트폴리오 URL 증빙"
            ],
            'cur': [
                "• 일반 표준 자기소개서 초안 보유"
            ],
            'gap': [
                "• 공기업 직무기술서에 맞춤화된 직무수행계획서 및 영문 Europass CV 부재"
            ],
            'sol': [
                "• 6대 엑셀 분석 데이터 기반 한국 공기업 NCS 직무기술서 1:1 매칭 자기소개서 완성",
                "• 체코·슬로바키아 공기업 제출용 영문 Europass CV 및 GitHub 리포지토리 구축"
            ]
        },
        13: { # 인성/직무적성검사
            'req': [
                "• 한국 공기업 NCS 직무능력평가(수리/문제해결/자원관리) 및 전산/경영 전공필기 통과"
            ],
            'cur': [
                "• NCS 문제 유형 기본 파악 단계"
            ],
            'gap': [
                "• 필기시험 합격선(상위 5~10%) 대비 시간 관리 및 고난도 수리/자원관리 해결력 부족"
            ],
            'sol': [
                "• 매일 2시간 NCS 모듈형/PSAT형 기출 풀이 루틴화",
                "• 전산직/경영직 전공 필기 요약노트 단권화"
            ]
        },
        14: { # 면접(인성/PT/영어)
            'req': [
                "• 직무수행계획 PT면접, 기술 아키텍처 구술면접, 영어 실무인터뷰, 다대일 인성면접"
            ],
            'cur': [
                "• 면접 실전 경험 부족"
            ],
            'gap': [
                "• 듀얼 멀티에이전트 아키텍처 및 특허 기술을 5분 내로 명쾌하게 브리핑하는 전달력 부족"
            ],
            'sol': [
                "• 듀얼 멀티에이전트 아키텍처 다이어그램 기반 5분 PT 발표 스크립트 작성 및 모의면접",
                "• 영어 기술 인터뷰 100대 예상 Q&A 완벽 숙달"
            ]
        },
        15: { # 기타 채용절차
            'req': [
                "• 공공기관 결격사유 조회 통과 및 체코/슬로바키아 취업비자(EU Blue Card) 발급 요건 충족"
            ],
            'cur': [
                "• 신원 및 결격사유 없음"
            ],
            'gap': [
                "• 유럽 공공기관 외국인 고용허가 절차 및 학위 아포스티유 인증 프로세스 미인지"
            ],
            'sol': [
                "• 체코 노동사회부(MPSV) 고용허가 면제 트랙 요건 사전 확인 및 공증 서류 패키징 완료"
            ]
        }
    }

    # Populate table rows
    for r_idx, r_data in table_data.items():
        if r_idx < len(rows):
            row = rows[r_idx]
            cells = row.findall('w:tc', NAMESPACES)
            # cells: [0: cat, 1: subcat, 2: req, 3: cur, 4: gap, 5: sol]
            if len(cells) >= 6:
                populate_table_cell(cells[2], r_data['req'], size_pt=8.0)
                populate_table_cell(cells[3], r_data['cur'], size_pt=8.0)
                populate_table_cell(cells[4], r_data['gap'], size_pt=8.0)
                populate_table_cell(cells[5], r_data['sol'], size_pt=8.0)

    # Now, append detailed strategy sections before the last sectPr
    sectPr = body.find('w:sectPr', NAMESPACES)

    # Detailed chapters to add
    new_elements = []

    # Section 1
    new_elements.append(make_p("", space_after=180))
    new_elements.append(make_heading("1. 4대 트랙별 기회비용 분석 및 트랙 1·2 집중 전략", level=1))
    new_elements.append(make_p(
        "본 진로계획서는 한국과 체코·슬로바키아 양국의 공기업 채용 구조를 1:1로 결속하여, 동일한 준비(자격증·포트폴리오·어학)로 "
        "기회비용 소모 없이 양국 공기업에 동시 입사할 수 있는 최적의 듀얼트랙을 정의합니다.",
        size_pt=9.5, space_after=80
    ))
    new_elements.append(make_p(
        "• [트랙 1: 공공 ICT·클라우드 인프라] - 트랙분리도 '매우 낮음 (★ 베스트)'\n"
        "   - 한국 타겟: 한전KDN, 한국지능정보사회진흥원(NIA), 한국도로공사, 국민건강보험공단 전산직\n"
        "   - 유럽 타겟: 체코 기술청(TA ČR), 슬로바키아 국가전자서비스청(NASES), 슬로바키아 철도공사(ŽSR)\n"
        "   - 준비 일치도: 90% 이상. AWS/CKA/리눅스/Python 역량은 양국 공기업의 요구사항이 100% 동일함.\n"
        "   - 기회비용: 포트폴리오 1개로 양국 공기업 전산직 서류 및 면접을 동시에 통과 가능.",
        size_pt=9.0, space_after=60
    ))
    new_elements.append(make_p(
        "• [트랙 2: 빅데이터·에너지리스크 분석] - 트랙분리도 '낮음 (우수)'\n"
        "   - 한국 타겟: 전력거래소(KPX), 한국전력공사, 발전 5사, 한국지역난방공사, 한국가스공사\n"
        "   - 유럽 타겟: 체코 전력공사(ČEZ), 체코 전력거래소(OTE), 슬로바키아 전력망공사(SEPS), 슬로바키아 가스공사(SPP)\n"
        "   - 준비 일치도: 85%. 시계열 DB(PostgreSQL), 전력거래 데이터 분석, 에너지 통계 모델링 역량이 공통 적용됨.\n"
        "   - 시너지: 한국 전공필기 준비와 병행하되, 유럽 실무 포트폴리오(KPX-ENTSO-E 연동 엔진)로 면접을 압도.",
        size_pt=9.0, space_after=100
    ))

    # Section 2
    new_elements.append(make_heading("2. 체코 두코바니 신규 원전 계약 연계 원자력-시장 듀얼 특허 설계안", level=1))
    new_elements.append(make_p(
        "체코 정부와 팀코리아 간의 두코바니 5·6호기 신규 원전 수주 계약에 발맞추어, 원전의 물리적 기저부하(Inflexible Baseload)와 "
        "유럽 전력시장(OTE)의 마이너스 전기요금 충격을 IT 알고리즘으로 해결하는 '한·유럽 연동 특허'를 포트폴리오의 핵심 Moat로 삼습니다.",
        size_pt=9.5, space_after=80
    ))
    new_elements.append(make_p(
        "• 발명의 명칭: 원자력 기저부하 발전원의 시장 가격 감응형 섹터 커플링 자원 배분 제어 및 다국가 전력망 보조서비스 정산 최적화 멀티에이전트 시스템 및 방법\n"
        "• 기술적 과제: 마이너스 전기요금 발생 시 원자로를 감발하지 않고, 잉여 전력을 축열시스템(TES) 지역난방, 핑크수소(HTSE) 수전해, BESS로 자동 우회 분배하여 정산 손실 방지.\n"
        "• 핵심 청구항 1 (장치/시스템): 비동기 다국가 API 수집부 + 15분 단위 가격 급락 예측 에이전트 + 섹터 커플링 제어 에이전트 + 보조서비스(FCR/aFRR) 정산 토큰 발행부.\n"
        "• 핵심 청구항 2 (알고리즘 방법): 손실 비용 및 수전해/축열 변환 효율 손실을 최소화하는 파레토 프론티어 다목적 최적화 스케줄링 단계.\n"
        "• 공기업 어필: 한수원(KHNP) 디지털혁신실 및 체코 ČEZ 신규원전 IT팀 면접에서 대체 불가능한 '원전-에너지IT 융합 인재'로 각인.",
        size_pt=9.0, space_after=100
    ))

    # Section 3
    new_elements.append(make_heading("3. 6대 마스터 엑셀 공고 실증 분석 및 물리적 증거 (100% 무결성 검증)", level=1))
    new_elements.append(make_p(
        "본 계획서는 임의의 가정이 아닌, 리포지토리 내 6대 마스터 엑셀 파일(학사형 608건 + 대학원 연구직 133건, 총 741건)의 "
        "전수 공고 데이터를 물리적으로 분석하여 도출되었습니다.",
        size_pt=9.5, space_after=80
    ))
    new_elements.append(make_p(
        "1. korea-public-sector-it-management-jobs.xlsx (한국 기본 학사형 | 423건 | 100% PASS)\n"
        "   - 한전KDN(AMI/전력통신 21건), 한국도로공사 일반직, 국민건강보험공단 전산직 수록.\n"
        "2. czech-public-sector-it-management-jobs.xlsx (체코 프라하 기본 학사형 | 175건 | 100% PASS)\n"
        "   - 체코 기술청(TA ČR), 에네르고트란스(ČEZ 산하), 국세청, 관세청, 고용청 등 프라하(CZ0100) 공공 IT 전수 수록.\n"
        "3. slovakia-public-sector-it-management-jobs.xlsx (슬로바키아 브라티슬라바 기본 학사형 | 10건 | 100% PASS)\n"
        "   - 슬로바키아 철도공사(ŽSR), 국가전자서비스청(NASES), 전력망공사(SEPS), 국영가스공사(SPP) 수록.\n"
        "4. korea-graduate-rd-it-management-jobs.xlsx (한국 대학원 석박사 확장 연구직 | 107건 | 100% PASS)\n"
        "   - 한국지능정보사회진흥원(NIA), 정보통신정책연구원 등 국가 국책연구원 R&D 공고 수록.\n"
        "5. czech-prague-graduate-rd-it-management-jobs.xlsx (체코 프라하 대학원 석박사 확장 연구직 | 21건 | 100% PASS)\n"
        "   - 체코 국립정보이론및자동화연구소(ÚTIA), 국립공과대(ČVUT) 석박사 연구원 공고 수록.\n"
        "6. slovakia-bratislava-graduate-rd-it-management-jobs.xlsx (슬로바키아 브라티슬라바 대학원 연구직 | 5건 | 100% PASS)\n"
        "   - 슬로바키아 국립과학원(SAV) 정보학연구소, 국립공과대(STU) 스마트제조 전임연구원 수록.",
        size_pt=9.0, space_after=100
    ))

    # Section 4
    new_elements.append(make_heading("4. 통합 자격증·어학·특허 취득 로드맵 및 채용 타임라인", level=1))
    new_elements.append(make_p(
        "• 1단계 (1~3개월): 기본 서류 만점 베이스 구축\n"
        "   - TOEIC 850점 달성 (한국 공기업 서류 만점선 확보)\n"
        "   - 정보처리기사 필기/실기 합격 (국내 전산직 필수 5~10점 가점)\n"
        "   - 컴퓨터활용능력 1급 및 한국사능력검정시험 1급 완비\n"
        "• 2단계 (4~6개월): 킬러 포트폴리오 및 클라우드 자격증\n"
        "   - AWS Certified Solutions Architect (Associate) 취득\n"
        "   - 'KPX ↔ ENTSO-E/OTE 듀얼 멀티에이전트' GitHub 오픈소스 배포 및 Docker/K8s 배포\n"
        "   - '원자력 기저부하-시장연계 멀티에이전트' 특허청 국내 가출원(출원번호 확보)\n"
        "• 3단계 (7~9개월): 최고급 전문자격 및 연구 공인 확보\n"
        "   - CISA (국제공인 정보시스템 감사사) 취득 (한전KDN/금융권 최고 가산점 + EU NIS2 법정 보안우대)\n"
        "   - 특허 명세서 기반 KCI 등재지 논문 투고 및 게재 확정\n"
        "   - 체코어 A2 자격 취득 및 비즈니스 영어 PT 스크립트 완성\n"
        "• 4단계 (10~12개월): 양국 공기업 동시 공채 지원 및 면접\n"
        "   - 국내: 한전KDN, NIA, 전력거래소, 한국도로공사 공채 지원 (서류 만점 + 특허/논문 제출)\n"
        "   - 유럽: 체코 TA ČR, ČEZ, 슬로바키아 NASES 영문 Europass 지원 및 면접 (EU Blue Card 패스트트랙 발급)",
        size_pt=9.0, space_after=120
    ))

    # Insert all new elements right before sectPr
    sectPr_idx = list(body).index(sectPr)
    for elem in reversed(new_elements):
        body.insert(sectPr_idx, elem)

    # Convert tree back to XML
    new_xml = ET.tostring(tree, encoding='utf-8', xml_declaration=True)

    # Re-pack docx zip
    all_files['word/document.xml'] = new_xml
    with zipfile.ZipFile(DOCX_PATH, 'w', zipfile.ZIP_DEFLATED) as zout:
        for fname, data in all_files.items():
            zout.writestr(fname, data)

    print(f"Successfully updated {DOCX_PATH}!")


if __name__ == '__main__':
    update_docx()
