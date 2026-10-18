# License Audit — Reference Repositories

| Repository | License | Copyright Holder | Attribution Requirements | Redistribution / Reuse Policy | Safe for Direct Code Reuse? |
|---|---|---|---|---|---|
| **JARVIS** (`134ertel/JARVIS`) | Unspecified / None explicitly provided in root | 134ertel | N/A | Default copyright applies | **NO**. Study as reference architecture only. Implement independent equivalents. |
| **Alice** (`pmbstyle/Alice`) | MIT License | (c) 2025 Slava Trofimov | Retain copyright notice & permission notice | Permissive; reuse permitted with attribution notice | **YES (with attribution)**, but independent clean implementation preferred. |
| **Marven** (`ahomsi0/Marven`) | GNU Affero General Public License v3.0 (AGPLv3) | Free Software Foundation / ahomsi0 | Full AGPL compliance, source disclosure on network use | **Strong Copyleft**. Copying code triggers AGPLv3 across OMEN | **NO**. Strictly study as reference architecture only. Clean-room independent implementation. |
| **OpenGuider** (`mo-tunn/OpenGuider`) | Apache License 2.0 (Third-Party: browser-use MIT) | mo-tunn | Retain Apache 2.0 notice & attribution | Permissive; reuse permitted with NOTICE & license statements | **YES (with attribution)**; clean-room implementation preferred. |
| **OpenJarvis** (`open-jarvis/OpenJarvis`) | Apache License 2.0 | open-jarvis | Retain Apache 2.0 notice & attribution | Permissive; reuse permitted with NOTICE & license statements | **YES (with attribution)**; clean-room implementation preferred. |

## Strategy for OMEN
1. **Clean-Room Independent Implementation**: OMEN implements independent architectural equivalents for all capabilities found across all 5 repositories to guarantee licensing independence and prevent viral AGPL contamination.
2. **Attribution**: Reference implementations and architectural inspiration are credited explicitly in documentation.
3. **No Direct Copying**: No direct copying of AGPL-licensed code from Marven or unlicensed code from JARVIS.
