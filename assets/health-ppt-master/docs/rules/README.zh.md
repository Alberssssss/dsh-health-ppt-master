# 项目规则

[English](README.md) | 中文

本目录面向在此仓库中工作的贡献者与 AI agent，提供约定和风格指南。这些规则源于现有代码与参考文档中的实际惯例。

| 规则 | 范围 |
|---|---|
| [`prompt-style.md`](./prompt-style.md) | `skills/ppt-master/references/` 下文件的风格指南，包括语气、分节、表格优先和禁用模式 |
| [`code-style.md`](./code-style.md) | `skills/ppt-master/scripts/` 下 Python 文件的风格指南，包括文件头、导入、CLI 入口、错误处理和无测试规则 |

新增规则文件时：

- 每个文件只讨论一个主题
- 文件名采用 `<topic>.md`（小写，使用连字符）
- 在上表中新增一行
- 正文应当是**规范性，而非描述性**的：告诉读者应当怎么做，而不是描述项目碰巧是什么样子
