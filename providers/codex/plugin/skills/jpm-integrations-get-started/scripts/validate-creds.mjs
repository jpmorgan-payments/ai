#!/usr/bin/env node
// Copyright 2025 J.P. Morgan Payments. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Validate a JPM cert + private key pair.
// Usage: node validate-creds.mjs --cert <path> --key <path>
// Prints a single JSON line:
//   {"ok": true, "thumbprint": "AB:CD:..."}
//   {"ok": false, "error": "..."}
// Exits 0 in both cases (consumer parses the JSON).

import { readFileSync } from 'node:fs';
import { X509Certificate, createPrivateKey, createPublicKey } from 'node:crypto';

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--cert') out.cert = argv[++i];
    else if (a === '--key') out.key = argv[++i];
  }
  return out;
}

function emit(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
  process.exit(0);
}

const { cert: certPath, key: keyPath } = parseArgs(process.argv);

if (!certPath || !keyPath) {
  emit({ ok: false, error: 'Usage: validate-creds.mjs --cert <path> --key <path>' });
}

let certPem, keyPem;
try { certPem = readFileSync(certPath); }
catch (e) { emit({ ok: false, error: `Cannot read certificate file at ${certPath}: ${e.message}` }); }

try { keyPem = readFileSync(keyPath); }
catch (e) { emit({ ok: false, error: `Cannot read private key file at ${keyPath}: ${e.message}` }); }

let cert;
try { cert = new X509Certificate(certPem); }
catch (e) { emit({ ok: false, error: `Certificate is not valid PEM/DER X.509: ${e.message}` }); }

let privKey;
try { privKey = createPrivateKey(keyPem); }
catch (e) { emit({ ok: false, error: `Private key is not valid PEM: ${e.message}` }); }

let privPubSpki, certPubSpki;
try { privPubSpki = createPublicKey(privKey).export({ type: 'spki', format: 'der' }); }
catch (e) { emit({ ok: false, error: `Cannot derive public key from private key: ${e.message}` }); }

try { certPubSpki = cert.publicKey.export({ type: 'spki', format: 'der' }); }
catch (e) { emit({ ok: false, error: `Cannot extract public key from certificate: ${e.message}` }); }

if (!Buffer.from(privPubSpki).equals(Buffer.from(certPubSpki))) {
  emit({ ok: false, error: 'Private key does not match the certificate (public keys differ).' });
}

emit({ ok: true, thumbprint: cert.fingerprint });
