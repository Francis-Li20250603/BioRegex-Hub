#!/bin/bash
BACKUP_DIR="/opt/bioregex-backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="bioregex_db_$DATE.sql"

docker exec bioregex-db pg_dump -U postgres bioregex > $BACKUP_DIR/$FILENAME
gzip $BACKUP_DIR/$FILENAME

# 保留最近7天备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -exec rm {} \;
