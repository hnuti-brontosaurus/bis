# Persistent forms

## Overview

When user writes data into a form, and refreshes the page, she loses her data by default. We want to fix that.

So, we need to store the data somewhere, and then repopulate the form with these data after refresh - in our case we shall store the data in browser's local storage.

## How it works

The logic of saving, retrieving and clearing the persistent data is implemented in [persistForm](../src/hooks/persistForm.ts) hooks.

1. we watch the data changes with react-hook-form watch
1. we save the data (debounced) into redux (reducer is defined in [formSlice](../src/features/form/formSlice.ts))
1. the redux form state is persisted with redux-persist library (it's setup in [store](../src/app/store.ts))
1. we save and delete the data with redux actions
1. we select the data with redux selector

## Usage

see how it's used in [OpportunityForm](../src/org/OpportunityForm.tsx) and [CloseEventForm](../src/org/CloseEvent/CloseEventForm.tsx)
