# Campus Supply · Web UI automation

A student signs in, searches a supply catalog, and submits a pickup reservation. Five executable examples cover successful and rejected sign-in, a case-insensitive partial match, an empty result, and a reservation confirmation. Each browser runs the same Gherkin feature.

## Setup and first run

Use Python 3.11, Node.js 22 or newer, Java 17, and Docker with Compose (or an accessible Redis server). Run commands from the repository root. On Windows, use PowerShell and substitute `npm.cmd` or `npx.cmd` if script execution is restricted.

```sh
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on macOS/Linux. Install the test runner and the report generator.

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium firefox webkit
npm ci
docker compose up -d
```

On Linux runners use `python -m playwright install --with-deps chromium firefox webkit` to install system libraries. The bundled Compose service uses host port 16379. Set `$env:REDIS_URL="redis://localhost:16379/0"` in PowerShell or `export REDIS_URL=redis://localhost:16379/0` in bash. An existing Redis service on localhost:6379 needs no override. Use a dedicated fixture database. Seeding updates keys under `campus-supply:fixture:`.

```sh
python -m framework.seed_redis
python -m behave
npx allure generate allure-results --single-file --clean -o allure-report
```

Open `allure-report/index.html` directly. In Suites, select a scenario to inspect its steps and execution log. A failed UI step includes a screenshot. For a fresh local report, point Behave at a new results directory using `python -m behave -f allure_behave.formatter:AllureFormatter -o run-results` and give that directory to Allure. Stop the local service with `docker compose down`.

## Run options

| Setting | Default | Purpose |
| --- | --- | --- |
| BROWSER | chromium | chromium, firefox or webkit |
| HEADED | unset | Set to 1 to watch the browser |
| BASE_URL | temporary loopback server | URL of another Campus Supply deployment |
| REDIS_URL | redis://localhost:6379/0 | Fixture service connection |

For Firefox, set `$env:BROWSER="firefox"` in PowerShell or `export BROWSER=firefox` in bash before running Behave. Run `python -m behave --tags=@search` for just the database-backed examples. Run `python -m behave --tags="not @redis"` when working offline without Redis. Use `python -m behave --dry-run -f pretty` to inspect step matching.

## Architecture and test data

| Location | Responsibility |
| --- | --- |
| app/index.html | Self-contained training application with demo credentials and an in-page reservation confirmation |
| features/shop.feature | Business behavior and named example rows |
| features/steps/shop.py | Resolve fixture IDs, perform user actions and assert visible outcomes |
| features/environment.py | Start a local server and browser per run, create a clean browser context per scenario, capture evidence and close resources |
| framework/pages.py | Encapsulate accessible locators and user interactions |
| framework/data.py | Read account rows from Excel, search cases using a parameterized SQLite query, and order JSON from Redis |
| fixtures/ | Versioned workbook, SQLite database and Redis seed records |
| .github/workflows/ | Browser matrix, reviewed merge and private report publication |

The local application makes each run independent of third-party uptime. Playwright's role and label locators follow the accessible UI and its assertions wait for visible state. Page objects concentrate changes to controls. Behave expands each Examples row into a separately reported case. Test expectations live in the feature or fixtures, independently of the application implementation.

### Add a case

For a second rejected login, add an Excel row with id `unknown`, username `visitor` and password `demo` to `fixtures/accounts.xlsx`. Append this line to the sign-in Examples table in `features/shop.feature` and run `python -m behave --tags=@login`.

```gherkin
      | unknown | Sign-in failed |
```

For a search case, add a row to the SQLite `searches(id, term, expected)` table and reference its id in the search Examples table. Use an empty expected string for zero matches. For an order, add a named object with product and student fields to `fixtures/reservations.json`, rerun the Redis seeder, and reference its key in a reservation scenario. Add a page object method and step definition when a new workflow requires a new interaction.

## Implementation plan and team responsibilities

| Step | Work and acceptance evidence | Responsible member |
| --- | --- | --- |
| 1 | Set up private repository, invite teammate and track tasks | moosarehan |
| 2 | Implement repeatable shop, browser lifecycle and page objects | moosarehan |
| 3 | Define expected sign-in, search and pickup outcomes and review Gherkin coverage | muhammadumarafzaal |
| 4 | Review Excel, database and Redis fixtures against expected UI outcomes | muhammadumarafzaal |
| 5 | Configure test matrix, merge workflow and report deployment | moosarehan |
| 6 | Review setup and execution evidence, record findings and sign off | muhammadumarafzaal |

Track framework and workflow work in issues #1 and #2 and teammate review in #3 and #4. These responsibilities describe ownership. Actual reviews are recorded on GitHub.

## GitHub workflow and submission

1. Pick an issue, create a feature branch, and commit a focused change. Open a pull request against main, link the issue, describe changed behavior and provide the local test result.
2. The UI acceptance workflow starts Redis and runs the full suite independently in Chromium, Firefox and WebKit on Ubuntu. Each job uploads its raw Allure results, including on test failure. The report job builds the downloadable execution-report artifact.
3. Request review from the other member. After approval, a maintainer can run **Merge reviewed change** from Actions on main with the PR number. It checks approval and successful CI at the PR head before merging. It explicitly dispatches acceptance after a token-driven merge. Ordinary merges trigger testing through a push to main.
4. A successful main build publishes the standalone HTML report on the private reports branch. Download the raw HTML and open it locally. The Actions run retains the report and raw results as grading evidence. If a run fails, inspect the job and scenario attachments, update the branch, and rerun CI.
5. Submit the private repository link, grant the evaluator access as needed, and include the example report. Use the commit history, issue discussion and reviewed PRs as evidence of team contributions.

