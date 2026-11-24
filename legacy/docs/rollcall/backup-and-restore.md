# Rollcall backup and restore

The nightly backup runs on the Rollcall host. It saves a PostgreSQL custom-format dump, the original PDFs referenced by that dump, and a SHA-256 manifest in one dated directory. The database dump and document list share one PostgreSQL snapshot. Rollcall stores originals under immutable content hashes, so ordinary uploads and corrections can continue during a backup. Serialize backups with migrations and any archive maintenance that can move or delete originals.

## Nightly backup

Provision a separate encrypted backup volume or an approved encrypted backup share. Limit access to the backup identity and recovery administrators. Keep the data destination and recovery keys separate from the Rollcall host. Use the installed PostgreSQL tools for the server major version. Give the scheduled identity read access to the application database and archive and write access to the backup destination. Set `ROLLCALL_BACKUP_DATABASE` for that identity using a password-free connection string and a protected PostgreSQL password file.

From the workspace root, run the following with the deployment paths:

```powershell
backend/.venv/Scripts/python.exe backend/backup_rollcall.py --postgres-bin 'C:/Program Files/PostgreSQL/18/bin' backup --archive '<live PDF archive>' --destination '<separate encrypted destination>'
```

Schedule the same command in Windows Task Scheduler after closing. Run under the dedicated backup identity, allow only one active instance, and configure the shop's monitoring to alert the backup owner if the task exits nonzero or a successful backup is older than 26 hours. The command exits nonzero on failed validation, inaccessible storage or a failed database dump. It publishes a dated directory only after the dump and PDF checksums are written. An interrupted process may leave a directory prefixed `.rollcall-incomplete-`.

The pilot proposal is to retain 14 nightly sets and four weekly sets. Confirm the retention period with the shop before deleting any backups. Once a week, copy a complete dated directory to the encrypted off-site drive. Verify the copy from the drive and disconnect it. Rotate two drives so an off-site copy remains available during the exchange.

```powershell
backend/.venv/Scripts/python.exe backend/backup_rollcall.py verify --bundle '<copied dated backup directory>'
```

Keep the Rollcall release, database role provisioning instructions and deployment settings with the recovery documentation. Store passwords and certificate keys in the approved secret store. The logical backup restores application data, including corrections, history and original PDFs. Provision database roles and access grants for the recovery installation separately.

## Restore rehearsal

Use a trusted backup set and a separate PostgreSQL test instance. Set `ROLLCALL_RESTORE_MAINTENANCE_DATABASE` to its maintenance database using a recovery identity allowed to create a database. Choose a new database name and a new PDF archive path on protected storage.

```powershell
backend/.venv/Scripts/python.exe backend/backup_rollcall.py --postgres-bin 'C:/Program Files/PostgreSQL/18/bin' restore --bundle '<dated backup directory>' --new-database rollcall_rehearsal --archive '<new restored PDF archive>'
```

The restore verifies the dump and original PDFs before creating the database, refuses an existing database or archive path, and compares restored document references against the manifest before publishing the archive. If a restore fails after creating the database, retain it for diagnosis and choose a fresh database name for the retry. Use an approved recovery account to remove the failed rehearsal database when diagnosis is complete.

Point a separate Rollcall instance at the restored database and archive. Compare record counts, reopen a saved correction and its original PDF, and record the time from starting the restore to passing the smoke check. Repeat on the shop recovery host before customer data enters the pilot. A successful nightly cadence targets a recovery point within 24 hours.

## Development verification

The disposable PostgreSQL 18.6 run passed all 25 backend tests. The backup integration test verified the bundle, rejected a corrupted PDF, restored a saved correction and its history, reopened the original byte for byte, and refused to overwrite an existing database. The synthetic test took 2.11 seconds, including setup of the sample data, backup and restore checks. Production recovery time still needs measurement on the shop hardware. [Isolated verifier evidence](../../output/isolated-postgres/run-26fc7f12c0f1/evidence.json)
