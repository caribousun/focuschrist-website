# GitHub connection and release continuity

Repository: caribousun/focuschrist-website. Production branch: main.

The owner authorized the connected GitHub plugin to publish approved Focus changes. The plugin was verified as caribousun with repository push/admin access. Use this existing authorized connection when CLI authentication is unavailable. Plugin authorization and local CLI authentication are separate; an unauthenticated CLI does not mean the plugin is disconnected.

At release start, verify plugin account, repository access and current main. Prefer an already authenticated, permitted CLI when available. Do not repeatedly ask for device authorization: here the browser step succeeds but the CLI token exchange is blocked by runtime network policy. Do not export plugin credentials, store tokens in memory, or alter network controls.

Build and test locally. Upload nonempty blobs and compare every returned Git SHA with the local Git hash. Create a tree from current main, a release branch and PR. Never reuse earlier empty blobs. Require successful checks, merge, then verify deployment and live pages. Local tests or a created PR alone do not establish publication.

Check connection availability each session. This record preserves procedure and owner authorization, not a guarantee that app connections never expire. Ask for reconnection only if the plugin itself reports missing authorization.
