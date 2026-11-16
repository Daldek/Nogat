# Security policy

## Supported versions

Nogat publishes no package yet (HUB §7). Security fixes go into the
development branch `develop` and, once it is published, into the latest
version of the standard on `main`. Older versions are not patched.

## Reporting a vulnerability

Please do not report vulnerabilities in public issues or pull requests.

Use GitHub's private vulnerability reporting: open the **Security** tab of
<https://github.com/Daldek/Nogat>, choose **Report a vulnerability** and
describe the problem, the affected commit or version and, if possible, how to
reproduce it. You get an answer as soon as the maintainer can read the report;
a fix is credited in the CHANGELOG unless you prefer otherwise.

## Scope

Nogat is the hub of the ecosystem: the standard, the project registry and the
scripts that read it. Reports about the scripts in `scripts/` (they read the
checkouts of the other projects, run `git fetch` in them and, with
`set apply`, write one project's manifests), the gate and CI templates in
`standards/ci/` that the projects copy, the JSON Schemas in `schemas/`, or the
supply chain of the hub's environment (`uv.lock`) are in scope. Each tool of
the ecosystem (Kartograf, Obserwator, Hydrolog, Hydrograf, Hydraulik, Retman,
Archiwista) has its own policy; report its defects in its repository.
