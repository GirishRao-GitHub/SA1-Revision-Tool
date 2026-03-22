const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, 'SA1 Assignment Tool.html');
const dataDir = path.join(__dirname, 'data');

console.log('--- SA1 Assignment Tool Builder ---');

// 1. Read existing HTML
let html = '';
try {
  html = fs.readFileSync(htmlPath, 'utf8');
} catch (e) {
  console.error(`ERROR: Could not read ${htmlPath}`, e);
  process.exit(1);
}

// 2. Locate Injection Markers
const startMarker = '// --- ASSIGNMENTS INJECTION START ---';
const endMarker = '// --- ASSIGNMENTS INJECTION END ---';

const startIndex = html.indexOf(startMarker);
const endIndex = html.indexOf(endMarker);

if (startIndex === -1 || endIndex === -1) {
  console.error('ERROR: Could not find injection markers in HTML file.');
  process.exit(1);
}

// 3. Read specific JSON assignment files
const assignmentKeys = ['X1', 'X2', 'X3', 'X4', 'X5', 'X6'];
const assignments = {};

for (const key of assignmentKeys) {
  const jsonPath = path.join(dataDir, `${key}.json`);
  if (fs.existsSync(jsonPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
      assignments[key] = data;
      console.log(`Loaded ${key}.json`);
    } catch (e) {
      console.error(`ERROR parsing ${key}.json:`, e.message);
      process.exit(1);
    }
  } else {
    // If not found in data directory, generate a simple skeleton for it
    assignments[key] = {
      label: `Assignment ${key}`,
      questions: {}
    };
    if (key === 'X2') assignments[key].label = 'Assignment X2: IP & LTC';
    if (key === 'X3') assignments[key].label = 'Assignment X3: Regulation & Solvency';
    console.log(`Generated skeleton for ${key}`);
  }
}

// 4. Construct the output code string
const objStr = JSON.stringify(assignments, null, 2);
const injectionCode = `${startMarker}\nconst ASSIGNMENTS = ${objStr};\n${endMarker}`;

// 5. Inject into HTML
const newHtml = html.substring(0, startIndex) + injectionCode + html.substring(endIndex + endMarker.length);

// 6. Save final HTML
fs.writeFileSync(htmlPath, newHtml, 'utf8');

console.log('SUCCESS: Injected data into SA1 Assignment Tool.html');
console.log('===================================');
