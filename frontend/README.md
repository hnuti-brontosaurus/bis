# App for Brontosaurus information system

## Documentation

Read and improve the documentation in the [`docs` folder](docs)

## Developer quickstart

1. Prerequisity: have Node.js and yarn installed
1. Clone this repository
1. Go to working directory: `cd bis-frontend`
1. Install dependencies: `yarn`
1. Run development version: `VITE_API_BASE_URL="https://dev.bis.brontosaurus.cz/api/" VITE_CORS_PROXY="https://bis.proxy.mrkvon.org/" yarn dev`

## Production quickstart

1. Prerequisity: have Node.js and yarn installed
1. Clone this repository
1. Go to working directory: `cd bis-frontend`
1. Install dependencies: `yarn`
1. Build production version (make sure to setup or omit variables as you need): `VITE_API_BASE_URL="https://dev.bis.brontosaurus.cz/api/" VITE_CORS_PROXY="https://bis.proxy.mrkvon.org/" yarn build`
1. A `build/` folder should have been created in the root of your project. Copy the files from `build/` to your production server, and [serve as single page application for example with nginx](https://gist.github.com/huangzhuolin/24f73163e3670b1cd327f2b357fd456a).

## Configuration

Configuration is done with environment variables. These variables should never contain secrets. After build, they'll be hardcoded in build files and therefore easily discoverable. They serve exclusively to set up configuration constants.

All Vite environment variables must be prefixed with `VITE_`.

To run the app in development version

```
VITE_VAR1="something" VITE_VAR2="something_else" yarn dev
```

To build the app

```
VITE_VAR1="something" VITE_VAR2="something_else" yarn build
```

- `VITE_API_BASE_URL` API base url, including trailing slash (default `/api/`)
- `VITE_SENTRY_DSN` a dsn for Sentry setup (disabled when none)
- `VITE_CORS_PROXY` A proxy which adds CORS headers to images, including trailing slash (default none)
- `VITE_MAP_TILE_SERVER` [url template](https://leafletjs.com/reference.html#tilelayer-url-template) of map tiles
- `VITE_MAPY_CZ_API_KEY` API key for mapy.cz geocoding

## Running locally with a remote proxy

`VITE_API_BASE_URL="https://dev.bis.brontosaurus.cz/api/" VITE_CORS_PROXY="https://bis.proxy.mrkvon.org/" yarn dev`

## Running locally with a local proxy

### Set up the proxy

In a new terminal run:

1. `git clone https://github.com/mrkvon/rdf-proxy.git`
1. `cd rdf-proxy`
1. `git switch cors-anywhere`
1. `yarn`
1. `yarn proxy`

And the proxy will run on `http://localhost:8080` and you can do `http://localhost:8080/https://example.com/whatever`

### Run the app

Use the command: `VITE_API_BASE_URL="http://localhost:8080/https://dev.bis.brontosaurus.cz/api/" VITE_CORS_PROXY="http://localhost:8080/" yarn dev`

## Analyzing bundle size

```sh
yarn analyze
```

## Testing
### Unit tests (vitest)
```sh
yarn test:unit
```
### Integration tests (cypress)
**Dev server must be running on `localhost://3000`!**
```sh
yarn test:e2e
```
