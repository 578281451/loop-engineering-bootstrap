from __future__ import annotations

import argparse
from pathlib import Path


START = "<!-- LOOP-ENGINEERING:START -->"
END = "<!-- LOOP-ENGINEERING:END -->"
BRIDGE = f"""{START}
## Loop Engineering 工作协议

本项目使用 `.agent/` 作为 Agent 的任务、状态、知识和验证工作层。它不是可选参考文档。

每次任务开始前：
1. 读取 `.agent/constitution.md`、`.agent/README.md` 和 `.agent/state/current.yaml`。
2. 查询 `.agent/index/knowledge-index.yaml`，只加载与任务相关的规则、决策、技能和验收标准。
3. 创建 `.agent/tasks/TASK-*.yaml` 和 PLAN，明确范围、风险、验收和验证命令。

任务执行中：更新 current state；保持项目规则和 `.agent` 规则一致；不要直接修改受保护知识。

任务结束时：运行相关测试和 E2E，记录命令与结果，追加 Event，完成 Review；可复用知识必须通过 Knowledge Patch 和 Compiler 更新。

先完成上述流程，再报告任务完成。规则入口由 Loop Engineering Skill 自动维护。
{END}"""


ADAPTERS = (
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    "AGENTS.md",
    ".agents/AGENTS.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
)


def find_entries(root: Path) -> list[Path]:
    return [root / path for path in ADAPTERS if (root / path).is_file()]


def integrate(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if START in text and END in text:
        before = text[: text.index(START)]
        after = text[text.index(END) + len(END) :]
        updated = before.rstrip() + "\n\n" + BRIDGE + after
    else:
        updated = text.rstrip() + "\n\n" + BRIDGE + "\n"
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return "updated"
    return "unchanged"


def main() -> int:
    parser = argparse.ArgumentParser(description="Integrate .agent into host-agent instructions.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    entries = find_entries(root)
    if not entries:
        print("no known host instruction entry found; create one only with user approval")
        return 0
    for entry in entries:
        print(f"{entry.relative_to(root)}: {integrate(entry)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
