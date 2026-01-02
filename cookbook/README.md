# frontend-contrib

Common files for ocn sk frontends.

## Keep this structure

- app
  - contrib
  - deployment
  - frontend
    - frontend-contrib
      - README (this file)
      - ...
    - public
    - src
    - .env (config local env with VITE_* env variables)
    - jsconfig.json (needs to be copied per project)
    - package.json (commands should be copied)
    - yarn.lock
  - src
  - tests
  - ...

## Project Setup

```sh
yarn
```

### Compile and Hot-Reload for Development

```sh
yarn run dev
```

### Format code

```sh
yarn run format
```

### Check code

```sh
yarn run lint
```
