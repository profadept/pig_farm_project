#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
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

if ! docker exec -e PGPASSWORD="$DB_PASS" $CONTAINER psql -U $DB_USER -d $DB_NAME -c "\l" > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect! Please check your .env file."
    exit 1
fi

BACKUP_DIR="/srv/backups/pigfarm"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="farmos_backup_$TIMESTAMP.sql"
FILEPATH="$BACKUP_DIR/$FILENAME"

if docker exec -e PGPASSWORD="$DB_PASS" $CONTAINER pg_dump -U $DB_USER -d $DB_NAME > "$FILEPATH"; then
    echo "✅ Backup complete: $FILEPATH"
else
    echo "❌ Backup failed, removing broken file"
    rm "$FILEPATH"
    exit 1
fi

# Keep only the last 14 days of backups
find "$BACKUP_DIR" -name "farmos_backup_*.sql" -mtime +14 -delete
