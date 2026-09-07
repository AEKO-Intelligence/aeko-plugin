# Local customization contract

Save changes only in the selected brand-owned working package. An installed plugin cache, a
shared upstream checkout, and global chat memory are not durable customer storage. Keep the
canonical `aeko-*` command directory and an immutable copy of the previous version.

Before editing, record the exact brand/domain, local package path, current file hashes, and the
skill or wiki section being changed. Add only files the owning `SKILL.md` tells the executor to
read. Examples can guide tone and structure, but they are not factual evidence or permission to
reuse prices, claims, or customer experience.

After editing, show the diff and run the local package checks. A local save does not activate a
backend version. OAuth also does not load package bytes. Only say a later run will use the change
after the host has selected the package and loaded the edited skill, applicable evals, required
wiki pages, and support files.

For an exported package, verify `package-manifest.json` and every file SHA-256. Keep projected
skill/wiki references tied to their original document, version, stored digest, authority, and
sources. Do not import another brand's package, fetch the latest source at run time, or treat a
GitHub connection as synchronization. The full Responses/MCP runner, contextual chat executor,
and GitHub App provisioning/sync are separate services.
