import { expect, type Page, type Request } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

const fixturesDir = path.join(__dirname, '..', 'fixtures')

export const fixture = <T = Record<string, any>>(name: string): T =>
  JSON.parse(fs.readFileSync(path.join(fixturesDir, `${name}.json`), 'utf8'))

export const asset = (name: string) =>
  path.join(__dirname, '..', 'assets', name)

export type Matcher = {
  method?: string
  /** Exact path, or a glob where `*` matches anything but `/`. */
  pathname?: string | RegExp
  url?: string | RegExp
}

export type Reply = {
  status?: number
  body?: unknown
  /** Name of a file in e2e/fixtures, without the .json suffix. */
  fixture?: string
}

export type Responder = Reply | ((request: Request) => Reply | Promise<Reply>)

export type RecordedRequest = {
  url: string
  method: string
  query: URLSearchParams
  body: any
}

/**
 * Replaces `cy.intercept(...).as(alias)` + `cy.wait('@alias')`. The recorder
 * keeps every request the route handled, so a spec can assert on a call that
 * already happened — unlike `page.waitForRequest`, which only sees the future.
 */
export class Recorder {
  readonly calls: RecordedRequest[] = []

  async nth(index: number, timeout = 15_000): Promise<RecordedRequest> {
    await expect
      .poll(() => this.calls.length, { timeout })
      .toBeGreaterThan(index)
    return this.calls[index]
  }

  first(timeout?: number) {
    return this.nth(0, timeout)
  }

  /** Waits until exactly `expected` calls landed and returns them. */
  async all(expected: number, timeout = 15_000): Promise<RecordedRequest[]> {
    await expect.poll(() => this.calls.length, { timeout }).toBe(expected)
    return this.calls
  }
}

const globToRegExp = (glob: string) =>
  new RegExp(
    `^${glob.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '[^/]*')}$`,
  )

const matchesPattern = (pattern: string | RegExp, value: string) =>
  pattern instanceof RegExp
    ? pattern.test(value)
    : globToRegExp(pattern).test(value)

const matches = (rawUrl: string, matcher: Matcher) => {
  const { pathname } = new URL(rawUrl)
  if (
    matcher.pathname !== undefined &&
    !matchesPattern(matcher.pathname, pathname)
  )
    return false
  if (matcher.url !== undefined && !matchesPattern(matcher.url, rawUrl))
    return false
  return true
}

const record = (request: Request): RecordedRequest => ({
  url: request.url(),
  method: request.method(),
  query: new URL(request.url()).searchParams,
  body: request.postData() === null ? null : request.postDataJSON(),
})

/**
 * Registers a stub for requests matching `matcher`. Playwright runs route
 * handlers newest-first, so a stub registered inside a test overrides one from
 * a `beforeEach` — the same precedence Cypress gives `cy.intercept`.
 */
export const mock = async (
  page: Page,
  matcher: Matcher,
  responder: Responder = {},
  options: { times?: number } = {},
): Promise<Recorder> => {
  const recorder = new Recorder()

  await page.route(
    url => matches(url.toString(), matcher),
    async route => {
      const request = route.request()
      if (matcher.method && request.method() !== matcher.method)
        return route.fallback()

      recorder.calls.push(record(request))

      const reply =
        typeof responder === 'function' ? await responder(request) : responder
      const body = reply.fixture ? fixture(reply.fixture) : (reply.body ?? {})

      await route.fulfill({ status: reply.status ?? 200, json: body })
    },
    options,
  )

  return recorder
}
