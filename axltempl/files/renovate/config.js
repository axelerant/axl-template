module.exports = {
  platform: "gitlab",
  endpoint: "{gitlab_api}",
  token: process.env.GITLAB_TOKEN,
  assignees: [],
  baseBranches: ["master"],
  repositories: ["{repo}"],
  labels: ["renovate"],
  extends: ["config:base"],
  gitAuthor: "Renovate <renovate@axelerant.com>",
  logLevel: "debug",
};
