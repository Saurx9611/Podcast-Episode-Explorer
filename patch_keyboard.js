const fs = require('fs');
let code = fs.readFileSync('app/saved/page.tsx', 'utf8');

// Find the handleKeyDown
const target = `if (e.key === 'Escape') {
        setIsFormModalOpen(false);
        setIsDeleteModalOpen(false);
        setActiveMenuId(null);
      }`;

const replacement = `if (e.key === 'Escape') {
        setIsFormModalOpen(false);
        setIsDeleteModalOpen(false);
        setActiveMenuId(null);
      }
      
      // Enter to run first search if in search input
      if (e.key === 'Enter' && document.activeElement === searchInputRef.current) {
        e.preventDefault();
        // Since we are in an effect and want the latest state, we should probably handle this in the input's onKeyDown instead.
        // We'll add it there later.
      }`;

code = code.replace(target, replacement);
fs.writeFileSync('app/saved/page.tsx', code);
