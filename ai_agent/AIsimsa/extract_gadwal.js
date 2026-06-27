const fs = require("fs");
const pdf = require("pdf-parse");
const buf = fs.readFileSync("gadwal2015.pdf");
pdf(buf).then(d => {
  fs.writeFileSync("gadwal2015.txt", d.text, "utf8");
  console.log("Pages:", d.numpages);
});
