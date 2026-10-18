# Repository Inspection Ledger

Complete inspection of all five reference repositories per Protocol requirements.

## JARVIS (105 files total, 96 inspected text/source/config/doc files)

| File | Category | Inspected | Relevant Features | Dependencies | Implementation Notes |
|---|---|---|---|---|---|
| `ARCHITECTURE.md` | documentation | ✓ | anthropic, api, audio, bus | - | - |
| `package.json` | configuration | ✓ | general | - | - |
| `README.md` | documentation | ✓ | anthropic, api, audio, auth | - | Defines: referenced, BUILD_UNINSTALLER |
| `backend/main.py` | source | ✓ | api | Path, dotenv, load_dotenv | Defines: main |
| `backend/requirements.txt` | documentation | ✓ | api, tts, wake, websocket | - | - |
| `backend/app/__init__.py` | source | ✓ | general | - | - |
| `backend/app/ai/backend.py` | source | ✓ | api, local, ollama, openai | Protocol, typing | Defines: AIBackend, is_available, chat, AIBackendError |
| `backend/app/ai/backends.py` | source | ✓ | ollama | AIBackend, app, ollama_backend | Defines: get_backend |
| `backend/app/ai/config.py` | source | ✓ | local, memory, model, ollama | Settings, SettingsManager, app | Defines: get_model, set_model |
| `backend/app/ai/manager.py` | source | ✓ | api, browser, code, computer | Settings, datetime, json | Defines: _to_function_calling_tools, _extract_wrapped_text, _clean_model_content, _is_affirmative |
| `backend/app/ai/ollama_backend.py` | source | ✓ | anthropic, api, code, hardware | AIBackendError, app, config | Defines: is_available, list_models, chat |
| `backend/app/ai/responder.py` | source | ✓ | api, model, reasoning, tool | datetime | Defines: decides, respond |
| `backend/app/ai/__init__.py` | source | ✓ | api, local, model, ollama | - | - |
| `backend/app/api/server.py` | source | ✓ | api, audio, browser, code | asynccontextmanager, asyncio, base64 | Defines: _on_wake_detected, _broadcast, _send_to_all, _start_wakeword_listener |
| `backend/app/api/__init__.py` | source | ✓ | api, bus, memory, security | - | - |
| `backend/app/automation/routines.py` | source | ✓ | code, memory, permission, rag | Path, json, pathlib | Defines: Step, Routine, validate_steps, RoutineStore |
| `backend/app/automation/__init__.py` | source | ✓ | memory, security | - | - |
| `backend/app/control/actions.py` | source | ✓ | browser, code, computer, git | Path, os, pathlib | Defines: _get_shell, _discover_apps, _resolve_target_exe, _find_discovered |
| `backend/app/control/files.py` | source | ✓ | permission, screen | os, pathlib, re | Defines: _resolve_location, _resolve_search_roots, _display_label, _walk_files |
| `backend/app/control/system.py` | source | ✓ | api, code, event, gpu | Optional, Path, pathlib | Defines: check_performance, _cpu_temperature_c, _gpu_stats, _network_up |
| `backend/app/control/__init__.py` | source | ✓ | computer, permission, security, task | app | - |
| `backend/app/core/config.py` | source | ✓ | local, model, ollama | app, dataclass, dataclasses | Defines: from, Settings |
| `backend/app/core/logging_setup.py` | source | ✓ | general | logging | Defines: configure_logging |
| `backend/app/core/__init__.py` | source | ✓ | memory, security, voice | - | - |
| `backend/app/history/action_log.py` | source | ✓ | code, memory, permission, security | datetime, json, pathlib | Defines: ActionEntry, ActionLog, __init__, _load |
| `backend/app/history/__init__.py` | source | ✓ | memory, permission, security | app, the | - |
| `backend/app/memory/config.py` | source | ✓ | editor, memory, permission, security | SettingsManager, app, being | Defines: is_memory_enabled, set_memory_enabled |
| `backend/app/memory/facts.py` | source | ✓ | code, editor, memory, permission | Path, TypedDict, json | Defines: Fact, FactMemory, __init__, _load |
| `backend/app/memory/store.py` | source | ✓ | api, code, memory, ollama | Literal, Path, json | Defines: ConversationMemory, __init__, _load, _save |
| `backend/app/memory/__init__.py` | source | ✓ | api, code, editor, local | Settings | - |
| `backend/app/security/permissions.py` | source | ✓ | api, code, computer, memory | Enum, enum, json | Defines: Scope, PermissionManager, __init__, _load |
| `backend/app/security/__init__.py` | source | ✓ | memory, permission, security | - | - |
| `backend/app/settings/manager.py` | source | ✓ | general | Any, Path, json | Defines: SettingsManager, __init__, load, save |
| `backend/app/settings/__init__.py` | source | ✓ | api | - | - |
| `backend/app/voice/live_transcribe.py` | source | ✓ | api, audio, auth, model | WhisperModel, app, faster_whisper | Defines: _get_model, transcribe_partial |
| `backend/app/voice/stt.py` | source | ✓ | api, audio, engine, local | Hugging, disk, faster_whisper | Defines: _get_model, transcribe |
| `backend/app/voice/tts.py` | source | ✓ | api, audio, engine, speech | os, pyttsx3, tempfile | Defines: synthesize |
| `backend/app/voice/wakeword.py` | source | ✓ | api, audio, event, git | logging, openWakeWord, queue | Defines: WakeWordListener, __init__, is_running, is_paused |
| `backend/app/voice/wakeword_config.py` | source | ✓ | memory, model, permission, security | SettingsManager, app | Defines: is_wakeword_enabled, set_wakeword_enabled |
| `backend/app/voice/__init__.py` | source | ✓ | engine, local, model, reasoning | app | - |
| `frontend/electron.vite.config.ts` | source | ✓ | plugin | @vitejs/plugin-react, electron-vite, path | - |
| `frontend/package-lock.json` | configuration | ✓ | agent, browser, bus, code | - | - |
| `frontend/package.json` | configuration | ✓ | auth, git, github, plugin | - | - |
| `frontend/tsconfig.json` | configuration | ✓ | general | - | - |
| `frontend/tsconfig.node.json` | configuration | ✓ | general | - | - |
| `frontend/tsconfig.web.json` | configuration | ✓ | general | - | - |
| `frontend/src/main/appSettings.ts` | source | ✓ | permission, security | electron, fs, path | Defines: settingsPath, load, save, isMicrophoneEnabled |
| `frontend/src/main/autostart.ts` | source | ✓ | api | electron | Defines: setAutostart, isAutostartEnabled, wasLaunchedHidden |
| `frontend/src/main/backendManager.ts` | source | ✓ | code, schedule, terminal | child_process, fs, path | Defines: getBackendStatus, onBackendStatusChange, setStatus, pollHealth |
| `frontend/src/main/index.ts` | source | ✓ | browser, event, model, permission | ./appSettings, ./autostart, ./backendManager | Defines: createWindow, showMainWindow, withWindow, openSettings |
| `frontend/src/main/ipc.ts` | source | ✓ | event, memory, security, voice | ./appSettings, ./autostart, ./backendManager | Defines: registerIpcHandlers |
| `frontend/src/main/tray.ts` | source | ✓ | tool | ./appSettings, electron, path | Defines: createTray, updateTrayMenu, getTray |
| `frontend/src/main/updater.ts` | source | ✓ | auth, code, git, github | electron, electron-updater | Defines: onUpdateStatusChange, emit, emitError, ensureWired |
| `frontend/src/main/wakewordBridge.ts` | source | ✓ | event, local, model, schedule | ws | Defines: connect, startWakewordBridge, stopWakewordBridge |
| `frontend/src/preload/index.d.ts` | source | ✓ | api | ./index | - |
| `frontend/src/preload/index.ts` | source | ✓ | api, code, event, memory | electron | Defines: subscribe |
| `frontend/src/renderer/index.html` | source | ✓ | security | - | - |
| `frontend/src/renderer/public/vad.worklet.bundle.min.js` | source | ✓ | audio, speech | - | Defines: s, o |
| `frontend/src/renderer/src/App.tsx` | source | ✓ | general | ./components/ErrorBoundary, ./components/Layout | Defines: App |
| `frontend/src/renderer/src/main.tsx` | source | ✓ | general | ./App, react, react-dom/client | - |

*(Truncated in table preview: 105 total files indexed in ledger manifest)*

## Alice (250 files total, 199 inspected text/source/config/doc files)

| File | Category | Inspected | Relevant Features | Dependencies | Implementation Notes |
|---|---|---|---|---|---|
| `.markdownlint.json` | configuration | ✓ | general | - | - |
| `.prettierrc.json` | configuration | ✓ | general | - | - |
| `electron-builder.json5` | configuration | ✓ | bus, git, github, model | - | - |
| `index.html` | source | ✓ | security | - | - |
| `package-lock.json` | configuration | ✓ | api, code, cron, engine | - | - |
| `package.json` | configuration | ✓ | api, auth, cron, embedding | - | - |
| `postcss.config.js` | source | ✓ | plugin | - | - |
| `README.md` | documentation | ✓ | api, audio, calendar, code | - | - |
| `tailwind.config.js` | source | ✓ | plugin | - | - |
| `tsconfig.json` | configuration | ✓ | general | - | - |
| `tsconfig.node.json` | configuration | ✓ | general | - | - |
| `vite.config.ts` | source | ✓ | api, code, event, openai | @tailwindcss/vite, @vitejs/plugin-vue, node:fs | - |
| `.vscode/extensions.json` | configuration | ✓ | code, plugin | - | - |
| `.vscode/launch.json` | configuration | ✓ | code, task, terminal | - | - |
| `.vscode/settings.json` | configuration | ✓ | general | - | - |
| `.vscode/tasks.json` | configuration | ✓ | code, task | - | - |
| `backend/.golangci.yml` | configuration | ✓ | code, git, github, local | - | - |
| `backend/main.go` | source | ✓ | api, model | - | - |
| `backend/internal/api/embeddings.go` | source | ✓ | api, code, embedding, git | - | - |
| `backend/internal/api/handler.go` | source | ✓ | api, code, embedding, model | - | - |
| `backend/internal/api/models.go` | source | ✓ | api, audio, embedding, model | - | - |
| `backend/internal/api/models_handlers.go` | source | ✓ | api, code, embedding, git | - | - |
| `backend/internal/api/stt.go` | source | ✓ | api, audio, code, git | - | - |
| `backend/internal/api/tts.go` | source | ✓ | api, audio, code, git | - | - |
| `backend/internal/config/config.go` | source | ✓ | embedding, model, tts, whisper | - | - |
| `backend/internal/downloader/downloader.go` | source | ✓ | code, model | - | - |
| `backend/internal/embedded/assets.go` | source | ✓ | git, local, model, permission | - | - |
| `backend/internal/minilm/onnx_embeddings.go` | source | ✓ | agent, code, embedding, git | - | Defines: with |
| `backend/internal/minilm/types.go` | source | ✓ | embedding, model, provider | - | - |
| `backend/internal/models/manager.go` | source | ✓ | embedding, model, tts, voice | - | - |
| `backend/internal/piper/tts.go` | source | ✓ | agent, audio, bus, code | - | - |
| `backend/internal/server/server.go` | source | ✓ | api, audio, auth, embedding | - | - |
| `backend/internal/whisper/stt.go` | source | ✓ | agent, audio, code, model | - | - |
| `docs/custom-avatars.md` | documentation | ✓ | audio, code, git, github | - | - |
| `docs/custom-tools.md` | documentation | ✓ | editor, local, model, openai | - | Defines: name, tools, run |
| `docs/functions.json` | configuration | ✓ | browser, calendar, code, computer | - | Defines: whenever, returns, to |
| `docs/setupInstructions.md` | documentation | ✓ | api, auth, code, embedding | - | - |
| `docs/systemPrompt.md` | documentation | ✓ | code | - | - |
| `docs/toolsInstructions.md` | documentation | ✓ | api, docker, local, tool | - | - |
| `electron/electron-env.d.ts` | source | ✓ | code, plugin | - | - |
| `electron/main/authManager.ts` | source | ✓ | api, auth, browser, calendar | ./googleAuthManager, ./windowManager, electron | Defines: registerAuthIPCHandlers, closeAuthWindowAndNotify, startAuthServer, stopAuthServer |
| `electron/main/backendManager.ts` | source | ✓ | api, code, embedding, event | axios, child_process, electron | Defines: BackendManager |
| `electron/main/codexAppServerManager.ts` | source | ✓ | agent, api, auth, code | electron, node:child_process, node:events | Defines: CodexAppServerClient, CodexAppServerManager, normalizeAccountStatus, compactObject |
| `electron/main/customAvatarsManager.ts` | source | ✓ | code | ../../types/customAvatars, electron, node:fs/promises | Defines: getCustomizationRoot, getAvatarsRoot, ensureDirectoryExists, fileExists |
| `electron/main/customToolsManager.ts` | source | ✓ | tool | electron, node:fs, node:fs/promises | Defines: getCustomizationRoot, getScriptsRoot, slugify, ensureDirectoryExists |
| `electron/main/desktopManager.ts` | source | ✓ | browser, computer, event, security | ./securityBoundaries, child_process, electron | Defines: DesktopManager |
| `electron/main/googleAuthManager.ts` | source | ✓ | api, auth, calendar, code | electron, googleapis, node:fs | Defines: getOAuth2Client, loadTokens, saveTokens, clearTokens |
| `electron/main/googleCalendarManager.ts` | source | ✓ | api, auth, calendar, event | googleapis | Defines: listEvents, createEvent, updateEvent, deleteEvent |
| `electron/main/googleGmailManager.ts` | source | ✓ | api, auth, code, gmail | googleapis | Defines: listMessages, getMessage, decodeBase64UrlToString, extractPlainTextBody |
| `electron/main/hotkeyManager.ts` | source | ✓ | event, screen | ./windowManager, electron | Defines: registerHotkey, registerMicrophoneToggleHotkey, registerMutePlaybackHotkey, registerTakeScreenshotHotkey |
| `electron/main/index.ts` | source | ✓ | auth, browser, code, embedding | ./ragDocumentStore, ./schedulerManager, ./settingsManager | Defines: isBrowserContextToolEnabled, initializeManagers, handleContextAction, startWebSocketServer |
| `electron/main/ipcManager.ts` | source | ✓ | api, auth, browser, calendar | ./settingsManager, axios, electron | Defines: isBrowserContextToolEnabled, getCachedAllowedHttpOrigins, sendHttpStreamEvent, readSseDataFrame |
| `electron/main/memoryManager.ts` | source | ✓ | embedding, local, memory, openai | ./memorySearch, ./thoughtVectorStore, node:crypto | Defines: cosineSimilarity, convertEmbeddingToBuffer, convertBufferToEmbedding, normalizeEmbeddings |
| `electron/main/memorySearch.ts` | source | ✓ | code, memory | - | Defines: tokenizeMemoryQuery, buildMemoryFtsQuery, initializeMemorySearch |
| `electron/main/ragDocumentStore.ts` | source | ✓ | api, code, database, embedding | electron, node:crypto, node:fs | Defines: initDb, ensureRagEmbeddingModelColumns, initializeIndex, initializeRagStore |
| `electron/main/schedulerManager.ts` | source | ✓ | cron, database, schedule, task | ./thoughtVectorStore, node-cron, node:child_process | Defines: initializeSchedulerDB, loadAndScheduleAllTasks, scheduleTask, executeTask |
| `electron/main/securityBoundaries.ts` | source | ✓ | api, local, ollama, openai | node:path | Defines: parseHttpUrl, getAllowedHttpOrigins, getHttpOriginsRequiringApproval, validateHttpBridgeUrl |
| `electron/main/settingsManager.ts` | source | ✓ | api, auth, code, embedding | ./settingsSecurity, electron, node:fs/promises | Defines: saveSettings, loadSettings, deleteSettingsFile, fileExists |
| `electron/main/settingsSecurity.ts` | source | ✓ | api, openai, router | - | Defines: splitSecretSettings, mergeSecretSettings, hasSecretValues |
| `electron/main/thoughtVectorStore.ts` | source | ✓ | api, code, database, embedding | axios, electron, node:fs | Defines: initDB, runMultilingualLocalEmbeddingMigration, generateLocalEmbeddings, waitForLocalEmbeddingsReady |

*(Truncated in table preview: 250 total files indexed in ledger manifest)*

## Marven (300 files total, 289 inspected text/source/config/doc files)

| File | Category | Inspected | Relevant Features | Dependencies | Implementation Notes |
|---|---|---|---|---|---|
| `declarations.d.ts` | source | ✓ | general | - | - |
| `HANDOFF.md` | documentation | ✓ | agent, anthropic, api, code | - | - |
| `middleware.ts` | source | ✓ | api, git, local, provider | @/lib/apiGuards, next/server | Defines: middleware |
| `next-env.d.ts` | source | ✓ | api | - | - |
| `next.config.ts` | source | ✓ | local, rag, sqlite | next | - |
| `package-lock.json` | configuration | ✓ | anthropic, api, bus, code | - | - |
| `package.json` | configuration | ✓ | anthropic, code, git, github | - | - |
| `PRIVACY.md` | documentation | ✓ | agent, anthropic, api, audio | - | - |
| `README.md` | documentation | ✓ | agent, anthropic, api, audio | - | - |
| `tsconfig.json` | configuration | ✓ | plugin | - | - |
| `app/globals.css` | source | ✓ | agent, code, editor, event | - | - |
| `app/layout.tsx` | source | ✓ | local, rag | next, next/font/google | Defines: RootLayout |
| `app/page.tsx` | source | ✓ | agent, anthropic, api, code | @/hooks/useVoice, @/lib/userProfile, @/package.json | Defines: openUrl, parseTimer, detectClipboardAction, createMessage |
| `app/api/agent/approve/route.ts` | source | ✓ | agent | @/lib/agent/approvals, next/server | Defines: POST |
| `app/api/agent/checkpoints/route.ts` | source | ✓ | agent | @/lib/workspacePaths, @/lib/workspaceState, fs/promises | Defines: ownedCheckpointPath, GET, POST |
| `app/api/agent/inline-edit/route.ts` | source | ✓ | agent, anthropic, api, code | @/lib/anthropic, @/lib/groq, @/lib/openai | Defines: POST |
| `app/api/agent/stream/route.ts` | source | ✓ | agent, anthropic, api, code | @/lib/agent/groq, @/lib/agent/loop, @/lib/agent/nim | Defines: POST, sseHeaders |
| `app/api/agent/summarize/route.ts` | source | ✓ | anthropic, api, auth, code | @/types, next/server | Defines: POST |
| `app/api/agent/verify/route.ts` | source | ✓ | agent, api, code, event | @/lib/agent/tools, @/lib/apiGuards, fs/promises | Defines: sseHeaders, packageManagerFor, isDefaultNpmTestScript, detectCommands |
| `app/api/chat/route.ts` | source | ✓ | anthropic, local, model, nvidia | @/lib/commandParser, @/lib/executeCommand, @/lib/groq | Defines: POST |
| `app/api/chat/parse-document/route.ts` | source | ✓ | memory | next/server | Defines: POST |
| `app/api/completion/inline/route.ts` | source | ✓ | anthropic, event, model, ollama | @/lib/completion/contextWindow, @/lib/completion/fimPrompt, @/lib/completion/providers | Defines: isValid, POST |
| `app/api/diagnostics/route.ts` | source | ✓ | anthropic, api, openai, provider | @/app/api/index/_state, @/package.json, crypto | Defines: GET |
| `app/api/files/read/route.ts` | source | ✓ | agent | @/lib/agent/checkpointStore, @/lib/workspaceState, fs/promises | Defines: GET |
| `app/api/health/route.ts` | source | ✓ | auth | next/server | Defines: GET |
| `app/api/index/_state.ts` | source | ✓ | agent, api, code, embedding | @/lib/index/embedder, @/lib/index/indexer, @/lib/index/store | Defines: isEnabled, setEnabled, getExcludePatterns, setExcludePatterns |
| `app/api/index/cancel/route.ts` | source | ✓ | general | ../_state, next/server | Defines: POST |
| `app/api/index/clear/route.ts` | source | ✓ | general | ../_state, next/server | Defines: POST |
| `app/api/index/delete-file/route.ts` | source | ✓ | general | ../_state, next/server, path | Defines: POST |
| `app/api/index/run-full/route.ts` | source | ✓ | api, code, event | ../_state, next/server | Defines: POST |
| `app/api/index/search/route.ts` | source | ✓ | code | ../_state, @/lib/index/search, next/server | Defines: POST |
| `app/api/index/set-enabled/route.ts` | source | ✓ | general | ../_state, next/server | Defines: POST |
| `app/api/index/set-options/route.ts` | source | ✓ | general | ../_state, next/server | Defines: GET, POST |
| `app/api/index/status/route.ts` | source | ✓ | general | ../_state, next/server | Defines: GET |
| `app/api/index/update-file/route.ts` | source | ✓ | general | ../_state, next/server, path | Defines: POST |
| `app/api/mcp/route.ts` | source | ✓ | api, mcp | @/lib/apiGuards, @/lib/mcpClient, @/types | Defines: GET, POST |
| `app/api/memory/route.ts` | source | ✓ | memory | @/lib/memoryClient, next/server | Defines: getContext, getScope, GET, POST |
| `app/api/models/route.ts` | source | ✓ | anthropic, api, local, model | @/lib/groq, @/lib/nim, @/lib/ollama | Defines: GET |
| `app/api/news/route.ts` | source | ✓ | api | next/server | Defines: GET |
| `app/api/storage/conversations/route.ts` | source | ✓ | api, sqlite | @/lib/apiGuards, @/lib/serverConversationStore, next/server | Defines: GET, PUT |
| `app/api/stt/route.ts` | source | ✓ | api, audio, auth, memory | next/server | Defines: POST |
| `app/api/system/route.ts` | source | ✓ | api | @/lib/apiGuards, child_process, next/server | Defines: GET, POST |
| `app/api/tts/route.ts` | source | ✓ | api, audio, browser, code | child_process, fs, next/server | Defines: isArabic, synthesizeWithElevenLabs, POST |
| `app/api/vision/route.ts` | source | ✓ | api, auth, code, local | crypto, fs, next/server | Defines: POST |
| `app/api/weather/route.ts` | source | ✓ | agent, api, code, git | next/server | Defines: wmoCodeToDescription, GET |
| `app/api/workspace/clone/route.ts` | source | ✓ | code, git | child_process, fs/promises, next/server | Defines: runClone, inferRepoName, POST |
| `app/api/workspace/create/route.ts` | source | ✓ | general | @/lib/workspacePaths, @/lib/workspaceState, fs/promises | Defines: POST |
| `app/api/workspace/file-ops/route.ts` | source | ✓ | api | @/lib/apiGuards, @/lib/workspaceState, fs/promises | Defines: getRoot, safePath, assertDeletable, copyRecursive |
| `app/api/workspace/files/route.ts` | source | ✓ | git, memory, permission | @/lib/workspacePaths, @/lib/workspaceState, fs/promises | Defines: getRoot, errorStatus, listRecursive, GET |
| `app/api/workspace/files/raw/route.ts` | source | ✓ | api, browser, code, editor | @/lib/workspacePaths, @/lib/workspaceState, fs/promises | Defines: GET |
| `app/api/workspace/git/route.ts` | source | ✓ | agent, api, git | @/lib/agent/git, @/lib/apiGuards, @/lib/gitUtils | Defines: POST |
| `app/api/workspace/git-assist/route.ts` | source | ✓ | agent, anthropic, code, engine | @/lib/agent/git, @/lib/groq, @/lib/workspaceState | Defines: streamToText, completeText, makePrompt, limit |
| `app/api/workspace/preview/[...slug]/route.ts` | source | ✓ | api, browser, code, sandbox | @/lib/workspacePaths, @/lib/workspaceState, fs/promises | Defines: GET |
| `app/api/workspace/release-checklist/route.ts` | source | ✓ | agent, git | @/lib/agent/git, @/lib/workspaceState, fs/promises | Defines: readPackage, listDist, scriptCommand, POST |
| `app/api/workspace/review/route.ts` | source | ✓ | agent, code, git, local | @/lib/agent/git, @/lib/workspaceState, next/server | Defines: extractChangedFiles, packageDiffNeedsLockfile, buildFindings, POST |
| `app/api/workspace/scan/route.ts` | source | ✓ | local | @/lib/workspaceState, fs/promises, next/server | Defines: exists, readPackageJson, detectPackageManager, commandFor |
| `app/api/workspace/search/route.ts` | source | ✓ | code, editor, git, local | @/lib/workspaceState, child_process, next/server | Defines: parseGrepLine, POST |
| `app/api/workspace/search-replace/route.ts` | source | ✓ | api, code, git | @/lib/apiGuards, @/lib/workspacePaths, @/lib/workspaceState | Defines: POST |
| `app/api/workspace/serve/route.ts` | source | ✓ | sandbox, security | @/lib/workspacePaths, @/lib/workspaceState, fs/promises | Defines: GET |
| `app/components/marven/AgentPanel.tsx` | source | ✓ | agent, browser, code, event | ./SlashMenu, ./ToolCallCard, react | Defines: fileToAttachment, AgentPanel, updateMentionTrigger, pickMention |

*(Truncated in table preview: 300 total files indexed in ledger manifest)*

## OpenGuider (126 files total, 112 inspected text/source/config/doc files)

| File | Category | Inspected | Relevant Features | Dependencies | Implementation Notes |
|---|---|---|---|---|---|
| `AGENTS.md` | documentation | ✓ | agent, bus, code, git | - | - |
| `main.js` | source | ✓ | agent, api, audio, auth | - | Defines: getVirtualDisplayBounds, resizeCursorOverlayToVirtualBounds, debugLog, recordPerformanceMetric |
| `package-lock.json` | configuration | ✓ | agent, anthropic, api, code | - | - |
| `package.json` | configuration | ✓ | anthropic, api, auth, browser | - | - |
| `preload.js` | source | ✓ | agent, api, browser, speech | - | - |
| `README.md` | documentation | ✓ | agent, api, audio, browser | - | - |
| `THIRD_PARTY_LICENSES.md` | documentation | ✓ | agent, api, auth, browser | - | - |
| `docs/open-guider-guide-en.md` | documentation | ✓ | api, gemini, model, permission | - | - |
| `docs/open-guider-guide-tr.md` | documentation | ✓ | api, gemini, model, provider | - | Defines: yazin |
| `docs/OpenGuider - Configuration (EN) .pdf` | documentation | ✓ | code, router | - | - |
| `docs/OpenGuider - Configuration(TR).pdf` | documentation | ✓ | api, code, router | - | - |
| `landing/index.html` | source | ✓ | api, code, git, github | - | - |
| `landing/landing.css` | source | ✓ | api, browser, editor, event | - | - |
| `landing/landing.js` | source | ✓ | api, audio, browser, event | - | Defines: createCard, renderModules, renderDownloads, initConfigurePanel |
| `landing/README.md` | documentation | ✓ | git, github | - | - |
| `renderer/approval.html` | source | ✓ | event | - | - |
| `renderer/cursor.html` | source | ✓ | event, gpu, screen | - | Defines: showCursorAt, hideCursor |
| `renderer/index.html` | source | ✓ | agent, anthropic, api, browser | - | - |
| `renderer/settings.html` | source | ✓ | agent, anthropic, api, browser | - | - |
| `renderer/widget.html` | source | ✓ | browser, task | - | - |
| `renderer/components/execution-log/execution-log.css` | source | ✓ | screen | - | - |
| `renderer/components/execution-log/ExecutionLog.js` | source | ✓ | browser, event, screen | - | Defines: ExecutionLog |
| `renderer/components/step-approval/step-approval.css` | source | ✓ | api, code, editor, screen | - | - |
| `renderer/components/step-approval/StepApprovalCard.js` | source | ✓ | browser, editor, event, screen | - | Defines: StepApprovalCard |
| `renderer/css/style.css` | source | ✓ | agent, api, browser, code | - | - |
| `renderer/css/widget.css` | source | ✓ | api, browser, event, rag | - | - |
| `renderer/js/app.js` | source | ✓ | general | ./panel/bootstrap.js | - |
| `renderer/js/settings.js` | source | ✓ | agent, anthropic, api, browser | - | Defines: showToast, init, activateProvider, setSelectValue |
| `renderer/js/widget.js` | source | ✓ | api, event, task | ./widget/task-widget.js | - |
| `renderer/js/panel/bootstrap.js` | source | ✓ | agent, api, audio, browser | ./messaging.js, ./plan-view.js, ./ptt.js | Defines: createPanelLogger, isActiveBrowserExecution, getModeBarPluginLabel, getTrustPresentation |
| `renderer/js/panel/messaging.js` | source | ✓ | agent, api, code, rag | - | Defines: createMessagingController, cancelMessage, syncSession, syncSessionInternal |
| `renderer/js/panel/plan-view.js` | source | ✓ | browser, code, plugin, task | - | Defines: createPlanView, normalizeRichText, escapeHtml, renderRichTextHtml |
| `renderer/js/panel/ptt.js` | source | ✓ | api, audio, auth, code | - | Defines: createPttController, startPTT, stopPTT, resolveSttProvider |
| `renderer/js/panel/state.js` | source | ✓ | agent, audio, browser, screen | - | Defines: createPanelState, getSettings, setSettings, getSetting |
| `renderer/js/panel/tts.js` | source | ✓ | api, audio, browser, event | - | Defines: createTtsPlaybackController, getTtsVolume, getTtsRate, stopDirectAudio |
| `renderer/js/panel/ui.js` | source | ✓ | agent, api, browser, code | - | Defines: queryPanelDom, createPanelUI, normalizeUrl, buildLink |
| `renderer/js/widget/task-widget.js` | source | ✓ | agent, api, browser, bus | - | Defines: createTaskWidgetController, formatPlainSummary, isActiveBrowserExecution, getBrowserExecutionName |
| `src/logger.js` | source | ✓ | general | - | Defines: ensureDir, rotateLogsIfNeeded, writeLine, initializeLogger |
| `src/performance-metrics.js` | source | ✓ | event, local | - | Defines: PerformanceMetrics |
| `src/platform-capabilities.js` | source | ✓ | gemini, ollama, openai, provider | - | Defines: getPlatformCapabilities, normalizeSettingsForPlatform, resolveEffectiveTtsProvider |
| `src/screenshot.js` | source | ✓ | code, screen | - | Defines: mapSourceToDisplay, rawCaptureAllScreens, captureAllScreens |
| `src/secure-store.js` | source | ✓ | api, gemini, openai, rag | - | Defines: SecureStore |
| `src/store.js` | source | ✓ | agent, anthropic, api, browser | - | Defines: createStore |
| `src/agent/evaluator-chain.js` | source | ✓ | screen | - | Defines: evaluateStep |
| `src/agent/executor-chain.js` | source | ✓ | screen | - | Defines: locateStepTarget |
| `src/agent/fallback-manager.js` | source | ✓ | general | - | Defines: FallbackManager, createFallbackManager |
| `src/agent/interaction-pipeline.js` | source | ✓ | embedding, engine, model, screen | - | Defines: logPreLayer, logPostLayer, InteractionPipeline, createInteractionPipeline |
| `src/agent/llm-client.js` | source | ✓ | general | - | Defines: loadLangChainCore, invokeStructuredChain |
| `src/agent/planner-chain.js` | source | ✓ | planner, screen, task | - | Defines: summarizeScreenshots, planGoal |
| `src/agent/replanner-chain.js` | source | ✓ | planner, screen, task | - | Defines: replanGoal |
| `src/agent/schemas.js` | source | ✓ | model, planner, screen | - | Defines: extractJSONObject, parseStructuredJSON |
| `src/agent/task-orchestrator.js` | source | ✓ | agent, browser, engine, event | - | Defines: normalizeExecutionMode, normalizeTrustLevel, TaskOrchestrator |
| `src/agent/tools/capture-screen-tool.js` | source | ✓ | screen, tool | - | Defines: captureScreenTool |
| `src/agent/tools/plan-tool.js` | source | ✓ | screen, tool | - | Defines: updatePlanTool, requestUserInputTool |
| `src/agent/tools/pointer-tool.js` | source | ✓ | screen, tool | - | Defines: normalizeCoordinate, resolveTargetDisplay, resolveCalibrationForDisplay, emitPointerTool |
| `src/ai/index.js` | source | ✓ | anthropic, api, auth, code | - | Defines: streamClaude, buildClaudeMessages, streamOpenAI, streamOpenRouter |
| `src/ai/structured.js` | source | ✓ | api, auth, model, provider | - | Defines: debugStructuredLog, formatStructuredUserError, invokeStructuredResponse |
| `src/context/context-analyzer.js` | source | ✓ | api, screen, vision | - | Defines: log, analyzeContext |
| `src/context/embedding-matcher.js` | source | ✓ | browser, embedding, local, model | - | Defines: log, loadEmbeddingModel, getEmbedding, getBatchEmbeddings |
| `src/context/prompt-enricher.js` | source | ✓ | general | - | Defines: formatOCRElements, formatWindowInfo, formatMatchedElements, buildEnrichedPrompt |

*(Truncated in table preview: 126 total files indexed in ledger manifest)*

## OpenJarvis (2169 files total, 2107 inspected text/source/config/doc files)

| File | Category | Inspected | Relevant Features | Dependencies | Implementation Notes |
|---|---|---|---|---|---|
| `.pre-commit-config.yaml` | configuration | ✓ | git, github | - | - |
| `CHANGELOG.md` | documentation | ✓ | agent, anthropic, api, auth | - | Defines: has, capabilities, local, constraint |
| `CODE_OF_CONDUCT.md` | documentation | ✓ | bus, code, email, event | - | - |
| `CONTRIBUTING.md` | documentation | ✓ | agent, api, browser, code | - | Defines: helpers |
| `mkdocs.yml` | configuration | ✓ | agent, api, auth, code | - | - |
| `pyproject.toml` | configuration | ✓ | agent, anthropic, api, auth | - | - |
| `README.md` | documentation | ✓ | agent, api, audio, auth | - | Defines: constraints |
| `render.yaml` | configuration | ✓ | api, auth, docker, engine | - | - |
| `REVIEW.md` | documentation | ✓ | agent, api, bus, code | - | - |
| `uv.lock` | configuration | ✓ | anthropic, audio, tool, vision | - | - |
| `configs/openjarvis/config.toml` | configuration | ✓ | agent, api, auth, code | - | - |
| `configs/openjarvis/examples/chat-simple.toml` | configuration | ✓ | agent, api, browser, engine | - | - |
| `configs/openjarvis/examples/code-assistant.toml` | configuration | ✓ | agent, code, engine, model | - | - |
| `configs/openjarvis/examples/deep-research.toml` | configuration | ✓ | agent, email, engine, memory | - | - |
| `configs/openjarvis/examples/full-system-access.toml` | configuration | ✓ | agent, code, engine, git | - | - |
| `configs/openjarvis/examples/morning-digest-linux.toml` | configuration | ✓ | agent, api, calendar, code | - | - |
| `configs/openjarvis/examples/morning-digest-mac.toml` | configuration | ✓ | agent, api, calendar, code | - | - |
| `configs/openjarvis/examples/morning-digest-minimal.toml` | configuration | ✓ | api, audio, auth, calendar | - | - |
| `configs/openjarvis/examples/scheduled-monitor.toml` | configuration | ✓ | agent, email, engine, memory | - | - |
| `configs/openjarvis/examples/spec-search-quickstart.toml` | configuration | ✓ | agent, api, code, engine | - | - |
| `configs/openjarvis/prompts/personas/jarvis.md` | documentation | ✓ | local, voice | - | - |
| `configs/openjarvis/prompts/personas/neutral.md` | documentation | ✓ | voice | - | - |
| `deploy/docker/docker-compose.gpu.nvidia.yml` | configuration | ✓ | docker, gpu, nvidia, ollama | - | - |
| `deploy/docker/docker-compose.gpu.rocm.yml` | configuration | ✓ | docker, gpu | - | - |
| `deploy/docker/docker-compose.yml` | configuration | ✓ | api, auth, docker, engine | - | - |
| `deploy/windows/README.md` | documentation | ✓ | api, auth, docker, git | - | - |
| `desktop/src-tauri/src/overlay.html` | source | ✓ | code, engine, event, gemini | - | Defines: genId, renderAll, bubble, scroll |
| `docs/desktop-auto-update.md` | documentation | ✓ | code, git, github, local | - | - |
| `docs/downloads.md` | documentation | ✓ | agent, api, browser, code | - | Defines: provides |
| `docs/gen_install_script.py` | source | ✓ | git, github | Path, mkdocs_gen_files, pathlib | - |
| `docs/gen_ref_pages.py` | source | ✓ | api, code | Path, mkdocs_gen_files, pathlib | - |
| `docs/index.md` | documentation | ✓ | agent, anthropic, api, auth | - | Defines: constraints |
| `docs/leaderboard.md` | documentation | ✓ | api, browser, email, hardware | - | - |
| `docs/telemetry.md` | documentation | ✓ | api, auth, code, email | - | Defines: enums |
| `docs/architecture/agents.md` | documentation | ✓ | agent, anthropic, api, auth | - | Defines: BaseAgent, __init__, run, attribute |
| `docs/architecture/channels.md` | documentation | ✓ | agent, api, bus, code | - | Defines: BaseChannel, TelegramChannel, DiscordChannel, SlackChannel |
| `docs/architecture/design-principles.md` | documentation | ✓ | agent, anthropic, api, bus | - | Defines: or, MyEngine, generate, stream |
| `docs/architecture/engine.md` | documentation | ✓ | agent, anthropic, api, code | - | Defines: InferenceEngine, generate, stream, list_models |
| `docs/architecture/intelligence.md` | documentation | ✓ | agent, anthropic, api, code | - | Defines: ModelSpec, populates, creates, IntelligenceConfig |
| `docs/architecture/learning.md` | documentation | ✓ | agent, api, bus, code | - | Defines: RouterPolicy, select_model, QueryAnalyzer, analyze |
| `docs/architecture/memory.md` | documentation | ✓ | agent, api, audio, code | - | Defines: MemoryBackend, store, retrieve, delete |
| `docs/architecture/overview.md` | documentation | ✓ | agent, anthropic, api, bus | - | Defines: weights, that, OllamaEngine, under |
| `docs/architecture/query-flow.md` | documentation | ✓ | agent, api, bus, code | - | Defines: with, TelemetryRecord, in |
| `docs/architecture/security.md` | documentation | ✓ | agent, api, bus, code | - | Defines: InferenceEngine, OllamaEngine, GuardrailsEngine, loaded |
| `docs/architecture/skills.md` | documentation | ✓ | agent, auth, bus, code | - | Defines: SkillManifest |
| `docs/assets/showcase/README.md` | documentation | ✓ | api, auth, email, memory | - | - |
| `docs/deployment/api-server.md` | documentation | ✓ | agent, api, auth, browser | - | - |
| `docs/deployment/docker.md` | documentation | ✓ | agent, api, auth, code | - | - |
| `docs/deployment/index.md` | documentation | ✓ | agent, api, docker, gpu | - | - |
| `docs/deployment/launchd.md` | documentation | ✓ | agent, api, auth, engine | - | - |
| `docs/deployment/render.md` | documentation | ✓ | api, auth, database, docker | - | - |
| `docs/deployment/systemd.md` | documentation | ✓ | api, auth, code, engine | - | - |
| `docs/design/2026-05-05-apple-silicon-pearl-mining-design.md` | documentation | ✓ | agent, api, auth, code | - | Defines: of, LlamaCppPearlMetalProvider, detect, hashrate |
| `docs/design/2026-05-05-apple-silicon-pearl-mining-plan-v1.md` | documentation | ✓ | agent, api, code, engine | - | Defines: test_pearl_packages_available_returns_false_when_pearl_mining_missing, test_pearl_packages_available_returns_true_when_all_present, test_install_hint_is_actionable, _module_available |
| `docs/design/2026-05-05-pearl-coordination-discussion-draft.md` | documentation | ✓ | agent, api, code, email | - | - |
| `docs/design/2026-05-05-vllm-pearl-mining-integration-design.md` | documentation | ✓ | agent, api, auth, code | - | Defines: stays, shipped, ensure_registered, MiningCapabilities |
| `docs/design/2026-05-05-vllm-pearl-mining-integration-plan.md` | documentation | ✓ | agent, api, auth, code | - | Defines: invariants, test_miner_registry_register_and_get, _Stub, MinerRegistry |
| `docs/development/contributing.md` | documentation | ✓ | agent, anthropic, api, bus | - | Defines: MyEngine, ensure_registered, Conventions, BenchmarkResult |
| `docs/development/mining-nvidia-validation.md` | documentation | ✓ | docker, engine, git, gpu | - | - |
| `docs/development/mining.md` | documentation | ✓ | agent, code, docker, engine | - | Defines: ensure_registered |

*(Truncated in table preview: 2169 total files indexed in ledger manifest)*

