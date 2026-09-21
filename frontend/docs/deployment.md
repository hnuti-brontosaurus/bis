# Deployment

## Deployment to development server https://dev.bis.brontosaurus.cz

Every push to `master` is deployed to the [development server](https://dev.bis.brontosaurus.cz) once the app builds and the tests pass.

From any other branch, including feature branches, put `#deploy` in the commit message and that commit gets deployed too, e.g. `chore: update frontend #deploy`. In any case, please use commit messages consistent with current backend commit style.

Both are driven by [ci.yml](../../.github/workflows/ci.yml).

## Deployment to production server

When a commit is tagged with tag `v*.*.*`, a production build gets created. Then an administrator has to confirm the deployment.

## Deployment to github pages

> **Stale.** This describes the frontend when it lived in its own repository. The
> `deploy-dev.yml` workflow it refers to no longer exists here, and the frontend
> is now built and served by the backend image (see [ci.yml](../../.github/workflows/ci.yml)).
> The `yarn deploy` script and the variables below are kept for reference until
> someone confirms whether the github-pages build is still used.

You'll need to set up the following environment variables and secrets for such an environment:

### Deployment variables

- `URL` - where the app will live (must be domain name without `https://` and without trailing slash)
- `API` - base url for api, especially useful when on different domain; it should be set up to allow CORS (optional)
- `CORS_PROXY` - proxy to fix CORS issues with images (optional)

### Deployment secrets

- `DEPLOY_GH_PAGES_SSH_KEY` - Private key for pushing to the target repo. The target repo itself has to have the public key added
- `SENTRY_DSN` - Sentry setup
