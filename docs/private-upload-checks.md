# Private upload checks

Checked on September 5, 2026. This is a development snapshot, not a public release
or a statement that the book is ready for publication.

## Verification

- Installed from the existing lock file with the figures dependency group.
- Full offline suite: 732 passed in 522.58 seconds, using Python 3.12.13.
- Ruff static checks passed.
- Skill package validation passed.
- All six derived CSV checksums passed.
- The README hiring-pipeline example ran and returned a Result.
- Pattern-based credential scan found no matches.
- The dedicated detect-secrets scan flagged only dataset checksums, pinned model
  hashes, and synthetic checksum fixtures. Each finding was reviewed.

These checks do not constitute a comprehensive security audit or independent
verification of all scientific claims. Live data retrieval was not tested.

## Packaging decisions

The snapshot starts a new Git history. It does not upload prior repository history,
the manuscript, book PDF or EPUB, raw downloads, local environments, or caches.
The manuscript-only figure-reference checker was omitted because it requires
unpublished manuscript files and contained an author-specific filesystem path.
It remains available in the original development repository.

The data fetch scripts identify the publishing GitHub profile instead of a personal
email address. Git attributes preserve exact CSV bytes across platforms. The commit
uses the publishing account's GitHub no-reply address.

## Before public release

Obtain the publisher's code-license choice and final attribution review, address the
book publication-review findings, check the reader instructions on a fresh download,
and approve a versioned release matching the book edition. Only then configure and
verify the stable public download redirect and create the book QR code.
