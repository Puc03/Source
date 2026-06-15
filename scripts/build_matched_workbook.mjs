import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(import.meta.dirname, "..");
const outputDir = path.join(root, "outputs", "cleaned_matching");
const workbookPath = path.join(outputDir, "ueh_tiki_cleaned_matched_dataset.xlsx");

const csvSheets = [
  ["match_quality_summary.csv", "Quality Summary"],
  ["ueh_students_clean.csv", "Students Clean"],
  ["ueh_student_courses_clean.csv", "Student Courses"],
  ["tiki_books_clean.csv", "Tiki Books Clean"],
  ["ueh_repository_clean.csv", "UEH Repo Clean"],
  ["course_resource_matches.csv", "Course Matches"],
  ["student_resource_matches.csv", "Student Matches"],
];

const workbook = Workbook.create();

for (const [filename, sheetName] of csvSheets) {
  const csvText = (await fs.readFile(path.join(outputDir, filename), "utf8")).replace(/^\uFEFF/, "");
  await workbook.fromCSV(csvText, { sheetName });
}

const summary = workbook.worksheets.add("README");
summary.getRange("A1:B12").values = [
  ["Dataset", "UEH students + Tiki books + UEH repository"],
  ["Purpose", "Cleaned source CSVs and deterministic text-based matching outputs"],
  ["Final joined table", "Student Matches"],
  ["Course-level top matches", "Course Matches"],
  ["Cleaned Tiki table", "Tiki Books Clean"],
  ["Cleaned student table", "Students Clean"],
  ["Exploded student-course table", "Student Courses"],
  ["Cleaned repository table", "UEH Repo Clean"],
  ["Scoring", "Accent-insensitive text normalization, n-grams, Vietnamese/English synonyms, exact phrase boosts"],
  ["Confidence", "high / medium / low based on match score"],
  ["Created by", "Codex"],
  ["Note", "Low-confidence rows are retained and flagged instead of silently dropped"],
];
summary.getRange("A1:B1").format = {
  fill: "#155E75",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A1:A12").format = { font: { bold: true } };
summary.getRange("A1:B12").format.autofitColumns();

for (const [, sheetName] of csvSheets) {
  const sheet = workbook.worksheets.getItem(sheetName);
  sheet.freezePanes.freezeRows(1);
  const header = sheet.getRange("A1:AZ1");
  header.format = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF" },
  };
}

const check = await workbook.inspect({
  kind: "sheet,table",
  tableMaxRows: 4,
  tableMaxCols: 6,
  maxChars: 5000,
});
console.log(check.ndjson);

const preview = await workbook.render({
  sheetName: "README",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  path.join(outputDir, "workbook_readme_preview.png"),
  new Uint8Array(await preview.arrayBuffer()),
);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(workbookPath);
console.log(workbookPath);
