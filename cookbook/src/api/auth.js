import { client } from "./client.js"

export const whoami = () => client.get("/auth/whoami/").then(r => r.data)

export const checkEmail = email =>
  client.post("/auth/check_email/", { email }).then(r => r.data)

export const validatePassword = password =>
  client.post("/auth/validate_password/", { password }).then(r => r.data)

export const login = payload => client.post("/auth/login/", payload).then(r => r.data)

export const register = payload =>
  client.post("/auth/register/", payload).then(r => r.data)
