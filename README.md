# Herdr Next Agent Plugin

A [Herdr](https://herdr.dev) plugin that jumps to the next agent needing attention.

Unlike Herdr's built-in `next_agent` / `previous_agent` bindings, which cycle agents in panel order, this plugin ranks agents by how urgently they need you (blocked first, then finished-but-unseen, then idle by default) and focuses the top one. If the agent you are already looking at is itself in the ranked list, it jumps to the one after it, so pressing the shortcut repeatedly cycles through every agent that needs attention.

## Install

```bash
herdr plugin install martin-ro/herdr-next-agent
```

Or for local development, clone the repo and link it in place:

```bash
git clone https://github.com/martin-ro/herdr-next-agent.git
herdr plugin link ./herdr-next-agent
```

Requires Python 3.11+ on the PATH (uses only the standard library).

## Keybinding

Herdr owns keybindings, so bind the action in your `~/.config/herdr/config.toml`. Suggested default:

```toml
[[keys.command]]
key = "prefix+u"
type = "plugin_action"
command = "martinro.next-agent.jump"
description = "next agent needing attention"
```

Then apply it:

```bash
herdr server reload-config
```

Pick any other key you like; the plugin only ships the action.

## Configuration

The plugin seeds a `config.toml` in its config dir on first run. Find it with:

```bash
herdr plugin config-dir martinro.next-agent
```

```toml
# Agent statuses that count as "needs attention", highest priority first.
# Statuses not listed are never jumped to.
# Known statuses: blocked, done, working, idle, unknown
priority = ["blocked", "done", "idle"]

# "all" = consider agents in every workspace; "workspace" = active workspace only
scope = "all"
```

- `priority`: reorder or remove statuses to change what "needs attention" means. For example, `priority = ["blocked", "done"]` never jumps to idle agents.
- `scope`: set to `"workspace"` to only consider agents in the active workspace.

Config is read on every invocation; no reload needed.

## Troubleshooting

```bash
herdr plugin action invoke martinro.next-agent.jump   # run the action manually
herdr plugin log list --plugin martinro.next-agent    # see errors
```
