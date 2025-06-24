# Backup Directory

This directory is for storing database backups and data exports.

## Volume Backup Commands

```bash
# Export database volume to backup
docker run --rm -v crowd-due-dill_database_v1:/data -v $(pwd)/backups:/backup alpine tar czf /backup/database_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Export logs volume to backup  
docker run --rm -v crowd-due-dill_logs_v1:/data -v $(pwd)/backups:/backup alpine tar czf /backup/logs_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore database from backup (example)
# docker run --rm -v crowd-due-dill_database_v1:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/database_20240620_123456.tar.gz -C /data
```

## Document Export Commands

```bash
# Export documents using document manager
docker exec crowd-due-dill-backend python3 tools/document_manager.py export backups/documents_$(date +%Y%m%d).json
``` 