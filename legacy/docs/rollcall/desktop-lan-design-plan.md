# Rollcall desktop and local network design plan

This plan defines how to design, prove, and release the Windows desktop client and shared Rollcall server. The first proof uses your home desktop as the server and your laptop as the second workstation. The shop pilot uses the same release artifacts with shop-specific configuration and separate data.

## 1. Establish the design before implementation

- [x] Inventory the current React, FastAPI, PostgreSQL and PDF code. Record what is live in the existing PDF app and what is sample-only in the Rollcall mockup. Use the mockup as a visual reference when porting screens.
- [x] Reproduce the baseline on the development PC. Install from reviewed pins and run the frontend, backend and isolated PostgreSQL checks. Prove PDF upload, original archival, correction saves and reopening. Save commands, dependency versions and outcomes.
- [x] Record short design decisions for client/server boundaries, LAN addressing and TLS, authentication, PDF handling, and deployment/recovery. For each, capture the default, owner, failure behavior, verification, and any decision needed from shop IT. Validate assumptions with a small prototype before investing in installers or porting every screen.
- [x] Draw the data flow and review the trust boundaries described below against the actual repository. Link risks to controls and acceptance checks. Update the review whenever a new entry point, privilege, or data store is introduced.

See [single-PC proof and verification](desktop-lan-proof.md) for the baseline evidence and remaining checks for Step B.

## 2. Architecture to prove

**Recommended starting design.** One Windows host runs a production build of React and FastAPI behind a single HTTPS origin. PostgreSQL listens locally and the PDF archive lives in a private host directory. The installed Electron client opens the configured Rollcall HTTPS origin in a dedicated window. The server is trusted to deliver the interface, so protect server deployment access and certificate trust as part of desktop security. Keeping UI and API on the same origin lets us reuse the existing relative API calls and upload flow and deploy the UI and API together.

**Alternative to evaluate only if needed.** Package React in the desktop installer and connect to a separately versioned API. This gives stronger control over which UI build each workstation runs, at the cost of coordinating client/API versions and handling cross-origin requests or a native bridge. Use this if the shop needs independent client updates or the server-served UI proof exposes a requirement it cannot meet.

**Configuration contract.** Keep the server address in machine-managed desktop configuration outside business Settings. Use an exact HTTPS origin with a stable DNS name and a valid trusted certificate for that name. For home testing, use a dedicated local hostname and a test CA trusted only on the test machines, or an existing trusted certificate if available. Use separate shop trust and credentials. The address can change at deployment with the same client build. Document what users see when the host is down, the certificate is invalid, or credentials expire.

## 3. Security design and release conditions

No process can guarantee zero vulnerabilities. The release standard is evidence that the controls work, no unresolved release-blocking findings, and an owner and deadline for patching and responding to issues.

| Boundary | Design control | Evidence before shop pilot |
|---|---|---|
| Electron and Windows | Sandboxed renderer, context isolation, Node integration disabled, web security enabled, and no native bridge unless a feature requires one. Restrict navigation to the exact configured origin. Deny popups and permissions by default. Keep untrusted URLs away from OS shell handlers. | Run on a regular Windows account. Confirm the installed app reaches Rollcall, blocks external navigation, and has no desktop privileges exposed to page scripts. |
| LAN and HTTPS | Expose only the HTTPS application endpoint to authorized local workstations. Scope Windows firewall rules to the approved profile and addresses. Keep PostgreSQL, internal API ports, and the archive private. Use normal certificate validation. | From the laptop, verify HTTPS connection and rejected access to database or archive services. Verify an untrusted or wrong-name certificate fails closed. Check guest-network isolation where available. |
| User identity and data | Propose named staff accounts and separate admin privileges for pilot. Enforce permissions in FastAPI on inventory mutations and original-PDF access. Use secure sessions, expiry and server-side audit attribution. For cookie sessions, apply CSRF protections to writes. Use a limited runtime database role and a separate migration role where practical. | Verify signed-out and insufficient-role requests are denied. Verify staff changes are attributed and session expiry prompts sign-in. Keep the named-account decision explicit before any real customer data enters the pilot. |
| PDF upload and archive | Validate type and enforce limits on upload size, processing time and resources. Use server-generated storage identifiers, parameterized database queries, and archive files outside the served UI directory. Render or open documents through an authorized route with isolation appropriate to the chosen PDF viewer. Keep customer data, PDFs, tokens and credentials out of logs. | Use synthetic valid and invalid fixtures. Confirm rejected uploads leave consistent state and authorized staff can reopen archived originals. Review logs and verify files cannot be accessed without authorization. |
| Build and updates | Pin and review dependencies. Check advisories for Electron, npm, Python, the PDF parser and OS components. Build versioned reproducible releases. Sign and verify the Windows installer for shop use, protect signing credentials, and deploy updates from a trusted source. | Save versions, dependency findings, signatures and hashes. Resolve critical and high findings before pilot or document compensating controls and obtain explicit release approval. Verify upgrade and recovery behavior on the laptop. |
| Host and backups | Dedicated non-admin service identity, restricted folders, startup after reboot, logs, and coordinated encrypted backup of the database and referenced PDFs. Track certificate expiry, disk space, backup completion and service health. | Restore to an isolated instance, compare inventory counts and PDF hashes, open original PDFs, and record recovery time and data-loss window. |

Primary desktop references: [Electron security guidance](https://www.electronjs.org/docs/latest/tutorial/security) and [Electron code-signing guidance](https://www.electronjs.org/docs/latest/tutorial/code-signing).

## 4. Build in independently verifiable steps

| Step | Deliverable | Exit evidence |
|---|---|---|
| A. Baseline | Reproducible existing server and PDF workflow with isolated test data. | Frontend and backend checks pass. Record a representative upload, reopen and correction. |
| B. Desktop and LAN proof | Minimal Electron shell and configurable HTTPS origin. Desktop hosts a test instance. Laptop opens it from Start in a Rollcall window. | Successful launch, rejected invalid certificate, blocked external navigation, and usable offline/reconnect screen. The installer and server configuration are versioned. |
| C. Thin live inventory | Add inventory schema, database-backed list/search and set/profile reads. Use synthetic seeded records first. Port the approved Inventory views into the React app. | Both machines see the same records and search by sample sizes and identifiers. A host restart retains records. PDF workflow remains verified. |
| D. Workflow integration | Add PDF-driven inventory changes, same-work-order revisions, third-set selection, removal and renewal. Preserve source evidence and history. | Concurrent submissions and lost-response retries apply one action. Third-set selection makes no change until selected. Consequential revisions go to review. |
| E. Release rehearsal | Build signed desktop installer, host startup/migration procedures, backup and restore steps, and a release evidence log. | Install, upgrade, restart, and recover the home setup using the same artifacts and procedure intended for the shop. |

For each step, define expected behavior and failure checks before implementation. Make the smallest vertical change, verify it through the installed app and server where applicable, and retain evidence with the release version. Keep interface refinements outside the critical path unless they prevent staff from completing or understanding a workflow.

## 5. Two-PC home rehearsal and shop cutover

1. **Prepare home.** Desktop gets a reserved LAN address or stable local DNS entry and a separate test database and archive. Laptop uses an ordinary Windows account and the installer. Use synthetic records throughout. Do not forward router ports or open the app to the internet.
2. **Run the rehearsal.** Confirm successful sign-in and search on both machines. With workflow integration present, submit a synthetic PDF on one and reopen it on the other. Exercise duplicate submission, stale edits, host shutdown/restart, session expiry, and certificate failure. Confirm the UI makes it clear when the last displayed data is stale and does not silently queue offline writes.
3. **Rehearse recovery.** Take a coordinated backup, restore separately, run the same smoke checks, and verify the update procedure on both machines. Keep screenshots and logs free of private data. Home results prove the workflow under home conditions. Shop DNS, firewall, Windows policy and certificate trust get their own checks.
4. **Prepare shop.** Confirm the host, IT owner, network scope, certificate and signing approach, backup destination, retention, and acceptable recovery time/data loss. Agree how opening inventory will be populated and validated. Provision a fresh shop environment and verify that the intended workstation can reach it.
5. **Pilot and roll back if needed.** Start with one workstation and controlled sample transactions. Release real data only after the security, restore and access checks pass. Keep a pre-upgrade recovery set. If readiness, inventory integrity or PDF access fails, pause writes and follow the tested restore or compatible rollback procedure. Expand to additional workstations after pilot acceptance.

### Project references

- [Rollcall product specification](specification.md)
- [Screens and shop operations](screens-and-operations.md)
- [PDF and inventory workflows](workflows.md)
- [Current handoff](CHAT_CONTINUATION.md)
