import os
import zipfile

DB_NAME = "welvision_db"
USER = "root"
PASSWORD = "root"
BACKUP_ZIP = "C:/welvision_backups/welvision_db_backup_20251027_213045.zip"

with zipfile.ZipFile(BACKUP_ZIP, "r") as zip_ref:
    zip_ref.extractall("C:/welvision_backups/temp_restore")

sql_file = [f for f in os.listdir("C:/welvision_backups/temp_restore") if f.endswith(".sql")][0]
sql_path = os.path.join("C:/welvision_backups/temp_restore", sql_file)

restore_command = f'mysql -u {USER} -p{PASSWORD} {DB_NAME} < "{sql_path}"'
print(f"🔄 Restoring database '{DB_NAME}' from backup ...")
os.system(restore_command)

print("✅ Database restored successfully.")
