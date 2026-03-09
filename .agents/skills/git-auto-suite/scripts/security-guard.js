#!/usr/bin/env node

/**
 * Git Auto Suite - Security Guard Script
 * ----------------------------------------------------
 * Description: Scans staged files for sensitive data patterns
 * (API keys, passwords, secrets) and checks specific file
 * extensions/names to prevent accidental commits of credentials.
 * 
 * Usage: node scripts/security-guard.js
 * Returns: Exit Code 0 if safe, Exit Code 1 if secrets found.
 */

const { execSync } = require('child_process');
const fs = require('fs');

// ANSI Color Codes for terminal output
const COLORS = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  green: '\x1b[32m',
  cyan: '\x1b[36m'
};

// ==========================================
// 🚨 CONFIGURATION: Define Sensitive Patterns
// ==========================================

const SENSITIVE_PATTERNS = [
  // Generic Secrets
  { name: 'Generic API Key', regex: /(api[_-]?key|apikey)['"\s]*[:=]['"\s]*[a-zA-Z0-9_\-]{20,}/i },
  { name: 'Generic Secret/Token', regex: /(secret|token|auth|bearer)['"\s]*[:=]['"\s]*[a-zA-Z0-9_\-]{20,}/i },
  { name: 'Database Password', regex: /(password|pass|pwd)['"\s]*[:=]['"\s]*[^'"\s,;]+/i },

  // Specific Cloud Providers
  { name: 'AWS Access Key', regex: /(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}/ },
  { name: 'AWS Secret Key', regex: /aws_(?:secret_access_key|session_token)[\s]*=[\s]*[a-zA-Z0-9/+=]{40}/i },
  { name: 'Google Cloud Token', regex: /ya29\.[0-9a-zA-Z\-_]+/i },
  { name: 'OpenAI API Key', regex: /sk-[a-zA-Z0-9]{48}/ },
  { name: 'Stripe Secret Key', regex: /(sk|rk)_live_[0-9a-zA-Z]{24}/i },

  // Cryptography
  { name: 'RSA/DSA Private Key', regex: /-----BEGIN (RSA|DSA|EC|PGP|OPENSSH) PRIVATE KEY-----/ },
];

const FORBIDDEN_FILES = [
  /\.env$/,
  /\.env\..*(local|dev|prod)/,
  /\.pem$/,
  /\.key$/,
  /credentials\.json$/,
  /client_secret.*\.json$/
];

// Files to skip content scanning (e.g., dev configs user explicitly wants to keep)
const SKIP_CONTENT_SCAN = [
  '.vscode/settings.json'
];

// ==========================================
// 🛠️ HELPER FUNCTIONS
// ==========================================

function getStagedFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACM', { encoding: 'utf-8' });
    return output.split('\n').filter(line => line.trim() !== '');
  } catch (err) {
    console.error(`${COLORS.red}❌ Git Error: Failed to get staged files.${COLORS.reset}`, err.message);
    process.exit(1);
  }
}

function getStagedDiff(filepath) {
  try {
    // Only get the added/modified lines (+) from the diff, stripping the '+' sign
    const diff = execSync(`git diff --cached -- "${filepath}"`, { encoding: 'utf-8' });
    return diff
      .split('\n')
      .filter(line => line.startsWith('+') && !line.startsWith('+++'))
      .map(line => line.substring(1)) // Remove the leading '+'
      .join('\n');
  } catch (err) {
    return '';
  }
}

// ==========================================
// 🛡️ MAIN SCAN LOGIC
// ==========================================

async function runSecurityScan() {
  console.log(`${COLORS.cyan}🔍 [Security Guard] Scanning staged files for sensitive data...${COLORS.reset}`);

  const files = getStagedFiles();
  if (files.length === 0) {
    console.log(`${COLORS.yellow}⚠️ No staged files found. Please run 'git add' first.${COLORS.reset}`);
    process.exit(1); // Exit 1 because there is no work to do
  }

  let hasViolations = false;
  let summary = [];

  for (const file of files) {
    // 1. Check if the file itself is forbidden
    const isForbidden = FORBIDDEN_FILES.some(regex => regex.test(file));
    if (isForbidden) {
      summary.push(`- 📄 Forbidden File Type: ${COLORS.red}${file}${COLORS.reset}`);
      hasViolations = true;
      continue;
    }

    // 2. Check the staged content of the file
    if (SKIP_CONTENT_SCAN.includes(file)) {
      console.log(`${COLORS.yellow}⚠️ Skipping content scan for excluded file: ${file}${COLORS.reset}`);
      continue;
    }

    const content = getStagedDiff(file);
    if (!content) continue;

    for (const rule of SENSITIVE_PATTERNS) {
      const match = content.match(rule.regex);
      // Heuristic: Ignore type definitions like 'password: str' or 'password: Any'
      if (match) {
        const line = match[0];

        // Heuristic: Ignore type definitions or property assignments to variables
        // If it doesn't contain a quote after the separator, it's likely a type or variable reference
        const afterSeparator = line.split(/[:=]/)[1]?.trim();
        if (afterSeparator && !afterSeparator.startsWith("'") && !afterSeparator.startsWith('"')) {
          continue;
        }

        // Ignore placeholders
        if (line.includes('your_') || line.includes('FIXME_') || line.includes('placeholder')) {
          continue;
        }

        summary.push(`- 🔑 Sensitive Pattern [${rule.name}] detected in: ${COLORS.red}${file}${COLORS.reset}`);
        hasViolations = true;
      }
    }
  }

  if (hasViolations) {
    console.log('\n========================================================');
    console.log(`${COLORS.red}🚨 SECURITY VIOLATION DETECTED 🚨${COLORS.reset}`);
    console.log('The following issues were found in your staged files:');
    summary.forEach(msg => console.log(msg));
    console.log('\n========================================================');
    console.log(`${COLORS.yellow}Action Required:${COLORS.reset}`);
    console.log('1. Run `git reset` to unstage the files.');
    console.log('2. Remove or obfuscate the sensitive data / passwords.');
    console.log('3. Stage the files again and retry.');
    console.log('========================================================\n');
    process.exit(1); // Block the commit process
  }

  console.log(`${COLORS.green}✅ [Security Guard] No secrets detected. Safe to proceed.${COLORS.reset}\n`);
  process.exit(0);
}

runSecurityScan();
