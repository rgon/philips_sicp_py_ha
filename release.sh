#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$ROOT_DIR/dist"
ARTIFACT_NAME="philips_sicp_display.zip"

# ensure the artifact dir is empty
rm -rf "$ARTIFACT_DIR"
# ensure the artifact dir exists
mkdir -p "$ARTIFACT_DIR"

# Build the custom_components with vendored dependencies
uv build
uv pip install --target $ARTIFACT_DIR custom_components/philips_sicp_display/
uv pip install --target $ARTIFACT_DIR lib/sicppy/

# vendorize sicppy into philips_sicp_display
mv $ARTIFACT_DIR/sicppy $ARTIFACT_DIR/philips_sicp_display
# rm everything except philips_sicp_display from $ARTIFACT_DIR/custom_components
find $ARTIFACT_DIR -mindepth 1 -maxdepth 1 ! -name 'philips_sicp_display' -exec rm -rf {} +

# Import vendorized dependencies relatively.
# For every line in philips_sicp_display, search for "from sicppy" and replace with "from .sicppy"
find "$ARTIFACT_DIR/philips_sicp_display" -type f -name "*.py" -exec sed -i 's/from sicppy/from .sicppy/g' {} +

ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"

( cd "$ARTIFACT_DIR/philips_sicp_display" && zip -r "$ARTIFACT_PATH" . >/dev/null )

echo "Created release artifact at $ARTIFACT_PATH"