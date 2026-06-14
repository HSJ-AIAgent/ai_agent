const fs = require('fs');
const path = require('path');

function crc32(buf) {
  const table = (() => {
    const t = new Uint32Array(256);
    for (let i = 0; i < 256; i++) {
      let c = i;
      for (let j = 0; j < 8; j++) c = (c & 1) ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[i] = c;
    }
    return t;
  })();
  let crc = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) crc = table[(crc ^ buf[i]) & 0xFF] ^ (crc >>> 8);
  return (crc ^ 0xFFFFFFFF) >>> 0;
}
function u32(n) { const b = Buffer.allocUnsafe(4); b.writeUInt32LE(n>>>0,0); return b; }
function u16(n) { const b = Buffer.allocUnsafe(2); b.writeUInt16LE(n&0xFFFF,0); return b; }

function buildZip(files) {
  const parts = [], cds = [];
  let offset = 0;
  const time = ((12<<11)|(0<<5)|0), date = (((2026-1980)<<9)|(5<<5)|25);
  for (const {name, content} of files) {
    const data = Buffer.isBuffer(content) ? content : Buffer.from(content, 'utf8');
    const nb = Buffer.from(name, 'utf8');
    const crc = crc32(data);
    const lh = Buffer.concat([
      Buffer.from([0x50,0x4B,0x03,0x04]),
      u16(20),u16(0),u16(0),u16(time),u16(date),
      u32(crc),u32(data.length),u32(data.length),
      u16(nb.length),u16(0),nb
    ]);
    const lo = offset;
    parts.push(lh, data);
    offset += lh.length + data.length;
    cds.push(Buffer.concat([
      Buffer.from([0x50,0x4B,0x01,0x02]),
      u16(20),u16(20),u16(0),u16(0),u16(time),u16(date),
      u32(crc),u32(data.length),u32(data.length),
      u16(nb.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(lo),nb
    ]));
  }
  const cd = Buffer.concat(cds);
  return Buffer.concat([...parts, cd, Buffer.concat([
    Buffer.from([0x50,0x4B,0x05,0x06]),
    u16(0),u16(0),u16(files.length),u16(files.length),
    u32(cd.length),u32(offset),u16(0)
  ])]);
}

function x(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function p(text, opts={}) {
  const {bold=false, italic=false, h=0, spaceAfter=200} = opts;
  const style = h===1?'Heading1':h===2?'Heading2':'Normal';
  const pPr = `<w:pPr><w:pStyle w:val="${style}"/><w:spacing w:after="${spaceAfter}"/></w:pPr>`;
  const rPr = (bold||italic)?`<w:rPr>${bold?'<w:b/>':''}${italic?'<w:i/>':''}</w:rPr>`:'';
  return `<w:p>${pPr}<w:r>${rPr}<w:t xml:space="preserve">${x(text)}</w:t></w:r></w:p>`;
}
function blank() { return `<w:p><w:pPr><w:spacing w:after="100"/></w:pPr></w:p>`; }

const body = [
  p('Response to Reviewers', {h:1}),
  p('Manuscript: Synthesis of PVDF-Based Bottlebrush Polymers and Their Application in Triboelectric Nanogenerators'),
  p('Date: May 25, 2026'),
  blank(),

  // ── Referee 1, Comment 1 ──────────────────────────────────────────────────
  p('Referee: 1', {h:2}),
  blank(),
  p('Comment 1', {bold:true}),
  p('The authors state that PVDF-N3 with different molecular weights (2, 3, and 5 kDa) was obtained by controlling pressure reduction. Could the authors clarify how pressure reduction directly influences molecular weight, and provide a detailed description of the control strategy and underlying mechanism.', {italic:true}),
  blank(),
  p('We thank the reviewer for this insightful question. In our protocol, PVDF-N3 is synthesized by RAFT polymerization of VDF using an azide-functionalized xanthate as the chain-transfer agent (CTA), carried out in a sealed pressure vessel. Since VDF is a gaseous monomer (b.p. −84 °C), it is initially charged into the reactor at high pressure. As polymerization proceeds, VDF is consumed and incorporated into the growing polymer chains, which naturally causes the headspace pressure to decrease over time. The reaction is terminated when the pressure reaches a pre-defined target value; a higher target pressure corresponds to less VDF consumed and thus shorter chains (lower Mn), while a lower target pressure corresponds to greater monomer consumption and longer chains (higher Mn). By setting three different target pressures, we obtained PVDF-N3 samples with Mn values of approximately 2, 3, and 5 kDa. Since the azide group is introduced directly through the xanthate CTA, chain-end fidelity is maintained across all three samples (>95% by 19F NMR), ensuring reliable reactivity in the subsequent CuAAC step for norbornene attachment. This approach for controlling Mn via monomer consumption in polymerization of VDF is well documented in the literature (Ameduri, Chem. Rev. 2009, 109, 6632; Kostov et al., Macromolecules 2011, 44, 1841).'),
  blank(),
  p('Changes in Supporting Information: We have added a description of the PVDF-N3 synthesis procedure clarifying that monomer consumption during polymerization is tracked via the headspace pressure drop, and that the reaction is terminated at a pre-defined target pressure to control the molecular weight of each sample, as highlighted in blue.'),
  blank(),

  // ── Referee 2, Comment 5 ──────────────────────────────────────────────────
  p('Referee: 2', {h:2}),
  blank(),
  p('Comment 5', {bold:true}),
  p('The manuscript demonstrates enhanced triboelectric performance through bottlebrush polymer design. Could the authors provide systematic optimization data (e.g., varying PVDF side-chain lengths, different grafting densities, or alternative backbone chemistries) to confirm that the chosen architecture represents the optimal configuration?', {italic:true}),
  blank(),
  p('We sincerely appreciate the reviewer\'s constructive suggestion. We address each of the three architectural variables below.'),
  blank(),
  p('Side-chain length. The effect of PVDF side-chain molecular weight has already been systematically investigated in this work. We prepared NB-PVDF macromonomers with Mn values of 2.0, 3.0, and 5.0 kDa and compared their triboelectric performance, demonstrating a clear dependence of device output on side-chain length (Figure X).'),
  blank(),
  p('Grafting density. While it is in principle possible to vary σ by copolymerizing NB-PVDF macromonomers with small-molecule norbornene (NB), the large molecular weight difference between the two comonomers leads to significant differences in their ROMP reactivity, making it difficult to achieve a random distribution of grafting points along the backbone and precise control over the overall BBP architecture (Zografos et al., ACS Macro Lett. 2021, 10, 1622). Beyond these synthetic constraints, the primary objective of this work is to maximize the alignment of densely packed PVDF side chains in order to enhance the β-phase fraction. For this purpose, a 100% grafting density—where every norbornene repeat unit carries a PVDF side chain—is the most favorable configuration, and we have added a brief statement to this effect in the manuscript.'),
  blank(),
  p('Backbone chemistry. The inherent characteristics of ROMP leave limited options beyond norbornene-based monomers. Furthermore, since the PVDF side chains are several thousand Da in length, the chemical nature of the backbone is not expected to significantly affect the triboelectric performance of the resulting BBP films.'),
  blank(),
  p('Changes in Manuscript: We have added a sentence stating that a 100% grafting density was employed to maximize the side-chain ordering effect, which promotes alignment of PVDF chains and thereby increases the β-phase fraction, as highlighted in blue.'),
  blank(),
  blank(),
  p('We hope our responses and the corresponding revisions satisfactorily address the reviewer\'s comments. We thank the reviewer again for the time and effort invested in evaluating our manuscript.'),
  blank(),
  p('Sincerely,'),
  p('The Authors'),
].join('\n');

const docXml = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
${body}
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>
</w:body></w:document>`;

const stylesXml = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:styleId="Normal" w:default="1"><w:name w:val="Normal"/>
<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>
<w:pPr><w:outlineLvl w:val="0"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="32"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>
<w:pPr><w:outlineLvl w:val="1"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:b/><w:sz w:val="28"/></w:rPr></w:style>
</w:styles>`;

const files = [
  {name:'[Content_Types].xml', content:`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>`},
  {name:'_rels/.rels', content:`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>`},
  {name:'word/_rels/document.xml.rels', content:`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>`},
  {name:'docProps/core.xml', content:`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>Response to Reviewers</dc:title><dc:creator>Authors</dc:creator>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-05-25T00:00:00Z</dcterms:created>
</cp:coreProperties>`},
  {name:'docProps/app.xml', content:`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<Application>Microsoft Office Word</Application></Properties>`},
  {name:'word/styles.xml', content: stylesXml},
  {name:'word/document.xml', content: docXml},
];

const outPath = path.join(__dirname, 'revision_response_2026-05-25.docx');
fs.writeFileSync(outPath, buildZip(files));
console.log(`Saved: ${outPath} (${fs.statSync(outPath).size} bytes)`);
