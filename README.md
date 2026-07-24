# Loop Engineering Bootstrap

`loop-engineering-bootstrap` 是一个用于 AI Agent 项目初始化和升级的 Skill。
它帮助 AI 读取目标项目已有的规范文档，抽取可迁移的工程流程，并创建一套可验证、可审计、可持续演化的 `.agent` 工作层。

## 解决的问题

很多项目已经存在 `CLAUDE.md`、`README.md` 和 `docs/` 规范，但这些文件通常混合了：

- 项目业务和技术栈
- 团队协作约定
- 临时问题修复记录
- 可迁移的 Agent 工作流程

本 Skill 会先分析和分类这些内容，避免把某个项目的技术细节、服务地址、模型名称或人员分工复制到通用模板中。

## 核心功能

- 读取项目现有文档和 Agent 配置
- 抽取通用的计划、上下文、验证、评审和知识生命周期规则
- 创建或升级 `.agent` 目录
- 建立 Event -> Lesson -> Rule -> Skill -> Memory 知识生命周期
- 创建 Knowledge Index，按任务范围加载最小上下文
- 创建 Knowledge Compiler 的校验、提议、审核、应用和审计结构
- 为前端项目增加 E2E 验收门禁
- 保留项目级规范原文件，不覆盖已有内容
- 执行路径、Schema、配置引用和测试校验
- 自动识别 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、Copilot 等宿主 Agent 规则入口
- 将 `.agent` 工作协议以幂等方式接入宿主规则文件

## 生成内容

调用 Skill 后，AI 会根据目标项目的实际文件补齐以下内容。已经存在且有效的文件会保留，项目专属事实不会被复制到通用宪法中。

| 输出 | 作用 |
|---|---|
| `.agent/constitution.md` | 跨项目通用的计划、证据、评审、测试、知识和恢复原则 |
| `.agent/README.md` | Agent 每次执行任务时使用的操作入口和完整工作循环 |
| `.agent/project.md` | 项目文档入口和职责映射，不重复业务内容 |
| `.agent/config.yaml` | 项目元数据、权威文档、工作流和受保护路径配置 |
| `.agent/context/builder.yaml` | 定义上下文加载顺序、必需字段和排除内容 |
| `.agent/index/knowledge-index.yaml` | 将任务领域映射到需要读取的项目文档和 Agent 知识 |
| `.agent/state/current.yaml` | 当前任务阶段、目标、风险、下一步和验证状态 |
| `.agent/state/roadmap.yaml` | 项目级路线图和每项工作的验收条件 |
| `.agent/state/blockers.yaml` | 当前阻塞项、影响范围和解除条件 |
| `.agent/tasks/` | 任务记录模板，包含范围、计划、验收、风险和尝试次数 |
| `.agent/events/` | 不可变的任务事实、异常和执行结果 |
| `.agent/lessons/` | 从事件中提取、经过审核的经验和根因 |
| `.agent/rules/` | 可执行、可检查的项目规则 |
| `.agent/skills/` | 可复用的操作流程、输入、输出和验证方式 |
| `.agent/memory/` | 稳定的业务、架构和术语知识 |
| `.agent/decisions/` | 经过评审的项目、架构和部署决策 |
| `.agent/reviews/` | 任务、知识 Patch 和 E2E 例外的审核记录 |
| `.agent/hooks/` | 任务前、任务后、危险操作和知识更新的检查协议 |
| `.agent/requirements/` | 后端、前端、数据库、API 和部署需求模板 |
| `.agent/acceptance/` | 后端、API、测试和前端 E2E 的验收标准 |
| `.agent/schemas/` | Event、Task、Knowledge、Review、Patch、Audit 的机器校验规则 |
| `.agent/compiler/` | Knowledge Patch 的校验、提议、审核、应用和审计程序 |
| `.agent/patches/` | proposed/reviewed/applied/rejected 的知识变更状态目录 |
| `.agent/audit/` | Compiler 操作的追加式审计记录 |

## 宿主 Agent 接入

`.agent` 不会因为被创建就自动成为 Claude Code 或其他 Agent 的规则。Skill 会在生成完成后自动寻找宿主入口，并写入带有稳定标记的 Loop Engineering 协议块：

```text
<!-- LOOP-ENGINEERING:START -->
...
<!-- LOOP-ENGINEERING:END -->
```

协议块要求 Agent 在任务前读取规则和索引、创建 Task/PLAN，执行中更新状态，完成后运行测试、记录 Event、完成 Review，并通过 Compiler 更新可复用知识。重复运行 Skill 时只更新这一个区块，不会重复追加。

支持的入口包括 `CLAUDE.md`、`.claude/CLAUDE.md`、`AGENTS.md`、`.agents/AGENTS.md`、`GEMINI.md` 和 `.github/copilot-instructions.md`。Cursor 等只有目录规则的宿主需要由 AI 根据现有规则文件做等价接入。

典型目录结构如下：

```text
.agent/
├── constitution.md
├── README.md
├── config.yaml
├── context/
├── index/
├── state/
├── tasks/
├── events/
├── lessons/
├── rules/
├── skills/
├── memory/
├── decisions/
├── reviews/
├── hooks/
├── requirements/
├── acceptance/
├── schemas/
├── compiler/
└── audit/
```

其中 `.agent/constitution.md` 只保存跨项目通用的 Loop Engineering 原则；项目特有约束仍然保留在项目自己的 `docs/` 或根目录文档中。

## 调用 Skill 后是否全部自动生成

是，但需要区分“Skill 工作流”和“初始化脚本”：

1. **直接调用 Skill**：AI 会先读取项目文档，再创建或补齐上表中的 `.agent` 文件，填写项目索引、权威文档引用、状态和 E2E 要求，最后执行校验和测试。
2. **单独运行 `bootstrap_loop.py`**：脚本只创建缺失的基础骨架和目录，目的是安全初始化；它不会自行理解项目文档，也不会替 AI 编写项目相关索引、抽取报告、完整 Schema 或知识内容。
3. **已有文件**：Skill 不会覆盖有效文件，而是检查、补充缺口并报告冲突。

因此，推荐直接调用 Skill；脚本适合在需要先快速建立空目录，或其他自动化工具需要一个安全初始化步骤时使用。

## 使用方式

安装 Skill 后，在目标项目中直接提出：

> 为当前项目初始化 Loop Engineering。读取现有规范，抽取通用流程，不要复制项目专属规则，并补充前端 E2E 验收。

Skill 会先生成抽取报告，再创建缺失文件，最后运行：

```powershell
python .agent/compiler/cli.py validate
pytest .agent/tests -q
```

Skill 自带的初始化脚本也可以单独运行：

```powershell
python scripts/bootstrap_loop.py --root .
```

宿主规则接入也可以单独执行：

```powershell
python scripts/integrate_agent_entry.py --root .
```

脚本是增量式的：已存在的文件会被保留，只创建缺失文件。

## 更新方式

Skill 的更新来源是 Git 仓库。推荐使用 GitHub 作为主源，Gitee 作为国内镜像：

```powershell
# 只检查远程版本，不修改本地 Skill
python scripts/update_skill.py --target "$env:USERPROFILE/.codex/skills/loop-engineering-bootstrap"

# 使用 Gitee 检查并更新
python scripts/update_skill.py --source https://gitee.com/tigerran/loop-engineering-bootstrap.git --target "$env:USERPROFILE/.codex/skills/loop-engineering-bootstrap" --apply
```

更新脚本会先 clone 到临时目录，更新前把当前 Skill 改名为带时间戳的备份目录；复制失败时自动恢复。更新完成后需要重新启动宿主 Agent，当前会话不会自动加载新版本。

## 适用场景

- 新项目初始化 Agent 工作规范
- 将零散的项目规范整理成 Loop Engineering 系统
- 升级已有的 `.agent` 目录
- 为多个项目统一 Agent 任务、知识和评审流程
- 为前端项目补充 E2E 验收约束

## 不做什么

- 不自动覆盖项目文档
- 不修改业务源代码
- 不复制密钥、凭证、私有日志或内部思维过程
- 不把项目技术栈强行写入通用宪法
- 不在没有证据和审核的情况下自动晋升知识

## 目录说明

- `SKILL.md`：AI 使用说明和执行流程
- `README.md`：项目功能、输出文件和使用说明
- `references/`：规范抽取和输出契约
- `scripts/bootstrap_loop.py`：增量式 `.agent` 初始化脚本
- `scripts/integrate_agent_entry.py`：接入宿主 Agent 规则入口
- `scripts/update_skill.py`：检查并安全更新已安装 Skill
- `docs/install.md`：安装和初始化说明
- `docs/update.md`：更新和恢复说明
- `CHANGELOG.md`：版本变更记录
- `CONTRIBUTING.md`：贡献和发布检查
- `LICENSE`：MIT 开源许可
- `.gitignore`：排除 Python 缓存、测试缓存和打包产物
- `evals/evals.json`：Skill 评估用例

## 仓库

- GitHub: https://github.com/578281451/loop-engineering-bootstrap
- Gitee: https://gitee.com/tigerran/loop-engineering-bootstrap
