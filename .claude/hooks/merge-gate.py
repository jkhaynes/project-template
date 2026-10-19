#!/usr/bin/env python3
"""Local merge gate: a PreToolUse hook on Bash that stands in for branch protection.

Private repos on the free GitHub plan can't enforce branch protection, so this hook
blocks Claude Code from merging on red:

- `gh pr merge`: allowed only when `gh pr checks` is all green. Pending, failing or
  missing checks block. Set MERGE_GATE_ALLOW_NO_CHECKS=1 for a repo without CI.
- `git push` to main or master: blocked. Go through a PR.
- `git merge` while on main or master: allowed only if scripts/check passes.

Anything else exits 0 straight away. Exit 2 blocks the command and shows stderr to
Claude. A merge is never allowed by accident: if the gate can't tell, it blocks.
"""
import json
import os
import re
import shlex
import shutil
import subprocess
import sys

PROTECTED = {"main", "master"}
SEPARATORS = re.compile(r"&&|\|\||[;|\n]")
GH_MERGE_VALUE_FLAGS = {"-b", "--body", "-F", "--body-file", "-t", "--subject",
                        "-A", "--author-email", "--match-head-commit", "-R", "--repo"}
GIT_PUSH_VALUE_FLAGS = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
GIT_GLOBAL_VALUE_FLAGS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


class Block(Exception):
    pass


def tokens_of(segment):
    try:
        toks = shlex.split(segment, posix=True)
    except ValueError:
        toks = segment.split()
    # Drop leading VAR=value assignments.
    while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
        toks.pop(0)
    return toks


def prog(tok):
    name = os.path.basename(tok).lower()
    return name[:-4] if name.endswith(".exe") else name


def git_subcommand(toks):
    """Return (subcommand, args, global_opts) for a git command, or (None, [], [])."""
    i, global_opts = 1, []
    while i < len(toks) and toks[i].startswith("-"):
        if toks[i] in GIT_GLOBAL_VALUE_FLAGS and i + 1 < len(toks):
            global_opts += toks[i:i + 2]
            i += 2
        else:
            global_opts.append(toks[i])
            i += 1
    if i >= len(toks):
        return None, [], []
    return toks[i], toks[i + 1:], global_opts


def run(args, cwd, timeout=120):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def current_branch(cwd, global_opts):
    git = shutil.which("git")
    if not git:
        raise Block("git not found on PATH, so the merge gate can't tell which branch you're on.")
    r = run([git, *global_opts, "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if r.returncode != 0:
        raise Block("couldn't read the current branch: " + r.stderr.strip())
    return r.stdout.strip()


def check_gh_merge(args, cwd):
    selector, repo, i = None, [], 0
    while i < len(args):
        a = args[i]
        if a in GH_MERGE_VALUE_FLAGS:
            if a in ("-R", "--repo") and i + 1 < len(args):
                repo = ["--repo", args[i + 1]]
            i += 2
            continue
        if a.startswith("--repo="):
            repo = ["--repo", a.split("=", 1)[1]]
        elif not a.startswith("-") and selector is None:
            selector = a
        i += 1

    gh = shutil.which("gh")
    if not gh:
        raise Block("the GitHub CLI (gh) isn't installed or isn't on PATH, so CI status can't be "
                    "checked. Install gh and run `gh auth login`, then try again.")
    auth = run([gh, "auth", "status"], cwd, timeout=30)
    if auth.returncode != 0:
        raise Block("gh isn't authenticated, so CI status can't be checked. Run `gh auth login`.")

    target = [selector] if selector else []
    r = run([gh, "pr", "checks", *target, *repo], cwd)
    out = (r.stdout + "\n" + r.stderr).strip()
    if r.returncode == 0:
        return
    if "no checks reported" in out.lower():
        if os.environ.get("MERGE_GATE_ALLOW_NO_CHECKS") == "1":
            return
        raise Block("no CI checks reported for this PR; is .github/workflows/ci.yml set up? "
                    "For a repo with no CI, set MERGE_GATE_ALLOW_NO_CHECKS=1.")
    not_green = []
    for line in r.stdout.splitlines():
        cols = line.split("\t")
        if len(cols) >= 2 and cols[1].strip().lower() not in ("pass", "skipping"):
            not_green.append(f"  {cols[0].strip()}: {cols[1].strip()}")
    state = "still pending" if r.returncode == 8 else "not green"
    detail = "\n".join(not_green) if not_green else "  " + (out or f"gh exited {r.returncode}")
    pr = f"PR {selector}" if selector else "this branch's PR"
    watch = " ".join(["gh pr checks", *target, "--watch"])
    raise Block(f"CI checks for {pr} are {state}:\n{detail}\n"
                f"Wait with `{watch}`, fix any failure, then merge.")


def check_git_push(args, cwd, global_opts):
    positional, i, flags = [], 0, set()
    while i < len(args):
        a = args[i]
        if a in GIT_PUSH_VALUE_FLAGS:
            i += 2
            continue
        if a.startswith("-"):
            flags.add(a.split("=", 1)[0])
        else:
            positional.append(a)
        i += 1
    if flags & {"--all", "--mirror", "--branches"}:
        raise Block("`git push --all/--mirror` would push main or master. Go through a PR.")
    refspecs = positional[1:]
    if not refspecs:
        if "--tags" in flags:
            return
        branch = current_branch(cwd, global_opts)
        if branch in PROTECTED:
            raise Block(f"you're on {branch}; pushing it directly skips CI review. Go through a PR.")
        return
    for spec in refspecs:
        dst = spec.split(":", 1)[1] if ":" in spec else spec
        dst = dst.lstrip("+")
        if dst.startswith("refs/heads/"):
            dst = dst[len("refs/heads/"):]
        if dst == "HEAD":
            dst = current_branch(cwd, global_opts)
        if dst in PROTECTED:
            raise Block(f"pushing to {dst} directly skips CI review. Go through a PR.")


def check_git_merge(args, cwd, global_opts):
    if any(a in ("--abort", "--continue", "--quit") for a in args):
        return
    branch = current_branch(cwd, global_opts)
    if branch not in PROTECTED:
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    bash, pwsh = shutil.which("bash"), shutil.which("pwsh") or shutil.which("powershell")
    if bash and os.path.exists(os.path.join(root, "scripts", "check.sh")):
        cmd = [bash, "scripts/check.sh"]
    elif pwsh and os.path.exists(os.path.join(root, "scripts", "check.ps1")):
        cmd = [pwsh, "-NoProfile", "-File", "scripts/check.ps1"]
    else:
        raise Block(f"merging into {branch} needs scripts/check to pass, and it couldn't be run "
                    "(no bash or pwsh, or the script is missing). Go through a PR instead.")
    r = run(cmd, root, timeout=1800)
    if r.returncode != 0:
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-20:])
        raise Block(f"scripts/check failed, so merging into {branch} is blocked:\n{tail}")


def gate(command, cwd):
    for segment in SEPARATORS.split(command):
        toks = tokens_of(segment.strip())
        if len(toks) < 2:
            continue
        p = prog(toks[0])
        if p == "gh" and toks[1:3] == ["pr", "merge"]:
            check_gh_merge(toks[3:], cwd)
        elif p == "git":
            sub, args, global_opts = git_subcommand(toks)
            if sub == "push":
                check_git_push(args, cwd, global_opts)
            elif sub == "merge":
                check_git_merge(args, cwd, global_opts)


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
        command = data.get("tool_input", {}).get("command", "") or ""
        cwd = data.get("cwd") or os.getcwd()
    except Exception:
        # Can't parse the hook input. Block only if it might be a merge or push.
        if re.search(r"\b(merge|push)\b", raw):
            print("merge-gate: couldn't read the hook input, so this merge/push is blocked.",
                  file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    if "merge" not in command and "push" not in command:
        sys.exit(0)
    try:
        gate(command, cwd)
    except Block as e:
        print(f"merge-gate: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # never fail open on a merge
        print(f"merge-gate: blocked because the gate itself failed ({e!r}). "
              "Fix the hook or merge by hand after checking CI.", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
