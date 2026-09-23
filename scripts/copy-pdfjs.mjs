import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(root, "node_modules", "pdfjs-dist", "build");
const target = resolve(root, "presentation", "static", "pdfjs");

await mkdir(target, { recursive: true });
await Promise.all([
    copyFile(resolve(source, "pdf.mjs"), resolve(target, "pdf.mjs")),
    copyFile(resolve(source, "pdf.worker.mjs"), resolve(target, "pdf.worker.mjs")),
]);
console.log("Copied PDF.js browser assets to presentation/static/pdfjs/");
