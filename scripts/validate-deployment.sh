#!/bin/bash
# Helm Chart Validation Script
# This script validates the Helm chart before deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CHART_DIR="$PROJECT_ROOT/deploy"

echo "======================================"
echo "MCE Cluster Generator - Chart Validation"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "1. Checking prerequisites..."
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm is installed$(helm version --short)${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${YELLOW}⚠ kubectl is not installed (optional for validation)${NC}"
else
    echo -e "${GREEN}✓ kubectl is installed$(kubectl version --client --short 2>/dev/null)${NC}"
fi
echo ""

# Validate chart structure
echo "2. Validating chart structure..."
if [ ! -f "$CHART_DIR/Chart.yaml" ]; then
    echo -e "${RED}✗ Chart.yaml not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Chart.yaml exists${NC}"

if [ ! -f "$CHART_DIR/values.yaml" ]; then
    echo -e "${RED}✗ values.yaml not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ values.yaml exists${NC}"

if [ ! -f "$CHART_DIR/templates/_helpers.tpl" ]; then
    echo -e "${RED}✗ _helpers.tpl not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ _helpers.tpl exists${NC}"

echo -e "${GREEN}✓ Chart structure is valid${NC}"
echo ""

# Lint the chart
echo "3. Linting Helm chart..."
if helm lint "$CHART_DIR" > /tmp/helm-lint.log 2>&1; then
    echo -e "${GREEN}✓ Helm lint passed${NC}"
    cat /tmp/helm-lint.log | grep -E "\[INFO\]|\[WARNING\]" || true
else
    echo -e "${RED}✗ Helm lint failed${NC}"
    cat /tmp/helm-lint.log
    exit 1
fi
echo ""

# Test template rendering
echo "4. Testing template rendering..."
if helm template test-release "$CHART_DIR" > /tmp/helm-template.yaml 2>&1; then
    echo -e "${GREEN}✓ Template rendering successful${NC}"

    # Count resources
    NUM_RESOURCES=$(grep -c "^kind:" /tmp/helm-template.yaml || echo "0")
    echo "  - Generated $NUM_RESOURCES Kubernetes resources"

    # List resource types
    echo "  - Resource types:"
    grep "^kind:" /tmp/helm-template.yaml | sort | uniq -c | sed 's/^/    /'
else
    echo -e "${RED}✗ Template rendering failed${NC}"
    exit 1
fi
echo ""

# Validate with different values files
echo "5. Validating different environments..."

for values_file in "$CHART_DIR"/values*.yaml; do
    env_name=$(basename "$values_file" .yaml | sed 's/values-//')

    if [ "$env_name" = "values" ]; then
        env_name="default"
    fi

    echo "  - Testing $env_name environment..."
    if helm template test-release "$CHART_DIR" -f "$values_file" > /dev/null 2>&1; then
        echo -e "    ${GREEN}✓ $env_name: OK${NC}"
    else
        echo -e "    ${RED}✗ $env_name: FAILED${NC}"
        exit 1
    fi
done
echo ""

# Check for required fields in Chart.yaml
echo "6. Validating Chart.yaml..."
chart_name=$(grep "^name:" "$CHART_DIR/Chart.yaml" | awk '{print $2}')
chart_version=$(grep "^version:" "$CHART_DIR/Chart.yaml" | awk '{print $2}')
app_version=$(grep "^appVersion:" "$CHART_DIR/Chart.yaml" | awk '{print $2}')

echo "  - Chart name: $chart_name"
echo "  - Chart version: $chart_version"
echo "  - App version: $app_version"

if [ -z "$chart_name" ] || [ -z "$chart_version" ] || [ -z "$app_version" ]; then
    echo -e "${RED}✗ Missing required fields in Chart.yaml${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Chart.yaml is valid${NC}"
echo ""

# Validate values.yaml syntax
echo "7. Validating values.yaml syntax..."
if python3 -c "import yaml; yaml.safe_load(open('$CHART_DIR/values.yaml'))" 2>/dev/null; then
    echo -e "${GREEN}✓ values.yaml syntax is valid${NC}"
else
    echo -e "${RED}✗ values.yaml has syntax errors${NC}"
    exit 1
fi
echo ""

# Check Dockerfile exists (needed for building image)
echo "8. Checking Dockerfile..."
if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
    echo -e "${GREEN}✓ Dockerfile exists${NC}"

    # Extract image tag from Dockerfile
    docker_version=$(grep "^LABEL.*version=" "$PROJECT_ROOT/Dockerfile" | sed 's/.*version="\([^"]*\)".*/\1/')
    if [ "$docker_version" = "$app_version" ]; then
        echo -e "${GREEN}✓ Dockerfile version matches Chart appVersion ($app_version)${NC}"
    else
        echo -e "${YELLOW}⚠ Dockerfile version ($docker_version) differs from Chart appVersion ($app_version)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Dockerfile not found${NC}"
fi
echo ""

# Summary
echo "======================================"
echo "Validation Summary"
echo "======================================"
echo -e "${GREEN}✓ All validation checks passed!${NC}"
echo ""
echo "Chart Details:"
echo "  - Name: $chart_name"
echo "  - Version: $chart_version"
echo "  - App Version: $app_version"
echo ""
echo "Next steps:"
echo "  1. Build and push Docker image:"
echo "     podman build -t docker.io/roi12345/mce-cluster-generator:$app_version ."
echo "     podman push docker.io/roi12345/mce-cluster-generator:$app_version"
echo ""
echo "  2. Install the chart:"
echo "     helm install mce-api ./deploy"
echo ""
echo "  3. Or use specific values:"
echo "     helm install mce-api ./deploy -f ./deploy/values-prod.yaml"
echo ""
echo "======================================"
