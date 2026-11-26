// news-image-20261126 entry program.
//
// The artwork for this entry is a single front-page image, entry.png,
// sitting next to this file. Running the program simply places a copy of
// that image into the output directory the runner provides, so the judge
// can pick it up from the expected location.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const sourceImage = join(here, "entry.png");

if (!existsSync(sourceImage)) {
  throw new Error(`entry.png not found next to main.ts (looked in ${here})`);
}

const outputDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
mkdirSync(outputDir, { recursive: true });

const destination = join(outputDir, "entry.png");
copyFileSync(sourceImage, destination);

// Fail loudly rather than hand the judge a truncated file: the copy must
// carry exactly the same number of bytes as the artwork we shipped.
if (statSync(destination).size !== statSync(sourceImage).size) {
  throw new Error("copied entry.png does not match the source size");
}
