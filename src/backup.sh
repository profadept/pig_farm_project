#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [ -f "$ENV_FILE" ]; then
    echo "🔄 Loading credentials from $ENV_FILE..."
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "❌ ERROR: .env file not found at $ENV_FILE!"
    exit 1
fi

DB_USER=${DB_USER:-postgres}
DB_NAME=${DB_NAME:-pig_farm_db}
DB_PASS=${DB_PASSWORD:-}

CONTAINER=$(docker ps --format '{{.Names}}' | grep -iE 'postgres|db' | head -n 1)

if [ -z "$CONTAINER" ]; then
    echo "❌ ERROR: No database container found running."
    exit 1
fi
echo "✅ Found database container: $CONTAINER"


if ! docker exec -e PGPASSWORD="$DB_PASS" $CONTAINER psql -U $DB_USER -d $DB_NAME -c "\l" > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect! Please check your .env file."
    echo "👉 The script is trying to login as: $DB_USER"
    exit 1
fi


echo "------------------------------------------------"
read -p "❓ Do you want to backup '$DB_NAME' now? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "🚫 Backup cancelled."
    exit 0
fi

echo ""
echo "📁 Where should we save the backup file?"
echo "  1) Inside this project (creates a 'backups' folder)"
echo "  2) Your computer's Downloads folder (~/Downloads)"
read -p "👉 Choose 1 or 2 (default is 1): " location

if [ "$location" == "2" ]; then
    BACKUP_DIR=~/Downloads
else
    BACKUP_DIR="$SCRIPT_DIR/../backups"
    mkdir -p "$BACKUP_DIR"
fi


TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="farmos_backup_$TIMESTAMP.sql"
FILEPATH="$BACKUP_DIR/$FILENAME"

echo ""
echo "⏳ Exporting database to $FILEPATH..."


if docker exec -e PGPASSWORD="$DB_PASS" $CONTAINER pg_dump -U $DB_USER -d $DB_NAME > "$FILEPATH"; then
    echo "🎉 Backup complete and safely stored at: $FILEPATH"
else
    echo "❌ ERROR: Backup failed! Deleting broken file..."
    rm "$FILEPATH"
    exit 1
fi