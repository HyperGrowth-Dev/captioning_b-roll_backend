const { execSync } = require('child_process');
const path = require('path');

// Ensure dist directory exists
const distDir = path.join(__dirname, 'dist');
if (!require('fs').existsSync(distDir)) {
    require('fs').mkdirSync(distDir, { recursive: true });
}

// Install dependencies if needed
try {
    console.log('Installing dependencies...');
    execSync('npm install', { stdio: 'inherit' });
    console.log('Dependencies installed successfully!');
} catch (error) {
    console.error('Failed to install dependencies:', error);
    process.exit(1);
}

// Compile TypeScript files
try {
    console.log('Compiling TypeScript files...');
    execSync('npx tsc --pretty', { 
        stdio: 'inherit',
        env: { ...process.env, FORCE_COLOR: '1' }
    });
    console.log('TypeScript compilation completed successfully!');
} catch (error) {
    console.error('TypeScript compilation failed:', error.message);
    if (error.stdout) console.error('stdout:', error.stdout.toString());
    if (error.stderr) console.error('stderr:', error.stderr.toString());
    process.exit(1);
} 