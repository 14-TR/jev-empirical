# Security and publication policy

- Supply `TYPESAFE_API_KEY` through the process environment, never source files, command-line values, notebooks, URLs, or GitHub workflow configuration.
- Live inference is opt-in. Automated CI must run offline without credentials.
- Keep raw requests/responses and execution logs outside the repository. Publish only explicitly reviewed, allowlisted result fields. Sanitization is not permission to publish private inputs.
- Run only original public diagnostic inputs until dataset provenance and redistribution rights have been reviewed. Do not send user conversations or private project data.
- Fix the provider endpoint, reject redirects, bound request counts and runtime, and disable hidden retries. Request limits are not dollar ceilings; distinguish price estimates from actual invoices.
- Review exact staged paths and complete Git history for secrets before every public push. Ignore rules alone do not protect already-tracked files.
- Do not paste credentials into issues. If exposure occurs, revoke the credential first, then remove the exposure and assess Git history and caches. Deleting a file is not revocation.

## Reporting

Report non-sensitive defects through GitHub issues. Do not include keys, personal data, raw account responses, or private logs. No secure private reporting channel has yet been established.
