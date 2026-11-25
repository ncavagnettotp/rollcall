# Database migrations

Files named `NNNN_name.sql` (four digits, lowercase name), applied in number order when the app
starts; see `rollcall/migrate.py`. Never edit a migration that has been applied anywhere: add a new
one. Migrations only move forward.
