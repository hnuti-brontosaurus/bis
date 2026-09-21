# Forms

We manage forms with [react-hook-form](https://react-hook-form.com/) and
validate them with [yup](https://github.com/jquense/yup) through
`@hookform/resolvers`. See
[`CloseEventForm`](../src/org/pages/CloseEvent/CloseEventForm.tsx) for a form
that uses both, splits itself into steps, and persists what the user typed.

To keep the data across a page refresh, see [persistent forms](persistent-forms.md).

## Controlled inputs must never receive `undefined`

When a controlled component gets `value={undefined}`, React switches the input
to uncontrolled and stops touching its DOM value. Clearing the field in the
form then changes nothing on screen — the user keeps seeing the old value,
until some other interaction happens to rewrite it.

Our form values are frequently `null` (that is what the API returns and
accepts), so the fallback has to produce an empty value, not `undefined`:

```tsx
// wrong — a null value leaves the previously typed text on screen
<input value={value ?? undefined} />

// right
<input value={value ?? ''} />
```

## Reset a form only after the submit succeeded

`handleSubmit` callbacks may be `async`. Await the API call and reset only when
it went through, so a rejected submit leaves the user's input in place to fix
instead of forcing them to type the whole row again.

```tsx
const handleFormSubmit = handleSubmit(async data => {
  if (!(await onSubmit(data))) return
  setFocus('first_name')
  reset({ first_name: '', last_name: '' })
})
```

Call `setFocus` _before_ `reset`, not after: `reset` re-registers the inputs, so
immediately after it react-hook-form cannot find the field yet and `setFocus`
throws.

## Show the reason the API rejected the data

A generic "něco se nepovedlo" tells the user nothing about which field to fix.
[`useShowApiErrorMessage`](../src/features/systemMessage/useSystemMessage.ts)
takes an rtk-query error and renders the backend's per-field messages as the
detail of the system message. Pass the translations of the model being written
so the field names come out in Czech:

```tsx
const [createSimpleParticipant, createStatus] =
  api.endpoints.createSimpleParticipant.useMutation()
useShowApiErrorMessage(
  createStatus.error,
  'Nepodařilo se přidat účastníka',
  translations.user,
)
```

Prefer this over catching the error and calling `useShowMessage` with a message
of your own — that throws the backend's explanation away.

## Extract async operations into a hook

When submitting or switching something means several steps — an API call, a
cache update, then a change of form state — put the server-side part in a hook
of its own and leave the form-state part in the component that owns the form.
The hook stays testable and reusable, and it stays obvious which piece of state
each line is changing.
[`useSwitchAttendanceListType`](../src/org/pages/CloseEvent/useSwitchAttendanceListType.ts)
is an example: it sends the PATCH and resets the rtk-query cache, and reports
whether it succeeded; its caller mirrors the change into the form fields.

Reusable hooks live in [`src/hooks/`](../src/hooks). A hook used by a single
page belongs next to that page.

## Show that an async change is in flight

While a request that will change what the form displays is running, the user is
looking at the old form with the old values and nothing tells them that
anything is happening. Render `<Loading>` in place of the part that is about to
change:

```tsx
<FormSectionGroup>
  <FormSection header="Způsob registrace účastníků">
    {/* the picker */}
  </FormSection>
  {isSwitching ? (
    <Loading>Měníme způsob zadání účastníků</Loading>
  ) : (
    <>{/* the sections that depend on the mode */}</>
  )}
</FormSectionGroup>
```
