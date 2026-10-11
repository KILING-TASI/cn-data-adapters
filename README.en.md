# Research data acquisition and replay

Acquire bounded fund NAV and SSE/SZSE stock or ETF daily responses, replay frozen bytes, and normalize explicitly mapped local tables. Official-page capture is separate from a validated structured data API.

[中文说明](README.md) · [Release v0.4.2](https://github.com/KILING-TASI/cn-data-adapters/releases/tag/v0.4.2) · [Skill instructions](SKILL.md) · [Input preparation](BEGINNER.md)

Current release: **regular release**. Python **3.10+**. Base runtime dependencies: none.

## First run

Download the [complete source ZIP](https://github.com/KILING-TASI/cn-data-adapters/releases/download/v0.4.2/cn-data-adapters-v0.4.2-source.zip), extract it and enter the directory containing `try_demo.py`:

```console
python try_demo.py --no-open --out-dir reports/first-demo
```

Alternatively, clone `https://github.com/KILING-TASI/cn-data-adapters.git`, run `cd cn-data-adapters`, then execute the command above. Open the report at the path printed by the command. Teaching data is synthetic; use a new output directory and keep prior reports.

## CLI and Skill

From the source directory:

```console
python -m pip install .
cn-data-adapters --help
```

Repository and distribution: `cn-data-adapters`. Primary CLI: `cn-data-adapters`. Skill name in SKILL.md: `cn-data-adapters`. Installing the CLI does not register the Skill; configure the complete resources in an assistant that supports local Skills. Build or optional dependencies may require network access during installation.

## Scope and rights

Read the [Chinese capability boundaries](README.md#能力与边界) and [detailed commands](USAGE.md). Each tool can run independently; cross-tool calls need explicit configuration. Successful execution does not authenticate source documents, fill missing data or establish investment validity. No trade execution or guaranteed returns.

Original code uses MIT. Third-party code and documents/data retain their own licenses and rights. Default-branch documentation edits do not rewrite released archives or frozen results.

[Changes](CHANGELOG.md) · [Third-party rights](THIRD_PARTY_NOTICES.md) · [Contribution](CONTRIBUTING.md) · [Security](SECURITY.md)

[Yearbooks](YEARBOOK.md) · [Acquisition coverage](PANORAMA.md) · [Contract migration](CONTRACT_MIGRATION.md). Candidate catalogs, archived tables and numeric coverage are separate.
