#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_DIR="$ROOT_DIR/dist"
ARTIFACT_NAME="sicp_homeassistant.zip"

# ensure the artifact dir is empty
rm -rf "$ARTIFACT_DIR"
# ensure the artifact dir exists
mkdir -p "$ARTIFACT_DIR"

# Build the custom_components with vendored dependencies
uv build
uv pip install --target $ARTIFACT_DIR custom_components/sicp_homeassistant/
uv pip install --target $ARTIFACT_DIR lib/sicppy/

# vendorize sicppy into sicp_homeassistant
mv $ARTIFACT_DIR/sicppy $ARTIFACT_DIR/sicp_homeassistant
# rm everything except sicp_homeassistant from $ARTIFACT_DIR/custom_components
find $ARTIFACT_DIR -mindepth 1 -maxdepth 1 ! -name 'sicp_homeassistant' -exec rm -rf {} +

ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"

( cd "$ARTIFACT_DIR/sicp_homeassistant" && zip -r "$ARTIFACT_PATH" . >/dev/null )

echo "Created release artifact at $ARTIFACT_PATH"