# platform Specification

## Purpose
How Rollcall starts, is configured, upgrades its database, reports its health, frames its pages,
serves its own assets and handles errors, so every other capability can rely on one stable base.

## Requirements

### Requirement: One-command start
Rollcall SHALL start as an app container plus a PostgreSQL container with a single Docker Compose
command, reachable at the host's own address and from other machines on the local network at the
configured port (default 8080). The app SHALL wait for the database before serving pages.

#### Scenario: Fresh start
- **GIVEN** a machine with Docker and a filled-in `.env` file
- **WHEN** the operator runs `docker compose up -d`
- **THEN** within 60 seconds both containers report healthy and the start page loads in a browser

#### Scenario: Reachable on the shop network
- **GIVEN** the stack is running on a PC whose network address is, for example, `192.168.1.50`
- **WHEN** someone on another PC on the same network opens `http://192.168.1.50:8080`
- **THEN** the start page loads, and `http://localhost:8080` works on the host PC itself

#### Scenario: Database slow to start
- **GIVEN** the database container takes 20 seconds to accept connections
- **WHEN** the stack starts
- **THEN** the app keeps retrying, then starts normally without operator action

### Requirement: Data survives restarts
The database and stored files SHALL live on named persistent volumes, so stopping, removing and
recreating the containers SHALL NOT lose data.

#### Scenario: Recreate containers
- **GIVEN** a running stack with applied migrations
- **WHEN** the operator runs `docker compose down` and then `docker compose up -d`
- **THEN** the same migrations are recorded as applied and none run again

### Requirement: Configuration from the environment
Rollcall SHALL read its settings from environment variables: database connection, secret key, shop
time zone, data directory and log level. It SHALL refuse to start with a message naming the
setting when a required one is missing or invalid, and SHALL never print secret values.

#### Scenario: Missing setting
- **WHEN** the app starts without the database connection setting
- **THEN** it exits with an error naming that setting, and serves nothing

#### Scenario: Weak secret key
- **WHEN** the secret key is shorter than 32 characters
- **THEN** the app refuses to start and says the secret key is too short, without printing it

#### Scenario: Unknown time zone
- **WHEN** the shop time zone is not a valid zone name such as `America/Chicago`
- **THEN** the app refuses to start and names the setting

### Requirement: Versioned database migrations
Rollcall SHALL change its database structure only through numbered migrations kept with the code.
At startup it SHALL apply each pending migration in order, each in its own transaction, and record
it as applied.

#### Scenario: Pending migrations
- **GIVEN** migrations 1 and 2 are applied and migration 3 is new
- **WHEN** the app starts
- **THEN** only migration 3 runs, and it is recorded with the time it was applied

#### Scenario: Failing migration
- **WHEN** a migration fails partway
- **THEN** none of its changes remain, it is not recorded as applied, and the app refuses to start
  with the migration's number in the error

#### Scenario: Several app processes start together
- **GIVEN** two app processes start at the same moment against the same database
- **WHEN** both find migration 3 pending
- **THEN** migration 3 runs exactly once and both processes start

#### Scenario: Database newer than the code
- **GIVEN** the database records a migration the running code does not have
- **WHEN** the app starts
- **THEN** it refuses to start and says the database belongs to a newer version of Rollcall

### Requirement: Health check
Rollcall SHALL answer a health check at `/health` without sign-in. The check SHALL report healthy
only when the database answers, and SHALL never reveal internal details.

#### Scenario: Healthy
- **WHEN** the database is reachable and `/health` is requested
- **THEN** the response is status 200 with body `ok`

#### Scenario: Database down
- **GIVEN** the database container is stopped
- **WHEN** `/health` is requested
- **THEN** the response is status 503 with body `database unavailable`, with no address, user or
  error text

#### Scenario: Database comes back
- **GIVEN** the database was stopped and is started again
- **WHEN** `/health` is requested after it is back
- **THEN** the response is 200 without restarting the app

### Requirement: Shared page frame
Every page SHALL use one frame: the name "Rollcall", navigation, a message area for success and
error messages, and the page content. Navigation SHALL list only pages that exist. The frame SHALL
be usable from a 360-pixel-wide screen up to a desktop monitor.

#### Scenario: Start page in the frame
- **WHEN** a browser opens `/`
- **THEN** the page shows the Rollcall header, the navigation and a line saying Rollcall is running

#### Scenario: No dead links
- **WHEN** any page is rendered
- **THEN** every navigation link leads to a page that answers with status 200

#### Scenario: Narrow screen
- **WHEN** the start page is shown 360 pixels wide
- **THEN** nothing scrolls sideways and the navigation can still be used

### Requirement: Works without the internet
Every script, stylesheet, font and image a page uses SHALL be served by Rollcall itself. Pages
SHALL tell the browser to refuse content from any other origin.

#### Scenario: Offline shop network
- **GIVEN** the shop network has no internet connection
- **WHEN** a page is loaded
- **THEN** it renders fully, and htmx works

#### Scenario: Outside content blocked
- **WHEN** any page response is inspected
- **THEN** it carries a content security policy that allows only Rollcall's own origin

### Requirement: Safe error handling
When a page is not found or a request fails unexpectedly, Rollcall SHALL show a plain-language
error page in the frame with a short reference code. Stack traces, SQL and file paths SHALL appear
only in the server log next to the same code.

#### Scenario: Unknown address
- **WHEN** a browser opens an address that does not exist
- **THEN** a "Page not found" page in the frame is shown with status 404 and a link to the start
  page

#### Scenario: Unexpected failure
- **WHEN** a request fails with an unhandled error
- **THEN** the browser gets status 500 and a page saying something went wrong with reference code,
  for example `E-7F3K2Q`, and the server log holds the full error under that code

#### Scenario: Failure during a partial update
- **WHEN** a request made by htmx for part of a page fails
- **THEN** the error message, with its reference code, appears in the page's message area and
  the rest of the page stays as it was
