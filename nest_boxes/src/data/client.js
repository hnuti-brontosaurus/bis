import axios from "axios"

// Signed in through the Django session the BIS login creates; DRF's session
// authentication wants the CSRF token back as a header on every write.
export const client = axios.create({
  baseURL: "/api/nest_boxes",
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  // django-filter reads a list as the key repeated, without brackets
  paramsSerializer: { indexes: null },
})

const relative = url =>
  url.replace(/^https?:\/\/[^/]+/, "").replace(/^\/api\/nest_boxes/, "")

export const fetchAll = async (url, config) => {
  const results = []
  let next = url
  while (next) {
    const { data } = await client.get(relative(next), config)
    results.push(...data.results)
    next = data.next
  }
  return results
}
