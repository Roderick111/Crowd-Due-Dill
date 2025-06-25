# Backup Directory

This directory is for storing database backups and data exports.

## Latest Backups

### Vector Database Backup - June 25, 2025
- **File**: `database/vector_db_backup_20250625_125727.tar.gz`
- **Size**: 4.4MB
- **Contents**: Complete vector database with 7 EU regulation documents (579 chunks)
- **Features**: Structure-aware chunking, Cross-Encoder reranking, LLM metadata extraction
- **Documents**: Digital Act, Crowdfunding, GDPR, DORA, AML, DORA Amendments, Scoring
- **Status**: Successfully transferred to production Docker volume

## Volume Backup Commands

```bash
# Export database volume to backup
docker run --rm -v crowd-due-dill_database_v1:/data -v $(pwd)/backups:/backup alpine tar czf /backup/database_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Export logs volume to backup  
docker run --rm -v crowd-due-dill_logs_v1:/data -v $(pwd)/backups:/backup alpine tar czf /backup/logs_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore database from backup (example)
# docker run --rm -v crowd-due-dill_database_v1:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/database_20240620_123456.tar.gz -C /data
```

## Local Vector Database Backup Commands

```bash
# Create timestamped backup of local vector database
timestamp=$(date +"%Y%m%d_%H%M%S") && tar -czf "vector_db_backup_${timestamp}.tar.gz" -C data/ .

# Move to backup directory
mv vector_db_backup_*.tar.gz backups/database/

# Verify backup contents
tar -tzf backups/database/vector_db_backup_*.tar.gz | head -10
```

## Document Export Commands

```bash
# Export documents using document manager
docker exec crowd-due-dill-backend python3 tools/document_manager.py export backups/documents_$(date +%Y%m%d).json
``` 