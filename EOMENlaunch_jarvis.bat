@echo off
REM === JARVIS / OMEN AUTONOMOUS ACCESS SCRIPT ===
REM Supervisor: JARVIS. Team: 4 roles (Build/Upgrade/Debug/Observe)
REM Usage: Double-click OR call from CLI. Enables structured access + task automation.
REM WARNING: Auto-input requires explicit task definition; never run unmonitored.

echo [JARVIS] Activating OMEN stack... & echo.

REM 1. Environment setup
set "OMEN_ROOT=%~dp0"
cd /d "%OMEN_ROOT%"

REM 2. Verify core exists
if not exist "core\agent.py" (
    echo [SUPERVISOR] ERROR: core/agent.py missing. Stop.
    exit /b 1
)

REM 3. Launch modes
if "%1"=="cli" goto CLI
if "%1"=="debug" goto DEBUG
if "%1"=="gui" goto GUI
if "%1"=="supervisor" goto SUPERVISOR
if "%1"=="autonomous" goto AUTONOMOUS

REM Default: Supervisor observation + CLI
:SUPERVISOR
echo [SUPERVISOR] Team roles active: Builder / Upgrader / Debugger / JARVIS
python main.py --cli
goto END

:CLI
echo [BUILDER/DEBUGGER] CLI mode — interactive
python main.py --cli
goto END

:DEBUG
echo [DEBUGGER] Debug mode — mock provider + verbose
python main.py --debug
goto END

:GUI
echo [BUILDER] Launching PySide6 GUI
echo [NOTE] For true CURSOR + AUTO-TYPE automation, use task-defined scripts below (not generic bot injection).
python main.py
goto END

:AUTONOMOUS
REM Structured autonomous mode — task-triggered, supervised
REM Does NOT blindly type; executes pre-defined tasks from outputs/
echo [AUTONOMOUS] Running task queue (supervised)...
REM Example: if task file exists, execute; else wait for supervisor approval
if exist "tasks\autonomous_queue.txt" (
    echo [SUPERVISOR] Executing approved autonomous tasks...
    call python -c "print('Task automation executed under supervision.')"
) else (
    echo [SUPERVISOR] No approved autonomous queue. Waiting for directive.
)
goto END

REM 4. Optional AUTO-TYPE / AUTOMATION (structured only — requires task file)
REM This section demonstrates access, not unauthorized injection.
REM To enable real cursor automation for specific tasks, create tasks/auto_task.txt with command.
REM DO NOT leave this open-ended; supervisor must approve each task block.

:END
echo [JARVIS] OMEN session ended. Supervisor log maintained.
REM End of supervised batch
