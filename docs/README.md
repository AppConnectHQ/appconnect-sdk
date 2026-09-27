# AppConnect SDK docs

Source for the AppConnect developer documentation. Pages are MDX with
Mintlify-style components (`<CodeGroup>`, `<Card>`, `<Warning>`), and
`docs.json` defines the navigation. The content isn't tied to a host yet.

## Layout

| Path                     | Contents                                              | Edited by           |
| ------------------------ | ----------------------------------------------------- | ------------------- |
| `index.mdx`, `quickstart.mdx`, `concepts.mdx` | Overview, first integration, core concepts | Hand-written |
| `guides/`                | Task guides, each with TypeScript and Python examples | Hand-written        |
| `platform/`              | Integrations catalog, MCP, REST API                   | Hand-written        |
| `reference/typescript/`  | API reference for `@appconnecthq/sdk`                 | **Generated**       |
| `reference/python/`      | API reference for `appconnect`                        | **Generated**       |
| `changelog.mdx`          | Links to `typescript/CHANGELOG.md` and `python/CHANGELOG.md` | Hand-written |

## Regenerating the API reference

Never edit `reference/` by hand. Change the doc comments in the source, then
regenerate:

```bash
# TypeScript (TypeDoc; config in typescript/typedoc.json)
cd typescript && bun run docs:api

# Python (config and layout in python/scripts/generate_api_reference.py)
cd python && uv run python scripts/generate_api_reference.py
```

CI regenerates both and fails if the committed reference is out of date.

## Writing guidelines

- Show TypeScript and Python side by side in a `<CodeGroup>`, and keep them
  equivalent.
- Use real method names, tool ids, and service slugs; the examples should run.
- Keep secrets server-side in every example; never show credentials in client
  code.
- Link between pages with root-relative paths without extensions, e.g.
  `/guides/tools`.
