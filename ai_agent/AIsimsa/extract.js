const fs = require("fs");
const pdfParse = require("pdf-parse");
const dataBuffer = fs.readFileSync("JAIK-2026-005_Manuscript(pdf)_001.pdf");
pdfParse(dataBuffer).then(data => {
  fs.writeFileSync("extracted_text.txt", data.text, "utf8");
  console.log("Pages:", data.numpages);
  console.log("Done");
}).catch(e => console.error(e));
