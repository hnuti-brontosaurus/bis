# Testing

We use [Cypress](https://www.cypress.io/) for testing.

The testing files are placed in [`cypress/`](../cypress) folder and [cypress config](../cypress.config.ts)

We have integration tests in [`cypress/e2e/`](../cypress/e2e/). For these tests, we stub api calls. The api therefore doesn't have to be set up before running these tests

## Run tests

### Interactive

To run tests interactively,

1. `BROWSER=none yarn start` - run the app on default port 3000 without any specific api settings
   If other app is running on port 3000, you'll have to stop it first
1. `yarn cypress open`
1. Select e2e tests from the available options
1. Select your preferred browser
1. Select a test file to run from list

### Automatic

To run tests automatically, run `yarn e2e`. Be careful, this command will kill all your node processes at the end (this should be fixed, but currently we don't know any better...)

### Continuous integration

We also have CI[^ci] [set up with github workflows](../.github/workflows/main.yml). It runs tests on github after every push and merge to `main` branch there.

[^ci]: continuous integration

We haven't figured out how to run tests against live api without stubbing, yet.
