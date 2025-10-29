#!/usr/bin/env bash
#
# Script description here
#
# Usage:
#   ./template.sh input.txt
#   ./template.sh --force input.txt
#   ./template.sh --help
#

# Error handling: exit on error, undefined variables, pipe failures
set -Eeuo pipefail

# Trap errors and cleanup
trap cleanup SIGINT SIGTERM ERR EXIT

# Get script directory (for relative paths)
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

# Global variables
VERBOSE=0
FORCE=0
DRY_RUN=0

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

#
# Cleanup function - runs on exit
#
cleanup() {
    trap - SIGINT SIGTERM ERR EXIT
    # Add cleanup code here (remove temp files, etc.)
}

#
# Setup logging
#
setup_colors() {
    if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
        # Terminal supports colors
        return 0
    else
        # No color support
        RED=''
        GREEN=''
        YELLOW=''
        NC=''
    fi
}

#
# Print message to stderr
#
msg() {
    echo >&2 -e "${1-}"
}

#
# Print error message and exit
# Args:
#   $1 - error message
#   $2 - exit code (default: 1)
#
die() {
    local msg=$1
    local code=${2-1}
    msg "${RED}Error: $msg${NC}"
    exit "$code"
}

#
# Print usage information
#
usage() {
    cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [OPTIONS] INPUT

Script description here.

OPTIONS:
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -f, --force         Force operation without confirmation
    -d, --dry-run       Show what would be done without doing it
    -o, --output FILE   Output file path

EXAMPLES:
    $(basename "${BASH_SOURCE[0]}") input.txt
    $(basename "${BASH_SOURCE[0]}") -v -o output.txt input.txt
    $(basename "${BASH_SOURCE[0]}") --force --dry-run input.txt

EOF
    exit 0
}

#
# Parse command line arguments
#
parse_params() {
    local input=''
    local output=''

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h | --help)
                usage
                ;;
            -v | --verbose)
                VERBOSE=1
                shift
                ;;
            -f | --force)
                FORCE=1
                shift
                ;;
            -d | --dry-run)
                DRY_RUN=1
                shift
                ;;
            -o | --output)
                output="$2"
                shift 2
                ;;
            -*)
                die "Unknown option: $1"
                ;;
            *)
                input="$1"
                shift
                ;;
        esac
    done

    # Validate required arguments
    [[ -z "${input}" ]] && die "Missing required argument: INPUT"

    # Export for use in functions
    export INPUT_FILE="$input"
    export OUTPUT_FILE="${output:-output.txt}"

    return 0
}

#
# Check required commands exist
#
check_requirements() {
    local missing=()

    for cmd in curl jq; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        die "Missing required commands: ${missing[*]}\nInstall them and try again."
    fi
}

#
# Verify file exists and is readable
# Args:
#   $1 - file path
# Returns:
#   0 if file valid, 1 otherwise
#
verify_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        msg "${RED}✗${NC} File not found: $file"
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        msg "${RED}✗${NC} File not readable: $file"
        return 1
    fi

    msg "${GREEN}✓${NC} File verified: $file"
    return 0
}

#
# Process a single file
# Args:
#   $1 - input file path
#   $2 - output file path
# Returns:
#   0 on success, 1 on error
#
process_file() {
    local input="$1"
    local output="$2"

    [[ $VERBOSE -eq 1 ]] && msg "Processing: $input → $output"

    if [[ ! -f "$input" ]]; then
        msg "${RED}Error: Input file not found: $input${NC}"
        return 1
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
        msg "${YELLOW}[DRY RUN]${NC} Would process: $input"
        return 0
    fi

    # Actual processing here
    grep -v '^#' "$input" > "$output" || {
        msg "${RED}Error: Processing failed${NC}"
        return 1
    }

    msg "${GREEN}✓${NC} Processed: $output"
    return 0
}

#
# Ask for confirmation
# Returns:
#   0 if confirmed, 1 if declined
#
confirm() {
    if [[ $FORCE -eq 1 ]]; then
        return 0
    fi

    read -r -p "Continue? [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

#
# Main function
#
main() {
    # Setup
    setup_colors
    parse_params "$@"

    # Check requirements
    check_requirements

    # Show configuration
    if [[ $VERBOSE -eq 1 ]]; then
        msg "Configuration:"
        msg "  Input:   $INPUT_FILE"
        msg "  Output:  $OUTPUT_FILE"
        msg "  Verbose: $VERBOSE"
        msg "  Force:   $FORCE"
        msg "  Dry run: $DRY_RUN"
        msg ""
    fi

    # Verify input file
    verify_file "$INPUT_FILE" || die "Input file verification failed"

    # Ask for confirmation
    msg "About to process: $INPUT_FILE"
    if ! confirm; then
        msg "${YELLOW}Operation cancelled${NC}"
        exit 0
    fi

    # Process file
    if process_file "$INPUT_FILE" "$OUTPUT_FILE"; then
        msg "${GREEN}✓${NC} Operation completed successfully"
        exit 0
    else
        die "Operation failed"
    fi
}

# Run main function
main "$@"
