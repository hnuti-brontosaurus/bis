# Start contributing

This is an intro how to start fixing or adding features

This project is written in [React](https://reactjs.org/) and [Typescript](https://www.typescriptlang.org/). It's a single page application and it was initialized with [Create React App](https://create-react-app.dev/).

Some of the extensively used libraries are

- [react-hook-form](https://react-hook-form.com/) for managing html forms
- redux with [redux-toolkit](https://redux-toolkit.js.org/), and [rtk-query](https://redux-toolkit.js.org/rtk-query/overview) to manage application-wide state, and api calls, respectively
- [react-router](https://reactrouter.com/en/main) for application routing

They typically have a good documentation which is worth reading when something is unclear.

## File structure

Please also refer to [Style guide](style-guide.md)

### A good starting point

The app starting point is `src/index.tsx`. Some libraries are set up here, and the rest of the app is imported here.

But at first, it may be more relevant for you to start at `src/App.tsx`. You'll find application-wide routing here. Page layouts and pages are imported here, so you can use it as a code crossroad.

[Run the app](../README.md#developer-quickstart), try changing something &mdash; and see what happens...

### Files and folders

- all the app code is in `src/`
- public stuff is in `public/`
- and some configurations are in the root. `package.json` and `tsconfig.json` might be the most important

Within the `src/`, you may find the following structure:

- `pages/`, `org/pages` and `user/pages` - routing pages
- `layout/` - components related to app layout and main routing outlets
- `components/` - reusable components
- `utils/` - helper functions
- `styles/` - scss stylesheets that are not bound to any particular tsx component
- `hooks/` - reusable component logic extracted in the form of react hooks
- `features/` and `app/` - redux stuff
- `app/services/` - connection to [api](api.md)
- `assets/` - stuff that's not code - images, icons, fonts etc...

## API

Go to [api.md](api.md)

## IDE

We used Visual Studio Code to write this project, and there is a config for it here already, but you can of course use any other IDE.

For `vscode`, you may find the following extensions useful:

- `dbaeumer.vscode-eslint`
- `csstools.postcss`
- `esbenp.prettier-vscode`
- TypeScript language support seems to be included by default

## Contact

You can contact [Talita](mailto:dzikilubiabloto@protonmail.com) or [Michal](mailto:michal.salajka@protonmail.com) to learn more. We may call, go through the code and answer questions etc. which could make your onboarding smoother. They can speak in English, Czech and Polish. Don't hesitate to ask!
