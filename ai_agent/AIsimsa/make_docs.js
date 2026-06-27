const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, Table, TableRow, TableCell,
  WidthType, VerticalAlign, ShadingType
} = require("docx");
// Table/TableRow/TableCell/WidthType/VerticalAlign/ShadingType/BorderStyle은 문서1에서 사용
const fs = require("fs");

// ======================================================
// 문서 1: 심사비평 전문 (저자 제공용 첨부파일)
// ======================================================
function makeFullCritique() {
  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          text: "논문 심사 비평 보고서",
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "논문 제목: ", bold: true }),
            new TextRun("Thiol-Epoxy 클릭 화학 기반 고분자 합성 및 계면 소재 연구 동향"),
          ],
          spacing: { before: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "논문 ID: ", bold: true }),
            new TextRun("JAIK-2026-005"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "투고 저널: ", bold: true }),
            new TextRun("접착 및 계면 (Journal of Adhesion and Interface)"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "심사 구분: ", bold: true }),
            new TextRun("리뷰 논문 (Review Article)"),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "심사일: ", bold: true }),
            new TextRun("2026-05-23"),
          ],
          spacing: { after: 300 },
        }),

        // 1. 논문 요약
        new Paragraph({ text: "1. 논문 요약", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({
          text: "본 논문은 thiol-epoxy 클릭 반응의 반응 메커니즘과 합성 전략, 그리고 이를 활용한 기능성 고분자 및 계면 소재 연구 동향을 정리한 리뷰 논문이다. 저자들은 Barner-Kowollik의 click-like 반응성 4대 기준(높은 반응 효율, 위치선택적 개환, 온화하고 다양한 반응 조건, 1:1 화학양론 정밀성)을 분석 프레임으로 삼아 thiol-epoxy 반응이 클릭 화학 범주에 부합함을 논증한다. 이어 poly(glycidyl methacrylate) 측쇄 기능화, 다양한 구조의 poly(β-hydroxy thioether) 합성, β-hydroxy thioether의 hydroxyl/sulfur 후속 기능화(esterification, alkylation), 표면 광중합 및 패터닝 응용을 차례로 다룬다. 결론적으로 thiol-epoxy 반응이 양친매성 homopolymer, sulfonium계 항균 고분자, antibiofouling zwitterionic 표면 등 다양한 기능성 소재 설계 플랫폼으로 확장 가능함을 제시한다.",
          spacing: { after: 200 },
        }),

        // 2. 주요 강점
        new Paragraph({ text: "2. 주요 강점", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({ children: [new TextRun({ text: "(1) 리뷰 프레임의 명확성", bold: true })] }),
        new Paragraph({ text: "Barner-Kowollik의 click-like 4대 기준을 일관된 분석 축으로 채택하여 3~6장을 각각 한 기준에 대응시킨 구성은 독자에게 명료한 논리 흐름을 제공한다. 단순 시간순 또는 응용 분야순 나열형 리뷰보다 교육적 가치가 높다.", spacing: { after: 100 } }),
        new Paragraph({ children: [new TextRun({ text: "(2) 메커니즘 설명의 정확성", bold: true })] }),
        new Paragraph({ text: "2장에서 산 촉매와 염기 촉매 조건의 위치선택성 차이를 thiolate의 입체 선호와 alkoxide의 빠른 protonation으로 설명한 부분은 교과서적 수준에서 정확하다. 특히 thiol(pKa ~ 8-10)과 alcohol(pKa ~ 16-18)의 pKa 차이를 통해 chain propagation이 억제되고 step-growth가 유지되는 이유를 명시한 점이 본문의 가장 강점이다.", spacing: { after: 100 } }),
        new Paragraph({ children: [new TextRun({ text: "(3) 후속 기능화 전략의 강조", bold: true })] }),
        new Paragraph({ text: "β-hydroxy thioether의 hydroxyl기와 sulfur가 각각 esterification과 alkylation을 통해 orthogonal하게 후속 기능화될 수 있다는 점을 명확히 부각하고, sulfonium polymer / amphiphilic homopolymer / zwitterionic 표면 등 응용 분기점까지 추적한 7~8장 구성은 본 리뷰의 차별화 요소이다.", spacing: { after: 100 } }),
        new Paragraph({ children: [new TextRun({ text: "(4) 위치선택성의 분광학적 근거 제시", bold: true })] }),
        new Paragraph({ text: "1H-NMR 기반 isomer 판별(3.5 ppm vs esterification 후 5 ppm downfield shift)을 [19]번 인용으로 제시한 점은 단순 주장에 그치지 않는 실험적 근거 인용으로 평가된다.", spacing: { after: 300 } }),

        // 3. 주요 문제점
        new Paragraph({ text: "3. 주요 문제점 및 비평", heading: HeadingLevel.HEADING_1 }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 1] Khan 그룹 자기/그룹 인용(self-/group-citation) 비율 과다 (57.6%)", bold: true, color: "CC0000" })] }),
        new Paragraph({ children: [new TextRun({ text: "• 내용: ", bold: true }), new TextRun("참고문헌 총 33편 중 Khan 공저 논문이 19편(57.6%)으로, 학술적 권고 상한(20%)의 약 2.9배, 이상치 경계(30%)의 약 1.9배를 초과한다. 본 리뷰의 가장 결정적인 결함이다.") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 근거: ", bold: true }), new TextRun("ICMJE 및 COPE 지침; Ioannidis et al., PLoS Biol., 2019, 17(8), e3000384 (self-citation rate >25%를 이상치로 보고).") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 개선 방향: ", bold: true }), new TextRun("Bowman, Hawker, Cramer, Konuray, Hayashi, Jin, Du Prez 등 외부 그룹 논문 최소 10편 추가 인용하여 group-citation 비율을 30% 미만으로 낮출 것.") ], spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 2] 리뷰 포괄성과 균형성 부족 — 경쟁 반응 및 한계점 비교 분석 누락", bold: true, color: "CC0000" })] }),
        new Paragraph({ children: [new TextRun({ text: "• 내용: ", bold: true }), new TextRun("amine-epoxy, thiol-ene, thiol-Michael, azide-alkyne 등 경쟁 반응과의 비교 분석이 전혀 없고, thiol의 악취·산화 민감성, epoxy 단량체의 발암성 등 한계에 대한 비판적 논의가 거의 없다.") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 근거: ", bold: true }), new TextRun("Hoyle and Bowman, Angew. Chem. Int. Ed., 2010, 49, 1540 — thiol-X 반응 비교표 제공이 본 분야 표준.") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 개선 방향: ", bold: true }), new TextRun("경쟁 반응 비교표(Table) 신설 및 \"Limitations and Future Outlook\" 절 추가.") ], spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 3] 2020년 이후 타 그룹 최신 연구 누락", bold: true, color: "CC0000" })] }),
        new Paragraph({ children: [new TextRun({ text: "• 내용: ", bold: true }), new TextRun("2020년 이후 인용 9편 중 외부 그룹은 단 2편(6%). Thiol-epoxy 기반 vitrimer, DLP/SLA 3D printing 수지, self-healing 코팅 등 2020-2025년 핵심 연구 트렌드가 모두 누락되었다.") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 개선 방향: ", bold: true }), new TextRun("\"Dynamic and reprocessable thiol-epoxy networks\" 절, \"Photocurable thiol-epoxy resins for additive manufacturing\" 절을 신설하고 관련 논문(Konuray 2020, Hayashi 그룹, Bagheri/Jin 2019-2022 등)을 보강.") ], spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 4] 학술지 헤더 연도/권호 불일치 (메타데이터 오류)", bold: true, color: "CC0000" })] }),
        new Paragraph({ text: "• 본문 상단에 \"접착 및 계면 제 18권 제 2호, 2017년\"이 표기되어 있으나, 논문 ID는 JAIK-2026-005 (2026년 투고)로 명백한 template 미수정 오류. CrossRef DOI 및 KCI/Scopus 색인 등록 시 데이터 충돌 발생 가능. → 즉시 정정 필요.", spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 5] 접수/수정/채택일 Placeholder 미수정", bold: true, color: "CC0000" })] }),
        new Paragraph({ text: "• \"202X년 월 일\" 형태의 placeholder가 접수·수정·채택일 모두에 남아 있다. 학술 윤리 및 우선권 분쟁 시 결정적 증빙 자료이므로 proof 단계에서 반드시 정확히 입력되어야 함.", spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 6] 도식(Figure/Scheme) 표기 일관성 부족", bold: true })] }),
        new Paragraph({ text: "• 반응 메커니즘과 합성 경로 도식(Fig 1, 4, 5)은 ACS/RSC 스타일가이드 상 \"Scheme\"으로 분류되어야 한다. Figure와 Scheme의 분류 기준을 일관되게 적용하고 캡션 원본을 첨부하라.", spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 7] Sharpless 기준과 Barner-Kowollik 기준의 혼용", bold: true })] }),
        new Paragraph({ text: "• 1장 서론에서 두 기준을 병렬 기술하나 3~6장 분석은 Barner-Kowollik 기준만 사용. 본 리뷰가 채택하는 click 기준을 1장에서 명확히 선언하라.", spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 8] 학회지 스코프(접착 및 계면) 정합성 부족", bold: true })] }),
        new Paragraph({ text: "• 본문에서 정량적 접착력 평가(lap shear, peel test), epoxy 접착제 경화제로서의 thiol-epoxy 응용 논의가 거의 없다. Jin and Yamamoto, Prog. Polym. Sci., 2015와 같은 thiol-cured epoxy adhesive 리뷰 인용 및 관련 절 신설이 필요하다.", spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 9] Ref. [21] Attribution 오해 소지", bold: true })] }),
        new Paragraph({ text: "• 7장에서 [21] (Buerkli et al., Biomacromolecules, 2014)은 ETH/Leroux 그룹 논문이나 마치 Khan 그룹의 연속 연구인 것처럼 기술. \"ETH/Leroux 그룹은 ... 를 제시하였다 [21]\"로 attribution을 명확히 할 것.", spacing: { after: 150 } }),

        new Paragraph({ children: [new TextRun({ text: "[문제점 10] 분자량 단위 모호 (DP vs Mn)", bold: true })] }),
        new Paragraph({ text: "• 3장 \"수평균 중합도 약 12,000\"의 단위(DP vs Mn g/mol)가 불명확. PGMA 단량체 분자량(142 g/mol) 고려 시 DP 12,000이면 Mn ~1.7 MDa로 통상 범위 초과. 원논문 [15] 재확인 후 단위 명시 필요.", spacing: { after: 300 } }),

        // 4. 데이터 검증
        new Paragraph({ text: "4. 데이터 검증 결과", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({ children: [new TextRun({ text: "• Khan/Eom 그룹 인용 비율: ", bold: true }), new TextRun("19/33 = 57.6% (권고 상한 20%의 2.9배 초과, 수용 불가)") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 2020년 이후 외부 그룹 인용: ", bold: true }), new TextRun("2/33 = 6.1% (매우 낮음)") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 헤더 메타데이터: ", bold: true }), new TextRun("권/호/연도 불일치, 접수/수정/채택일 placeholder 미수정") ] }),
        new Paragraph({ children: [new TextRun({ text: "• 본문 수치: ", bold: true }), new TextRun("분자량 단위 모호(문제점 10), 촉매 mol% 기준 미명시, pKa 값 출처 인용 누락") ], spacing: { after: 300 } }),

        // 5. 선행 연구 비교 분석
        new Paragraph({ text: "5. 선행 연구 비교 분석", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({ children: [new TextRun({ text: "누락된 정전적 선행 연구:", bold: true })] }),
        new Paragraph({ text: "• Hoyle and Bowman, Angew. Chem. Int. Ed., 2010, 49, 1540 — thiol-X click 화학 정전적 리뷰 (필수 인용)" }),
        new Paragraph({ text: "• Jin and Yamamoto, Prog. Polym. Sci., 2015, 41, 1 — thiol-cured epoxy adhesive (학회지 스코프 정합성 필수)" }),
        new Paragraph({ text: "• Carioscia et al., Polymer, 2007, 48, 1526 — thiol-epoxy photopolymerization kinetics (Bowman 그룹)" }),
        new Paragraph({ text: "• Chatani et al., Polym. Chem., 2014, 5, 4555 — PBG 기반 thiol-epoxy 광경화 (Bowman 그룹)" }),
        new Paragraph({ children: [new TextRun({ text: "누락된 2020-2025년 최신 연구:", bold: true })], spacing: { before: 150 } }),
        new Paragraph({ text: "• Konuray et al., Polymers, 2020, 12, 1084 — Dual-curable thiol-epoxy systems" }),
        new Paragraph({ text: "• Hayashi 그룹 — Thio-vitrimer 시리즈 (Polym. Chem., 2020-2022)" }),
        new Paragraph({ text: "• Bagheri and Jin, ACS Appl. Polym. Mater., 2019-2022 — Thiol-epoxy 3D printing" }),
        new Paragraph({ children: [new TextRun({ text: "독창성 문제:", bold: true })], spacing: { before: 150 } }),
        new Paragraph({ text: "• 동일 Khan 그룹의 선행 리뷰([11] 2016, [12] 2023, [13] 2022)와의 차별화 포인트가 명확히 제시되지 않음. 1장 또는 결론에 차별화 진술 추가 필요.", spacing: { after: 300 } }),

        // 6. 세부 수정 요청사항
        new Paragraph({ text: "6. 세부 수정 요청사항", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({ children: [new TextRun({ text: "[헤더/메타데이터]", bold: true })] }),
        new Paragraph({ text: "(R1) 표지 헤더 \"접착 및 계면 제 18권 제 2호, 2017년\"을 즉시 삭제·수정하라." }),
        new Paragraph({ text: "(R2) 접수/수정/채택일 placeholder를 실제 일자로 정확히 기입하라.", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[서론(1장)]", bold: true })] }),
        new Paragraph({ text: "(R3) Barner-Kowollik 4대 기준과 Sharpless 원 기준의 관계를 명확히 정리하고 본 리뷰가 채택하는 기준을 선언하라." }),
        new Paragraph({ text: "(R4) Khan 그룹 선행 리뷰([11-13])와 본 리뷰의 차별화 포인트를 명시하라.", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[메커니즘(2장)]", bold: true })] }),
        new Paragraph({ text: "(R5) thiol/alcohol pKa 값의 출처(Bordwell pKa table 등)를 인용하라." }),
        new Paragraph({ text: "(R6) 전자적 효과가 강한 substrate에서 위치선택성 예외 사례를 1-2문장으로 언급하라.", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[3~6장]", bold: true })] }),
        new Paragraph({ text: "(R7) 3장: \"DP 약 12,000\"의 단위를 명확히 표기하라." }),
        new Paragraph({ text: "(R9) 5장: Bowman 그룹 PBG/photopolymerization 선행 연구(Carioscia 2007, Chatani 2014)를 추가 인용하라." }),
        new Paragraph({ text: "(R10) 5장: 촉매 mol%의 기준(thiol 또는 epoxy 대비)을 명시하라." }),
        new Paragraph({ text: "(R11) 6장: thiol의 악취·휘발성 등 실용적 한계도 함께 논의하라.", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[7~8장]", bold: true })] }),
        new Paragraph({ text: "(R12) 7장: Ref. [21]은 ETH/Leroux 그룹 논문임을 명시하여 attribution을 정확히 하라." }),
        new Paragraph({ text: "(R13) 8장: 정량적 접착력 평가와 epoxy 접착제 경화제로서의 thiol-epoxy 응용 절을 신설하라.", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[신설 절]", bold: true })] }),
        new Paragraph({ text: "(R14) \"Dynamic and reprocessable thiol-epoxy networks\" 절 신설 (vitrimer, 동적 공유결합 네트워크)" }),
        new Paragraph({ text: "(R15) \"Photocurable thiol-epoxy resins for additive manufacturing\" 절 신설 (DLP/SLA 3D printing)" }),
        new Paragraph({ text: "(R16) \"Comparison with competing reactions and limitations\" 절 신설 (경쟁 반응 비교표 및 한계점)", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[참고문헌]", bold: true })] }),
        new Paragraph({ text: "(R17) Khan/Eom 그룹 인용 비율을 30% 미만으로 감축. 외부 그룹 논문 최소 10편 추가." }),
        new Paragraph({ text: "(R18) Hoyle & Bowman (2010), Jin & Yamamoto (2015)를 필수 인용하라." }),
        new Paragraph({ text: "(R19) 인용 형식을 학회지 투고 규정에 맞춰 통일하라.", spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "[Figure/Scheme]", bold: true })] }),
        new Paragraph({ text: "(R20) 반응 메커니즘·합성 경로 도식은 \"Scheme\"으로, 데이터 그림은 \"Figure\"로 분류하여 표기를 통일하라." }),
        new Paragraph({ text: "(R21) 모든 Figure/Scheme 캡션 원본을 첨부하라.", spacing: { after: 300 } }),

        // 7. 종합 판정
        new Paragraph({ text: "7. 종합 판정", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({
          children: [
            new TextRun({ text: "판정: ", bold: true }),
            new TextRun({ text: "Major Revision (수정 후 재심)", bold: true, color: "C65911" }),
          ],
          spacing: { after: 150 },
        }),
        new Paragraph({
          text: "본 리뷰는 thiol-epoxy 클릭 반응의 메커니즘과 응용을 한국어로 체계적으로 정리한 시도로서 학술적 가치가 있으나, 다음의 중대한 결함이 식별되어 현재 상태로는 게재 불가하다.",
          spacing: { after: 100 },
        }),
        new Paragraph({ children: [new TextRun({ text: "(1) ", bold: true }), new TextRun("자기/그룹 인용 비율 57.6%는 학술적 수용 한계를 크게 초과하여 리뷰의 객관성을 심각하게 훼손한다. (가장 결정적 결함)") ] }),
        new Paragraph({ children: [new TextRun({ text: "(2) ", bold: true }), new TextRun("2020-2025년 외부 그룹의 핵심 연구(vitrimer, 3D printing, self-healing)가 누락되어 리뷰의 최신성과 포괄성이 부족하다.") ] }),
        new Paragraph({ children: [new TextRun({ text: "(3) ", bold: true }), new TextRun("경쟁 반응과의 비교 분석, 한계점 논의가 부재하여 리뷰 논문의 \"balanced view\" 요건을 충족하지 못한다.") ] }),
        new Paragraph({ children: [new TextRun({ text: "(4) ", bold: true }), new TextRun("학회지 핵심 스코프인 \"접착\"에 대한 직접적 연결이 부족하여 Journal of Adhesion and Interface 스코프 적합성이 약하다.") ] }),
        new Paragraph({ children: [new TextRun({ text: "(5) ", bold: true }), new TextRun("헤더의 권/호/연도 불일치 및 접수/수정/채택일 placeholder 미수정은 즉시 수정 필요한 메타데이터 오류이다.") ], spacing: { after: 150 } }),
        new Paragraph({ children: [new TextRun({ text: "핵심 수정 우선순위:", bold: true })] }),
        new Paragraph({ text: "① (필수) Khan/Eom 그룹 인용 비율 30% 미만으로 감축" }),
        new Paragraph({ text: "② (필수) 학술지 헤더 및 접수/수정/채택일 메타데이터 정정" }),
        new Paragraph({ text: "③ (필수) 2020년 이후 외부 그룹 최신 연구 보강" }),
        new Paragraph({ text: "④ (필수) 학회지 스코프 적합성 확보를 위한 접착 응용 절 신설" }),
        new Paragraph({ text: "⑤ (강력 권장) 경쟁 반응 비교표 및 한계점 절 신설", spacing: { after: 300 } }),

        new Paragraph({ text: "═".repeat(60), alignment: AlignmentType.CENTER }),
        new Paragraph({ text: "심사 종료  |  2026-05-23", alignment: AlignmentType.CENTER }),
      ],
    }],
  });
  return doc;
}

// ======================================================
// 문서 2: 공식 심사의견서 (테이블 없이 단락만 사용)
// ======================================================
function makeReviewForm() {
  const HR = "─".repeat(55);

  const authorOpinionLines = [
    "본 리뷰 논문은 thiol-epoxy 클릭 반응을 Barner-Kowollik의 4대 기준으로 체계적으로 정리한 의미 있는 시도입니다.",
    "그러나 게재 승인을 위해 다음 사항의 대폭 수정이 필요합니다.",
    "",
    "【필수 수정사항】",
    "",
    "1. 자기/그룹 인용 비율 조정 (최우선 과제)",
    "현재 참고문헌 33편 중 Khan/Eom 그룹 논문이 19편(57.6%)으로 학술적 권고 수준(20%)을 크게 초과합니다.",
    "Bowman, Hawker, Konuray, Hayashi, Jin 등 외부 그룹의 논문을 최소 10편 이상 추가 인용하여",
    "그룹 인용 비율을 30% 미만으로 낮춰 주십시오.",
    "",
    "2. 최신 연구 동향 보강",
    "2020-2025년 타 그룹의 핵심 연구인 thiol-epoxy 기반 vitrimer/동적 공유결합 네트워크,",
    "DLP/SLA 3D printing 수지, self-healing 코팅 분야의 연구를 포함하는 절을 신설해 주십시오.",
    "",
    "3. 경쟁 반응 비교 및 한계점 논의",
    "amine-epoxy, thiol-ene, thiol-Michael과의 비교 분석표와 thiol-epoxy 반응의 한계점",
    "(thiol 산화·악취·발암성, oxygen inhibition 등) 및 미래 전망을 다루는 절을 추가해 주십시오.",
    "",
    "4. 학회지 스코프 적합성 확보",
    "「접착 및 계면」 학회지의 핵심 스코프인 '접착(adhesion)'과의 연결이 매우 약합니다.",
    "Thiol-epoxy를 epoxy 접착제 경화제 또는 계면 접착력 향상 소재로 활용한 연구",
    "(예: Jin & Yamamoto, Prog. Polym. Sci., 2015)를 논의하는 절을 신설하고",
    "정량적 접착 평가 데이터를 보강해 주십시오.",
    "",
    "5. 학술 메타데이터 정정",
    "- 표지 헤더의 \"제 18권 제 2호, 2017년\" 표기를 즉시 수정 또는 삭제해 주십시오.",
    "- 접수/수정/채택일의 \"202X년 월 일\" placeholder를 실제 일자로 기입해 주십시오.",
    "",
    "【기술적 수정사항 (일부)】",
    "- 3장: \"수평균 중합도 약 12,000\"의 단위(DP 또는 Mn, g/mol)를 명확히 표기할 것",
    "- 5장: 반응 조건의 촉매 mol% 기준(thiol 대비? epoxy 대비?)을 명시할 것",
    "- 7장: 참고문헌 [21] (Buerkli et al.)이 ETH/Leroux 그룹 논문임을 명시할 것",
    "- Figure/Scheme 표기: 반응 메커니즘·합성 경로 도식은 \"Scheme\"으로 분류하여 통일할 것",
    "- 서론: Barner-Kowollik 기준과 Sharpless 원 기준의 관계를 명확히 정리하고,",
    "  기존 Khan 그룹 리뷰([11-13])와 본 리뷰의 차별화 포인트를 명시할 것",
  ];

  const editorOpinionLines = [
    "【편집위원(장)용 비밀 의견】",
    "",
    "본 논문은 국립금오공과대학교 엄태준 교수(교신저자)와 그 제자(이나경)가 투고한",
    "thiol-epoxy 클릭 화학 리뷰 논문입니다. 편집위원(장)께서 참고하시도록 다음 사항을 보고드립니다.",
    "",
    "◆ 저자 이해충돌 관련 주의사항",
    "교신저자 엄태준은 참고문헌 [17], [18], [20], [27]의 공저자이며, 모두 Khan 그룹의 논문입니다.",
    "전체 33편 중 Khan/Eom 그룹 논문이 19편(57.6%)으로, 이 리뷰는 사실상 Khan 그룹의",
    "그룹 업적 요약서에 가까운 성격을 지닙니다. 게재 허용 시 학회지 공정성에 대한",
    "외부 비판이 예상됩니다.",
    "",
    "◆ 학회지 스코프 적합성",
    "본 논문은 고분자 합성 화학 위주의 내용으로, 「접착 및 계면」 학회지의 핵심 키워드인",
    "접착(adhesion), 접착제(adhesive), 계면 강도(interfacial strength) 관련 내용이 거의 없습니다.",
    "게재를 허용할 경우 접착 분야 핵심 응용을 보강하는 것을 조건으로 명시하시기 바랍니다.",
    "",
    "◆ 독창성",
    "Khan 그룹 자체에서 동일 주제의 리뷰를 이미 세 편([11] 2016, [12] 2023, [13] 2022)",
    "출판한 상황에서, 본 리뷰의 학술적 기여가 한국어 소개 수준에 그치지 않도록",
    "차별화 요소를 강화할 것을 요구할 필요가 있습니다.",
    "",
    "◆ 판정 의견",
    "Major Revision으로 판정하며, 수정 후 재심을 권장합니다.",
    "저자들이 (a) group-citation 비율을 30% 미만으로 낮추고, (b) 최신 연구 트렌드를 보강하며,",
    "(c) 학회지 스코프 정합성을 확보하는 경우에만 게재를 재고할 것을 권고드립니다.",
    "현 상태로의 게재는 학회지 편집 공정성 면에서 바람직하지 않습니다.",
    "",
    "◆ 다음 라운드 심사 참여",
    "수정 논문의 재심사에 참여할 의향이 있습니다.",
  ];

  const doc = new Document({
    sections: [{
      children: [
        // 제목
        new Paragraph({
          text: "심사 의견서",
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          children: [new TextRun({ text: "논문 ID: JAIK-2026-005  |  심사일: 2026-05-23", italics: true })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 300 },
        }),

        // 논문 정보
        new Paragraph({ text: HR, spacing: { after: 100 } }),
        new Paragraph({ children: [new TextRun({ text: "논문 제목: ", bold: true }), new TextRun("Thiol-Epoxy 클릭 화학 기반 고분자 합성 및 계면 소재 연구 동향")] }),
        new Paragraph({ children: [new TextRun({ text: "저      자: ", bold: true }), new TextRun("이나경, 엄태준 (국립금오공과대학교 재료공학부 고분자공학전공)")] }),
        new Paragraph({ children: [new TextRun({ text: "투고 저널: ", bold: true }), new TextRun("접착 및 계면 (Journal of Adhesion and Interface)")] }),
        new Paragraph({ text: HR, spacing: { after: 400 } }),

        // 저자 제공용 심사의견
        new Paragraph({
          children: [new TextRun({ text: "▶ 저자 제공용 심사의견", bold: true, size: 28 })],
          spacing: { after: 160 },
        }),
        ...authorOpinionLines.map(line =>
          new Paragraph({ text: line, spacing: { after: 80 } })
        ),

        new Paragraph({ text: "", spacing: { after: 200 } }),
        new Paragraph({ text: HR, spacing: { after: 400 } }),

        // 편집위원(장) 제공용 심사의견
        new Paragraph({
          children: [new TextRun({ text: "▶ 편집위원(장) 제공용 심사의견", bold: true, size: 28 })],
          spacing: { after: 160 },
        }),
        ...editorOpinionLines.map(line =>
          new Paragraph({ text: line, spacing: { after: 80 } })
        ),

        new Paragraph({ text: "", spacing: { after: 200 } }),
        new Paragraph({ text: HR, spacing: { after: 300 } }),

        // 심사 판정
        new Paragraph({
          children: [new TextRun({ text: "▶ 심사 판정", bold: true, size: 28 })],
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "심사:  ", bold: true }),
            new TextRun("○ 게재 가    ○ 수정 후 게재    "),
            new TextRun({ text: "● 수정 후 재심", bold: true, color: "C65911" }),
            new TextRun("    ○ 게재 불가"),
          ],
          spacing: { after: 120 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "판정 근거:  ", bold: true }),
            new TextRun("그룹 인용 비율 57.6% 초과(최우선 수정), 최신 연구 누락, 경쟁 반응 비교 부재,"),
          ],
          spacing: { after: 60 },
        }),
        new Paragraph({
          text: "학회지 스코프 적합성 부족, 메타데이터 오류. 상기 사항 대폭 수정 후 재심사 필요.",
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "다음 라운드에도 이 논문을 심사하시겠습니까?  ", bold: true }),
            new TextRun({ text: "● 예    ○ 아니오", bold: true }),
          ],
          spacing: { after: 300 },
        }),

        new Paragraph({ text: HR, spacing: { after: 200 } }),
        new Paragraph({
          children: [new TextRun({ text: "심사일: 2026년 5월 23일", italics: true })],
          alignment: AlignmentType.RIGHT,
        }),
      ],
    }],
  });
  return doc;
}

// ======================================================
// 논문 요약 (저자용) — 별도 파일
// ======================================================
function makeSummary() {
  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          text: "논문 요약 — 「Thiol-Epoxy 클릭 화학 기반 고분자 합성 및 계면 소재 연구 동향」",
          heading: HeadingLevel.TITLE,
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          children: [new TextRun({ text: "이나경·엄태준 | 국립금오공과대학교 | 접착 및 계면 (JAIK-2026-005)", italics: true })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 },
        }),

        new Paragraph({ text: "한 줄 요약", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({
          text: "이 논문은 'Thiol-Epoxy 클릭 반응'이 왜 '클릭 화학'으로 불릴 자격이 있는지를 4가지 기준으로 체계적으로 증명하고, 이 반응을 이용해 만들 수 있는 항균 고분자·약물 전달체·항오염 표면 등 첨단 소재 연구를 정리한 리뷰 논문입니다.",
          spacing: { after: 300 },
        }),

        new Paragraph({ text: "핵심 개념 설명", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({ children: [new TextRun({ text: "Thiol-Epoxy 클릭 반응이란?", bold: true })] }),
        new Paragraph({
          text: "• 'Thiol'(황-수소 결합, SH기 포함 분자)과 'Epoxy'(산소가 탄소 2개를 연결한 삼각형 고리 구조)가 만나면, 염기 촉매 조건에서 Epoxy 고리가 열리며 'β-hydroxy thioether'라는 안정한 결합 구조를 형성합니다.",
          spacing: { after: 80 },
        }),
        new Paragraph({
          text: "• 이때 황이 붙는 위치가 한 곳으로 정해지고(위치선택성), 부산물이 거의 없으며, 상온에서 짧은 시간 안에 반응이 거의 100% 완료됩니다. 이런 특성들이 '클릭 화학'의 기준과 부합합니다.",
          spacing: { after: 200 },
        }),
        new Paragraph({ children: [new TextRun({ text: "왜 이 반응이 주목받는가?", bold: true })] }),
        new Paragraph({
          text: "• 반응 후 만들어진 구조(β-hydroxy thioether)에는 두 개의 '후속 기능화 포인트'(hydroxyl기, thioether sulfur)가 있어, 이를 활용해 항균 고분자, 양친매성 고분자, 약물 전달체, 항오염 표면 등 다양한 첨단 소재로 변환할 수 있습니다.",
          spacing: { after: 80 },
        }),
        new Paragraph({
          text: "• 특히 빛으로 반응을 제어하는 '광중합(photopolymerization)' 방식을 통해 마이크로/나노 수준의 표면 패턴 형성이 가능하여, 의료기기·바이오 인터페이스·스마트 코팅 분야에서 잠재적 응용 가치가 큽니다.",
          spacing: { after: 300 },
        }),

        new Paragraph({ text: "논문의 주요 내용 요약", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({ children: [new TextRun({ text: "① 반응 메커니즘 (2장)", bold: true })] }),
        new Paragraph({
          text: "염기 촉매 하에서 thiol이 thiolate 음이온으로 바뀐 뒤 epoxy 고리를 열면서 β-hydroxy thioether를 형성합니다. 중간에 생기는 alkoxide(음이온)는 chain 반응으로 이어지지 않고 빠르게 중화됩니다. 이는 thiol(pKa ~8-10)이 alcohol(pKa ~16-18)보다 훨씬 약한 산이라 열역학적으로 유리하기 때문입니다.",
          spacing: { after: 150 },
        }),
        new Paragraph({ children: [new TextRun({ text: "② 높은 반응 효율 (3장)", bold: true })] }),
        new Paragraph({
          text: "PGMA(poly(glycidyl methacrylate)) 등 수천 개의 epoxy 반복단위를 가진 고분자에서도 상온 수 시간 내에 전환율 ~100%가 달성됩니다. 덴드리머, 병솔 모양 공중합체 등 복잡한 구조에도 적용 가능합니다.",
          spacing: { after: 150 },
        }),
        new Paragraph({ children: [new TextRun({ text: "③ 위치선택성 (4장)", bold: true })] }),
        new Paragraph({
          text: "비대칭 epoxy에서 황은 항상 입체장애가 작은 쪽 탄소에 결합합니다. 이를 1H-NMR로 확인한 결과 단일 위치 이성질체만 생성되는 것이 다양한 구조에서 입증되었습니다.",
          spacing: { after: 150 },
        }),
        new Paragraph({ children: [new TextRun({ text: "④ 다양한 반응 조건 (5장)", bold: true })] }),
        new Paragraph({
          text: "LiOH/10% aqueous THF 조건이 최적이며, TEA, DBU 등 다른 염기와 물·DMSO·MeCN 등 다양한 용매 조합도 가능합니다. 특히 photobase generator를 이용한 광제어 반응으로 표면 패턴 형성이 가능합니다.",
          spacing: { after: 150 },
        }),
        new Paragraph({ children: [new TextRun({ text: "⑤ 1:1 화학양론 (6장)", bold: true })] }),
        new Paragraph({
          text: "자유 thiol은 공기 중 산화로 disulfide가 될 수 있어 등몰 반응이 어렵습니다. 이 문제를 disulfide를 NaBH4로 환원해 thiolate를 현장에서 만드는 전략으로 해결하였습니다.",
          spacing: { after: 150 },
        }),
        new Paragraph({ children: [new TextRun({ text: "⑥ 후속 기능화 및 응용 (7~8장)", bold: true })] }),
        new Paragraph({
          text: "β-hydroxy thioether의 OH는 esterification으로, 황은 alkylation으로 독립적으로 변환됩니다. 이를 이용해 항균성 sulfonium 고분자, siRNA 전달용 양친매성 고분자, 항오염(antibiofouling) zwitterionic 표면 패턴 등이 제조되었습니다.",
          spacing: { after: 300 },
        }),

        new Paragraph({ text: "심사 결과 핵심 요약 (참고용)", heading: HeadingLevel.HEADING_1 }),
        new Paragraph({
          children: [
            new TextRun({ text: "판정: ", bold: true }),
            new TextRun({ text: "수정 후 재심 (Major Revision)", bold: true, color: "C65911" }),
          ],
          spacing: { after: 100 },
        }),
        new Paragraph({ children: [new TextRun({ text: "주요 지적 사항:", bold: true })] }),
        new Paragraph({ text: "• 참고문헌 33편 중 57.6%가 Khan/Eom 그룹 자기인용 → 학술적 수용 한계(20%) 3배 초과" }),
        new Paragraph({ text: "• vitrimer, 3D 프린팅 등 2020-2025년 최신 연구 트렌드 누락" }),
        new Paragraph({ text: "• 학회지 「접착 및 계면」 스코프(접착 응용)와의 연결이 약함" }),
        new Paragraph({ text: "• 경쟁 반응과의 비교 및 한계점 논의 부재" }),
        new Paragraph({ text: "• 표지 헤더 연도(2017년) 오기 및 접수/수정/채택일 기입 누락" }),

        new Paragraph({ text: "", spacing: { after: 400 } }),
        new Paragraph({
          children: [new TextRun({ text: "작성일: 2026-05-23  |  심사위원: AI 자동 심사 (paper-reviewer-judge)", italics: true })],
          alignment: AlignmentType.RIGHT,
        }),
      ],
    }],
  });
  return doc;
}

// 파일 생성
const outDir = "c:\\Users\\tmdwo\\Downloads\\agent-SJ\\AIsimsa";

Promise.all([
  Packer.toBuffer(makeFullCritique()).then(buf => {
    fs.writeFileSync(`${outDir}\\심사비평_전문_JAIK-2026-005.docx`, buf);
    console.log("✓ 심사비평_전문_JAIK-2026-005.docx 생성 완료");
  }),
  Packer.toBuffer(makeReviewForm()).then(buf => {
    fs.writeFileSync(`${outDir}\\심사의견서_JAIK-2026-005.docx`, buf);
    console.log("✓ 심사의견서_JAIK-2026-005.docx 생성 완료");
  }),
  Packer.toBuffer(makeSummary()).then(buf => {
    fs.writeFileSync(`${outDir}\\논문요약_JAIK-2026-005.docx`, buf);
    console.log("✓ 논문요약_JAIK-2026-005.docx 생성 완료");
  }),
]).catch(err => console.error("오류:", err));
