# Release policy

The repository remains private during book drafting and development. Every private release must pass
the full test suite, skill validation, static analysis, and human review.

Before publication, review source attribution, licensing, repository metadata, secrets, and public
documentation. The book printed link and QR code must resolve through an author-controlled stable
redirect to the versioned release that matches the book edition. The QR code must never target an
unversioned default branch.

## Publication gate

A public release requires a human check of source attribution, licensing, secret scanning, document
links, and the final book edition tag. Create the QR code only after the stable redirect resolves to
that tagged public release.
