#!/bin/bash
#
# Universal Installer for Claude Skills Library
#
# Installs the cs-* production agents (agents/) to the target tool's
# agent directory. Also delegates to the existing per-tool skill
# installers for Codex and OpenClaw.
#
# Usage:
#   ./scripts/install.sh --tool claude-code [--agent <name>] [--dry-run] [--list]
#   ./scripts/install.sh --tool codex [codex-install.sh options]
#   ./scripts/install.sh --tool openclaw [openclaw-install.sh options]
#
# Options (claude-code):
#   --tool claude-code   Install all cs-* agents to ~/.claude/agents/
#   --agent <name>       Install a single agent by name (e.g. cs-ceo-advisor)
#   --dry-run            Show what would be installed without making changes
#   --list               List available agents
#   --help               Show this help message
#
# Examples:
#   ./scripts/install.sh --tool claude-code
#   ./scripts/install.sh --tool claude-code --agent cs-product-manager
#   ./scripts/install.sh --tool claude-code --dry-run
#   ./scripts/install.sh --tool codex --category marketing
#   ./scripts/install.sh --tool openclaw --dry-run
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
AGENTS_SRC_DIR="$REPO_ROOT/agents"
CLAUDE_AGENTS_DIR="${CLAUDE_AGENTS_DIR:-$HOME/.claude/agents}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

show_help() {
    head -25 "$0" | tail -20
    exit 0
}

# Find all cs-* agent markdown files (excludes CLAUDE.md, routing-rules.yaml, .gitkeep)
find_agents() {
    find "$AGENTS_SRC_DIR" -type f -name "cs-*.md" | sort
}

list_agents() {
    print_info "Available agents in $AGENTS_SRC_DIR:"
    echo ""
    while IFS= read -r agent_file; do
        echo "  - $(basename "$agent_file" .md)"
    done < <(find_agents)
    exit 0
}

install_agent_file() {
    local agent_file="$1"
    local dry_run="$2"
    local agent_name
    agent_name="$(basename "$agent_file" .md)"
    local dest="$CLAUDE_AGENTS_DIR/$agent_name.md"

    if [[ "$dry_run" == "true" ]]; then
        print_info "[DRY RUN] Would install: $agent_name -> $dest"
        return 0
    fi

    mkdir -p "$CLAUDE_AGENTS_DIR"

    if [[ -e "$dest" ]]; then
        print_info "Updating existing agent: $agent_name"
    fi

    cp "$agent_file" "$dest"
    print_success "Installed: $agent_name"
}

install_claude_code() {
    local target="$1"
    local dry_run="$2"
    local installed=0
    local failed=0

    print_info "Installing agents to: $CLAUDE_AGENTS_DIR"
    echo ""

    if [[ -n "$target" ]]; then
        local agent_file="$AGENTS_SRC_DIR"
        agent_file=$(find_agents | grep -F "/$target.md" || true)

        if [[ -z "$agent_file" ]]; then
            print_error "Agent not found: $target"
            exit 1
        fi

        if install_agent_file "$agent_file" "$dry_run"; then
            installed=$((installed + 1))
        else
            failed=$((failed + 1))
        fi
    else
        while IFS= read -r agent_file; do
            if install_agent_file "$agent_file" "$dry_run"; then
                installed=$((installed + 1))
            else
                failed=$((failed + 1))
            fi
        done < <(find_agents)
    fi

    echo ""
    print_info "Installation complete: $installed installed, $failed failed"

    if [[ "$dry_run" != "true" && "$installed" -gt 0 ]]; then
        echo ""
        print_success "Agents installed to: $CLAUDE_AGENTS_DIR"
        print_info "Verify with: ls $CLAUDE_AGENTS_DIR"
    fi
}

main() {
    local tool=""
    local target=""
    local dry_run="false"
    local list_requested="false"
    local extra_args=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            --tool)
                tool="$2"
                shift 2
                ;;
            --agent)
                target="$2"
                shift 2
                ;;
            --dry-run)
                dry_run="true"
                extra_args+=("$1")
                shift
                ;;
            --list)
                list_requested="true"
                extra_args+=("$1")
                shift
                ;;
            --help|-h)
                show_help
                ;;
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done

    echo ""
    echo "========================================"
    echo "  Claude Skills - Universal Installer"
    echo "========================================"
    echo ""

    # --list with no --tool (or --tool claude-code) lists this repo's agents.
    # --list with --tool codex/openclaw is passed through to that installer.
    if [[ "$list_requested" == "true" && ( -z "$tool" || "$tool" == "claude-code" ) ]]; then
        list_agents
    fi

    if [[ -z "$tool" ]]; then
        print_error "Missing required --tool <claude-code|codex|openclaw>"
        show_help
    fi

    case "$tool" in
        claude-code)
            if [[ ! -d "$AGENTS_SRC_DIR" ]]; then
                print_error "Agents directory not found: $AGENTS_SRC_DIR"
                exit 1
            fi
            install_claude_code "$target" "$dry_run"
            ;;
        codex)
            exec "$SCRIPT_DIR/codex-install.sh" "${extra_args[@]}"
            ;;
        openclaw)
            exec "$SCRIPT_DIR/openclaw-install.sh" "${extra_args[@]}"
            ;;
        *)
            print_error "Unknown tool: $tool (expected claude-code, codex, or openclaw)"
            exit 1
            ;;
    esac
}

main "$@"
