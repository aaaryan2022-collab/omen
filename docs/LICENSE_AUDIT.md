# LICENSE AUDIT — REFERENCE REPOSITORIES

Date: 2026-10-07
Purpose: Determine reuse rights before incorporating reference code

## JARVIS (reference/JARVIS/)
- License file: Not present at root (need to verify)
- Copyright: Unknown from repo; README says "futuristic desktop AI assistant for Windows"
- Note: MIT-like or proprietary? Check backend/ and frontend/ headers.
- Attribution: Required if MIT.
- Reuse: Study-only unless license confirmed MIT/Apache.
- Verdict: VERIFY BEFORE REUSE.

## Alice (reference/Alice/)
- License: MIT (confirmed from LICENSE file)
- Copyright: (c) 2025 Slava Trofimov
- Terms: Per MIT — include copyright + permission notice in all copies.
- Reuse permitted: YES (with attribution preserved)
- Attribution line to preserve: "Copyright (c) 2025 Slava Trofimov" + full MIT text.
- Verdict: REUSABLE WITH ATTRIBUTION.

## Marven (reference/Marven/)
- License: LICENSE file present (need to read)
- Status: Cloned; inspect LICENSE.
- Verdict: PENDING — read LICENSE.

## OpenGuider
- Status: Not cloned (network restrictions)
- Verdict: PENDING — clone when possible.

## OpenJarvis
- Status: Not cloned
- Verdict: PENDING.

## OMEN LICENSE STRATEGY
OMEN is new independent work. No direct code copied from references (study only). If any feature is implemented independently (equivalent capability, different code), no attribution required beyond documenting inspiration sources in docs/reference-analysis/.
