# OMEN Security Model
## Principle of Least Privilege and Explicit Authorization

### 1. Security Philosophy
Security in OMEN is enforced at the application code level, not left to LLM prompt compliance. The language model is treated as an untrusted planning and reasoning engine operating under strict deterministic constraints.

---

### 2. Authorization & Permission Scopes
Every tool execution requires an explicit permission scope. Tools are categorized by risk level:

| Scope | Risk Level | Description | Confirmation Policy |
| :--- | :--- | :--- | :--- |
| `read:fs` | Low | Read local files in approved project directories. | Auto-approved once plan is approved. |
| `read:screen` | Low | Capture desktop screenshot for OCR and element detection. | Auto-approved once plan is approved. |
| `write:fs` | Medium | Create, edit, or rename files within the designated workspace. | Auto-approved within approved task scope. |
| `exec:terminal`| High | Execute shell commands or run scripts. | Requires explicit plan approval + command inspection. |
| `net:browser` | Medium | Fetch URL text or navigate public webpages. | Auto-approved within approved task scope. |
| `email:read` | Medium | Read messages and download attachments from Gmail. | Gated by account profile authorization. |
| `email:send` | Critical | Transmit email messages to external recipients. | **Mandatory separate explicit confirmation.** |
| `assign:submit`| Critical | Submit college coursework or assignments to portals. | **Mandatory separate explicit confirmation.** |
| `admin:update` | Critical | Modify application code or install system packages. | Guarded self-improvement policy + user sign-off. |

---

### 3. Untrusted Data Handling (Prompt Injection Defense)
Content ingested from external sources—including webpage HTML, email bodies, PDF attachments, and file contents—is treated as untrusted data:
1. External text is wrapped in data boundaries (`<external_content>...</external_content>`).
2. Instructions discovered inside external documents cannot override OMEN's system instructions, escalate permissions, or trigger unapproved actions.
3. System policies and approval checks are evaluated independently of model output.

---

### 4. Account Isolation: Personal vs. Institute Gmail
- Separate OAuth 2.0 client records and token stores.
- Access tokens stored in secure OS storage (Windows Credential Manager / DPAPI encrypted storage).
- Separate log trails so institute academic activity is cleanly auditable.
- No cross-account credential leakage.
- Disconnect / Revoke access controls provided in Settings.

---

### 5. Emergency Stop Protocol
- **Keyboard Shortcut**: `Ctrl+Shift+Escape` engages an instant hardware stop.
- **Voice Command**: "OMEN STOP" halts all pending tool actions immediately.
- Execution threads are cancelled, active subprocesses terminated, and current state saved to the recovery ledger.
