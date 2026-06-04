#!/usr/bin/env bash
#
# Ruflo Integration Script for Claude Skills Library
#
# Registers Ruflo as MCP server and installs cs-* agents so they are
# available as Ruflo swarm agents within Claude Code.
#
# Usage:
#   ./scripts/ruflo-install.sh [--dry-run] [--mcp-only] [--agents-only]
#
# Options:
#   --mcp-only     Only register Ruflo as MCP server, skip agent install
#   --agents-only  Only install cs-* agents, skip MCP registration
#   --dry-run      Show what would be done without making changes
#   --help         Show this help message
#
# Examples:
#   ./scripts/ruflo-install.sh                 # Full integration
#   ./scripts/ruflo-install.sh --dry-run       # Preview only
#   ./scripts/ruflo-install.sh --mcp-only      # MCP server only
#

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUFLO_AGENTS_DIR="${RUFLO_AGENTS_DIR:-$HOME/.ruflo/agents}"
DRY_RUN=false
MCP_ONLY=false
AGENTS_ONLY=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[OK]${NC}   $1"; }
print_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error()   { echo -e "${RED}[FAIL]${NC} $1"; }

show_help() {
  head -30 "$0" | tail -25
  exit 0
}

for arg in "$@"; do
  case $arg in
    --dry-run)     DRY_RUN=true ;;
    --mcp-only)    MCP_ONLY=true ;;
    --agents-only) AGENTS_ONLY=true ;;
    --help|-h)     show_help ;;
    *)
      print_error "Unknown option: $arg"
      show_help
      ;;
  esac
done

echo ""
echo "========================================"
echo "  Claude Skills × Ruflo Integration"
echo "========================================"
echo ""

check_prerequisites() {
  if ! command -v node &>/dev/null; then
    print_error "Node.js not found. Install from https://nodejs.org/ and re-run."
    exit 1
  fi
  print_info "Node.js $(node --version) detected"

  if ! command -v claude &>/dev/null; then
    print_warn "'claude' CLI not in PATH — MCP registration requires Claude Code CLI."
    print_warn "Install: https://claude.ai/code"
  fi
}

register_ruflo_mcp() {
  echo ""
  print_info "Registering Ruflo as MCP server in Claude Code..."

  local cmd="claude mcp add ruflo -- npx ruflo@latest mcp start"

  if $DRY_RUN; then
    print_info "[dry-run] would run: $cmd"
    return 0
  fi

  if ! command -v claude &>/dev/null; then
    print_warn "Skipping MCP registration (claude CLI not found)."
    print_warn "Run manually after installing Claude Code:"
    echo "    $cmd"
    return 0
  fi

  if $cmd 2>/dev/null; then
    print_success "Ruflo MCP registered"
  else
    print_warn "MCP registration returned non-zero. Ruflo may already be registered."
    print_warn "To verify: claude mcp list | grep ruflo"
    print_warn "To register manually: $cmd"
  fi
}

install_agents() {
  echo ""
  print_info "Installing cs-* agents to ${RUFLO_AGENTS_DIR} ..."

  local installed=0
  local skipped=0

  while IFS= read -r agent_file; do
    local agent_name
    agent_name="$(basename "$agent_file" .md)"
    local target="${RUFLO_AGENTS_DIR}/${agent_name}.md"

    if [[ -f "$target" ]]; then
      skipped=$((skipped + 1))
      continue
    fi

    if $DRY_RUN; then
      print_info "[dry-run] would install: $agent_name → $target"
    else
      mkdir -p "$RUFLO_AGENTS_DIR"
      cp "$agent_file" "$target"
      print_success "installed: $agent_name"
    fi
    installed=$((installed + 1))
  done < <(find "$REPO_DIR/agents" -name "cs-*.md" 2>/dev/null | sort)

  echo ""
  if $DRY_RUN; then
    print_info "Dry run complete. Would install $installed agent(s). ($skipped already exist)"
  else
    print_info "Done. Installed $installed agent(s). ($skipped already existed)"
    if [[ $installed -gt 0 ]]; then
      print_info "Location: $RUFLO_AGENTS_DIR"
    fi
  fi
}

list_available_agents() {
  echo ""
  print_info "Available cs-* agents in this repository:"
  find "$REPO_DIR/agents" -name "cs-*.md" 2>/dev/null | sort | \
    while IFS= read -r f; do
      local name
      name="$(basename "$f" .md)"
      local desc
      desc="$(grep -m1 '^description:' "$f" 2>/dev/null | sed 's/description:[[:space:]]*//' | head -c 80 || echo '—')"
      printf "  %-30s %s\n" "$name" "$desc"
    done
}

check_prerequisites

if ! $AGENTS_ONLY; then
  register_ruflo_mcp
fi

if ! $MCP_ONLY; then
  install_agents
fi

list_available_agents

echo ""
echo "========================================"
echo "  Integration complete"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to activate the Ruflo MCP server"
echo "  2. Use Ruflo slash commands to launch multi-agent workflows:"
echo "       /spawn cs-orchestrator"
echo "       /swarm 'Plan and execute our Q3 marketing campaign'"
echo "  3. Skills are available in Ruflo via the .claude-plugin/marketplace.json"
echo ""
echo "Resources:"
echo "  Ruflo docs:      https://github.com/ruvnet/ruflo"
echo "  Skills library:  https://github.com/googox/claude-skills"
echo ""
