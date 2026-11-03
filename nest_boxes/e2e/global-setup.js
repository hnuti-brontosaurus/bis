// Seeds once per run, before any spec signs in as the seeded users.
export default async config => {
  const { baseURL } = config.projects[0].use
  const response = await fetch(`${baseURL}/api/nest_boxes/testing/seed/`, {
    method: "POST",
  })
  if (!response.ok) throw new Error(`Seeding failed: ${response.status}`)
}
