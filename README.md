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

## 生成内容

典型输出包括：

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

脚本是增量式的：已存在的文件会被保留，只创建缺失文件。

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
- `references/`：规范抽取和输出契约
- `scripts/bootstrap_loop.py`：增量式 `.agent` 初始化脚本
- `evals/evals.json`：Skill 评估用例

## 仓库

- GitHub: https://github.com/578281451/loop-engineering-bootstrap
- Gitee: https://gitee.com/tigerran/loop-engineering-bootstrap
