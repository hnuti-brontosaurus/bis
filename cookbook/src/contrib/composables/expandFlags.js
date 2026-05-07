// Symbol-keyed flags for collapsible UI state on dynamic-input rows.
// Symbols are skipped by JSON.stringify, so the flags never reach the API.
export const SHOW_COMMENT = Symbol("show_comment")
export const SHOW_DETAILS = Symbol("show_details")
