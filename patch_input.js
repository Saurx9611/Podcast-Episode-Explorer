const fs = require('fs');
let code = fs.readFileSync('app/saved/page.tsx', 'utf8');

const target = `onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full`;

const replacement = `onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && filteredSearches.length > 0) {
                handleRunSearch(filteredSearches[0]);
              }
            }}
            className="w-full`;

code = code.replace(target, replacement);
fs.writeFileSync('app/saved/page.tsx', code);
