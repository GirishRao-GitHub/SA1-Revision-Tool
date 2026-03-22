const fs = require('fs');
const path = require('path');

function extractSittings(htmlPath) {
    console.log(`Processing ${htmlPath}...`);
    const content = fs.readFileSync(htmlPath, 'utf8');
    
    // Find SITTINGS object
    const startIdx = content.indexOf('SITTINGS = {');
    if (startIdx === -1) {
        console.error(`Could not find SITTINGS in ${htmlPath}`);
        return [];
    }
    
    // Find the opening brace of the object
    const braceStart = content.indexOf('{', startIdx);
    
    // Find the end of the object by matching braces
    let braceCount = 0;
    let endIdx = -1;
    let started = false;
    
    for (let i = braceStart; i < content.length; i++) {
        if (content[i] === '{') {
            braceCount++;
            started = true;
        } else if (content[i] === '}') {
            braceCount--;
        }
        
        if (started && braceCount === 0) {
            endIdx = i + 1;
            break;
        }
    }
    
    if (endIdx === -1) {
        console.error(`Could not find end of SITTINGS object in ${htmlPath}`);
        return [];
    }
    
    const sittingsJsonFragment = content.substring(braceStart, endIdx);
    
    let SITTINGS;
    try {
        // Evaluate as an expression
        SITTINGS = eval('(' + sittingsJsonFragment + ')');
    } catch (e) {
        console.error(`Eval failed for ${htmlPath}:`, e.message);
        // If eval fails, maybe it's because of some outside variables or weirdness.
        // Let's try to see a snippet of what failed
        console.log("Snippet of failed content:", sittingsJsonFragment.substring(0, 500));
        return [];
    }
    
    const keys = Object.keys(SITTINGS);
    console.log(`Found sittings: ${keys.join(', ')}`);
    
    if (!fs.existsSync('data')) fs.mkdirSync('data');
    
    keys.forEach(key => {
        const value = SITTINGS[key];
        const filename = `iai_${key.replace(/[^a-z0-9]/gi, '_')}.json`;
        if (!value.label) value.label = `IAI ${key}`;
        
        fs.writeFileSync(path.join('data', filename), JSON.stringify(value, null, 2));
        console.log(`Saved data/${filename}`);
    });
    
    return keys;
}

const s1 = extractSittings('IAI SA1 Exam Revision Tool 2006-2016.html');
const s2 = extractSittings('IAI SA1 Exam Revision Tool 2017-2025.html');

console.log('Total IAI sittings extracted:', s1.length + s2.length);
