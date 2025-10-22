#!/bin/bash
# Simple Artifact Creator with Template Selection
# Creates new artifacts from existing templates or artifacts

set -e

ARTIFACTS_DIR="$HOME/Desktop/Artifacts"
TEMPLATES_DIR="$(cd "$(dirname "$0")/.." && pwd)/templates/html"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                    🎨 Simple Artifact Creator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to list available templates
list_templates() {
    echo -e "${GREEN}📦 Available Templates:${NC}"
    echo ""

    echo -e "${YELLOW}FROM PLUGIN:${NC}"
    local i=1

    # Base template
    echo -e "  ${i}. base-template.html          ${BLUE}[Foundation - 707 lines]${NC}"
    i=$((i+1))

    # Example templates
    for template in "$TEMPLATES_DIR"/examples/*.html; do
        if [ -f "$template" ]; then
            local basename=$(basename "$template")
            local size=$(wc -l < "$template" | tr -d ' ')
            echo -e "  ${i}. $(basename "$template")  ${BLUE}[${size} lines]${NC}"
            i=$((i+1))
        fi
    done

    echo ""
    echo -e "${YELLOW}FROM YOUR ARTIFACTS:${NC}"

    # Existing artifacts
    if [ -d "$ARTIFACTS_DIR" ]; then
        for artifact in "$ARTIFACTS_DIR"/*.html; do
            if [ -f "$artifact" ]; then
                local basename=$(basename "$artifact")
                local size=$(wc -l < "$artifact" | tr -d ' ')
                echo -e "  ${i}. $basename  ${BLUE}[${size} lines]${NC}"
                i=$((i+1))
            fi
        done

        # Bundled artifacts from React projects
        for dir in "$ARTIFACTS_DIR"/*/; do
            if [ -d "$dir" ] && [ -f "${dir}bundle.html" ]; then
                local dirname=$(basename "$dir")
                local size=$(wc -l < "${dir}bundle.html" | tr -d ' ')
                echo -e "  ${i}. ${dirname}/bundle.html  ${BLUE}[${size} lines]${NC}"
                i=$((i+1))
            fi
        done
    fi

    echo ""
}

# Function to get template path by number
get_template_path() {
    local num=$1
    local i=1

    # Base template
    if [ "$i" -eq "$num" ]; then
        echo "$TEMPLATES_DIR/base-template.html"
        return
    fi
    i=$((i+1))

    # Example templates
    for template in "$TEMPLATES_DIR"/examples/*.html; do
        if [ -f "$template" ] && [ "$i" -eq "$num" ]; then
            echo "$template"
            return
        fi
        i=$((i+1))
    done

    # Existing artifacts
    if [ -d "$ARTIFACTS_DIR" ]; then
        for artifact in "$ARTIFACTS_DIR"/*.html; do
            if [ -f "$artifact" ] && [ "$i" -eq "$num" ]; then
                echo "$artifact"
                return
            fi
            i=$((i+1))
        done

        # Bundled artifacts
        for dir in "$ARTIFACTS_DIR"/*/; do
            if [ -d "$dir" ] && [ -f "${dir}bundle.html" ] && [ "$i" -eq "$num" ]; then
                echo "${dir}bundle.html"
                return
            fi
            i=$((i+1))
        done
    fi

    echo ""
}

# Main flow
main() {
    # Create Artifacts directory if it doesn't exist
    mkdir -p "$ARTIFACTS_DIR"

    # List available templates
    list_templates

    # Get user selection
    echo -e "${GREEN}Select a template (number):${NC} "
    read -r template_num

    template_path=$(get_template_path "$template_num")

    if [ -z "$template_path" ] || [ ! -f "$template_path" ]; then
        echo -e "${RED}❌ Invalid selection${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Selected:${NC} $(basename "$template_path")"
    echo ""

    # Get artifact name
    echo -e "${GREEN}Enter new artifact name (without .html):${NC} "
    read -r artifact_name

    if [ -z "$artifact_name" ]; then
        echo -e "${RED}❌ Artifact name required${NC}"
        exit 1
    fi

    # Add .html if not present
    if [[ ! "$artifact_name" =~ \.html$ ]]; then
        artifact_name="${artifact_name}.html"
    fi

    output_path="$ARTIFACTS_DIR/$artifact_name"

    # Check if file exists
    if [ -f "$output_path" ]; then
        echo -e "${YELLOW}⚠️  File already exists. Overwrite? (y/n):${NC} "
        read -r confirm
        if [ "$confirm" != "y" ]; then
            echo -e "${RED}❌ Cancelled${NC}"
            exit 1
        fi
    fi

    # Copy template to new artifact
    cp "$template_path" "$output_path"

    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Artifact created successfully!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📁 Location:${NC} $output_path"
    echo -e "${BLUE}📝 Size:${NC} $(wc -l < "$output_path" | tr -d ' ') lines"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo -e "  1. Edit the artifact: ${BLUE}code \"$output_path\"${NC}"
    echo -e "  2. View in browser: ${BLUE}open \"$output_path\"${NC}"
    echo -e "  3. Modify content, styles, or functionality"
    echo ""

    # Offer to open
    echo -e "${GREEN}Open the artifact now? (y/n):${NC} "
    read -r open_now
    if [ "$open_now" = "y" ]; then
        open "$output_path"
    fi
}

# Run main function
main
