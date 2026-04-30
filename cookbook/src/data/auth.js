import { client } from "./client.js"

export const authApi = {
  whoami: () => client.get("/auth/whoami/").then(r => r.data),
  checkEmail: (email, config) =>
    client.post("/auth/check_email/", { email }, config).then(r => r.data),
  validatePassword: password =>
    client.post("/auth/validate_password/", { password }).then(r => r.data),
  login: payload => client.post("/auth/login/", payload).then(r => r.data),
  register: payload => client.post("/auth/register/", payload).then(r => r.data),
}
