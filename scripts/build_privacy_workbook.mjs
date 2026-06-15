import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(import.meta.dirname, "..");
const outputDir = path.join(root, "outputs", "privacy_layer");
const workbookPath = path.join(outputDir, "ueh_tiki_privacy_layer.xlsx");
const fallbackWorkbookPath = path.join(outputDir, "ueh_tiki_privacy_layer_mask_last5.xlsx");

const csvSheets = [
  ["privacy_validation.csv", "Privacy Validation"],
  ["student_token_map_protected.csv", "Token Map"],
  ["students_protected.csv", "Students Protected"],
  ["student_courses_protected.csv", "Courses Protected"],
  ["student_resource_matches_analytics.csv", "Matches Analytics"],
  ["course_resource_matches_analytics.csv", "Course Matches"],
  ["tiki_books_public.csv", "Tiki Public"],
  ["ueh_repository_public.csv", "UEH Repo Public"],
];

const workbook = Workbook.create();

for (const [filename, sheetName] of csvSheets) {
  const csvText = (await fs.readFile(path.join(outputDir, filename), "utf8")).replace(/^\uFEFF/, "");
  await workbook.fromCSV(csvText, { sheetName });
}

const readme = workbook.worksheets.add("README");
readme.getRange("A1:B15").values = [
  ["Privacy Layer", "UEH + Tiki matched dataset"],
  ["Hash", "student_hash = HMAC-SHA256(student_code, secret)"],
  ["Token", "student_token = stable pseudonymous ID for API/dashboard use"],
  ["Secret", "Stored outside this output folder; not included in workbook"],
  ["Private mapping", ".secrets/student_token_mapping_private.csv; not included in workbook"],
  ["Protected sheets", "Keep token map, masked code and initials for controlled debugging"],
  ["Analytics sheets", "No raw ID, raw student code, name, masked code, or initials"],
  ["Kafka default", "Use Matches Analytics and Course Matches"],
  ["Student rows", "2,000"],
  ["Student-course rows", "12,000"],
  ["Student-match rows", "12,000"],
  ["Validation", "All checks passed before export"],
  ["Transform version", "privacy_v1"],
  ["Public sources", "Tiki books and UEH repository metadata"],
  ["Caution", "Do not publish protected sheets outside controlled internal use"],
];
readme.getRange("A1:B1").format = {
  fill: "#155E75",
  font: { bold: true, color: "#FFFFFF" },
};
readme.getRange("A1:A15").format = { font: { bold: true } };
readme.getRange("A1:B15").format.autofitColumns();

for (const [, sheetName] of csvSheets) {
  const sheet = workbook.worksheets.getItem(sheetName);
  sheet.freezePanes.freezeRows(1);
  sheet.getRange("A1:AZ1").format = {
    fill: "#0F766E",
    font: { bold: true, color: "#FFFFFF" },
  };
}

const inspect = await workbook.inspect({
  kind: "sheet,table",
  tableMaxRows: 3,
  tableMaxCols: 5,
  maxChars: 5000,
});
console.log(inspect.ndjson);

const preview = await workbook.render({
  sheetName: "README",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  path.join(outputDir, "privacy_workbook_readme_preview.png"),
  new Uint8Array(await preview.arrayBuffer()),
);

const output = await SpreadsheetFile.exportXlsx(workbook);
try {
  await output.save(workbookPath);
  console.log(workbookPath);
} catch (error) {
  if (error?.code !== "EBUSY") {
    throw error;
  }
  await output.save(fallbackWorkbookPath);
  console.log(fallbackWorkbookPath);
}
