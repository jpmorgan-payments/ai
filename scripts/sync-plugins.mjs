#!/usr/bin/env node
/**
 * Copies skills/ into every provider plugin.
 *
 *   node scripts/sync-plugins.mjs
 *
 * skills/ is the source of truth. Each providers/<harness>/plugin/skills/ is a disposable
 * copy, because harnesses install a plugin directory rather than reading a shared tree.
 * Everything else in a plugin directory — its plugin.json — is hand-maintained and untouched.
 */
import { cpSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS = join(ROOT, 'skills');
const PROVIDERS = ['claude', 'codex', 'cursor'];

// Repo documentation, not a skill.
const EXCLUDE = new Set([join(SKILLS, 'README.md')]);

for (const provider of PROVIDERS) {
  const dest = join(ROOT, 'providers', provider, 'plugin', 'skills');

  // Wipe first, so a renamed or deleted skill doesn't linger in the copy.
  rmSync(dest, { recursive: true, force: true });
  cpSync(SKILLS, dest, { recursive: true, filter: (src) => !EXCLUDE.has(src) });

  console.log(`✓ providers/${provider}/plugin/skills`);
}
