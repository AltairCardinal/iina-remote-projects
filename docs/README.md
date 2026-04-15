# 文档目录

这里存放散落在各子项目中的原始开发文档，整理自 `iina-remote/` 原始目录。

## 文档清单

| 文档 | 来源 | 说明 |
|------|------|------|
| `SPEC.md` | `iina-remote/SPEC.md` | 完整功能规格说明 |
| `CONTROL_METHODS.md` | `iina-remote/CONTROL_METHODS.md` | IINA 控制方法（AppleScript + HTTP IPC） |
| `IMPLEMENTATION_PLAN.md` | `iina-remote/IMPLEMENTATION_PLAN.md` | 开发实施计划 |
| `PROGRESS.md` | `iina-remote/PROGRESS.md` | 开发进度记录 |
| `DEPLOY.md` | `iina-remote/DEPLOY.md` | 部署指南 |
| `ROADMAP.md` | `iina-remote/ROADMAP.md` | 项目路线图 |

## 阅读顺序建议

接手项目的开发者推荐阅读顺序：

1. `SPEC.md` — 了解 IINA Remote 要做什么
2. `ARCHITECTURE.md` — 了解整体技术架构（如果没有，请参考 `server/README.md` 和各子项目 README）
3. `IMPLEMENTATION_PLAN.md` — 了解实施计划和时间线
4. `PROGRESS.md` — 了解已完成和进行中的工作
5. `CONTROL_METHODS.md` — 了解 IINA 的控制方式（这对理解 server 的 playback handler 很重要）
