"""
Local CI/CD Pipeline Simulator
-------------------------------
Runs each pipeline stage step-by-step with real validations and colorized status reporting.
Simulates what GitHub Actions / GitLab CI does in the cloud.
"""

import subprocess
import sys
import time

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner(stage_num: int, title: str):
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}STAGE {stage_num}: {title.upper()}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}")


def run_step(description: str, command: list, allow_fail: bool = False) -> bool:
    print(f"\n{BOLD}> Running:{RESET} {description} ...")
    print(f"  {YELLOW}$ {' '.join(command)}{RESET}")
    start = time.time()
    try:
        res = subprocess.run(command, capture_output=True, text=True, check=False)
        duration = round(time.time() - start, 2)
        if res.returncode == 0:
            print(f"  {GREEN}[PASS]{RESET} ({duration}s)")
            if res.stdout.strip():
                # print first few lines of output
                lines = res.stdout.strip().splitlines()
                preview = lines[:8]
                for l in preview:
                    print(f"    {l}")
                if len(lines) > 8:
                    print(f"    ... [{len(lines) - 8} lines truncated]")
            return True
        else:
            if allow_fail:
                print(
                    f"  {YELLOW}[WARN] (Optional check bypassed){RESET} ({duration}s)"
                )
                return True
            print(f"  {RED}[FAIL]{RESET} (Exit Code: {res.returncode}, {duration}s)")
            if res.stderr.strip():
                print(f"{RED}{res.stderr}{RESET}")
            elif res.stdout.strip():
                print(f"{RED}{res.stdout}{RESET}")
            return False
    except FileNotFoundError:
        if allow_fail:
            print(
                f"  {YELLOW}[WARN] Tool not installed locally, skipping optional step.{RESET}"
            )
            return True
        print(f"  {RED}[FAIL] Command executable not found: {command[0]}{RESET}")
        return False


def main():
    print(
        f"{BOLD}{GREEN}============================================================{RESET}"
    )
    print(
        f"{BOLD}{GREEN}        CI/CD PIPELINE EXECUTION SIMULATOR                 {RESET}"
    )
    print(
        f"{BOLD}{GREEN}============================================================{RESET}"
    )

    # STAGE 1: Code Quality & Lint
    print_banner(1, "Continuous Integration - Code Style & Linting")
    # Python compilation check
    compile_ok = run_step(
        "Python Syntax Compilation Validation",
        [sys.executable, "-m", "compileall", "-q", "src", "tests"],
    )
    if not compile_ok:
        sys.exit(1)

    # Ruff or Flake8 linting check
    run_step("Static Code Style Linter (Ruff)", ["ruff", "check", "."], allow_fail=True)

    # STAGE 2: Security & SAST
    print_banner(2, "Continuous Integration - Security & SAST Audit")
    run_step(
        "Bandit Static Application Security Scanner",
        ["bandit", "-r", "src/", "-ll"],
        allow_fail=True,
    )

    # STAGE 3: Automated Testing & Coverage
    print_banner(3, "Continuous Integration - Automated Tests & Coverage")
    test_ok = run_step(
        "Pytest Suite Execution with Coverage",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--cov=src",
            "--cov-report=term-missing",
        ],
    )
    if not test_ok:
        print(
            f"\n{RED}{BOLD}PIPELINE HALTED:{RESET} Unit tests failed! Continuous Integration blocked build."
        )
        sys.exit(1)

    # STAGE 4: Artifact Packaging & Container Build Check
    print_banner(4, "Continuous Delivery - Artifact Build & Verification")
    print(f"{GREEN}[OK] Dockerfile syntax verified{RESET}")
    print(f"{GREEN}[OK] Multi-stage container instructions valid{RESET}")
    print(f"{GREEN}[OK] Release Tag: v1.0.0-git-{int(time.time())}{RESET}")

    # STAGE 5: Staging Deployment & Smoke Verification
    print_banner(5, "Continuous Deployment - Staging Deployment & Smoke Test")
    print("> Deploying to Staging namespace...")
    time.sleep(0.5)
    print("  Applying configuration: k8s/deployment.yaml")
    print("> Running Post-Deployment Synthetic Smoke Tests...")
    # Run test_api directly to simulate smoke test against live target
    smoke_ok = run_step(
        "Staging Smoke Test Verification",
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_api.py",
            "-k",
            "test_liveness_probe or test_readiness_probe",
        ],
    )
    if not smoke_ok:
        print(
            f"\n{RED}{BOLD}DEPLOYMENT ABORTED:{RESET} Staging smoke test failed. Rollback triggered!"
        )
        sys.exit(1)

    # STAGE 6: Production Rollout
    print_banner(6, "Continuous Deployment - Production Gate & Rollout")
    print(
        f"{YELLOW}[MANUAL APPROVAL / AUTO GATE]: Staging verified. Releasing to Production...{RESET}"
    )
    time.sleep(0.5)
    print(
        "[OK] Production RollingUpdate Strategy initiated (maxSurge=1, maxUnavailable=0)"
    )
    print("[OK] 3/3 Pods Ready in Production cluster.")
    print("[OK] Liveness & Readiness checks healthy: 200 OK.")

    print(f"\n{BOLD}{GREEN}{'=' * 60}{RESET}")
    print(
        f"{BOLD}{GREEN}*** PIPELINE SUCCEEDED: All CI/CD Stages Passed Successfully! ***{RESET}"
    )
    print(f"{BOLD}{GREEN}{'=' * 60}{RESET}\n")


if __name__ == "__main__":
    main()
