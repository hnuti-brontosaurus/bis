# API

This app is based on [BIS API](https://github.com/hnuti-brontosaurus/bis), which currently (2023/03) runs e.g. at https://dev.bis.brontosaurus.cz/api/

## Connection

We use [rtk-query](https://redux-toolkit.js.org/rtk-query/overview) to connect to the API.

## How to add a new endpoint

The code that connects us to API lives in `src/app/services/bis.ts`. There is the list of endpoints that we _actually_ use.

There is also `src/app/services/testApi.ts` that gets automatically generated.

Whenever API changes, or whenever you feel like, run

```sh
yarn generate-api
```

This updates the automatically generated `testApi.ts` mentioned above.

All the available endpoints.read exported here, and also the TypeScript types related to API.

But there are mistakes, and the enpoints have funny names.

If you need a new endpoint, try to locate it in the `testApi.ts`, copy it to `bis.ts`, rename it (e.g. to `createEvent`, `readEvent(s)`, `updateEvent`, `removeEvent`, ...), and include proper, simpler types, too. As of now, you also need to remove `/api/` string at the beginning of the query url.

If you want to export a type from `testApi.ts`, first import it to `bisTypes.ts`, fix it if needed, and export it from `bisTypes.ts`. All the types from `testApi` should go through `bisTypes`, so we keep track of what's included and what's not.

In other words, don't import types directly from `testApi`. Use `bisTypes` for that purpose.
