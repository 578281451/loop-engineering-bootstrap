# Installation

## Install From GitHub

Install the Skill into the host Agent's Skill directory by using the host's
normal GitHub Skill installer:

```text
https://github.com/578281451/loop-engineering-bootstrap/tree/main
```

If the installer accepts a repository instead of a tree URL, use:

```text
578281451/loop-engineering-bootstrap
```

## Install From Gitee

Use the Gitee mirror when GitHub is unavailable:

```text
https://gitee.com/tigerran/loop-engineering-bootstrap.git
```

## Verify

After installation, confirm the directory contains `SKILL.md`, `README.md`,
`references/`, `scripts/`, and `evals/`. Restart the host Agent before using
the Skill so it reloads the available Skill list.

## Initialize A Project

Ask the Agent:

> Initialize Loop Engineering for this project. Read the existing rules first,
> extract portable process rules, integrate the host instruction entry, create
> the `.agent` layer, and validate the result.
