<div align="center">

<img src="assets/ani2xcur_icon.png" width="200" height="200" alt="Ani2xcur CLI">

# Ani2xcur CLI

_✨一站式鼠标指针转换与管理工具_
  <p align="center">
    <a href="https://github.com/licyk/ani2xcur-cli/stargazers" style="margin: 2px;">
      <img src="https://img.shields.io/github/stars/licyk/ani2xcur-cli?style=flat&logo=github&logoColor=silver&color=bluegreen&labelColor=grey" alt="Stars">
    </a>
    <a href="https://github.com/licyk/ani2xcur-cli/forks" style="margin: 2px;">
      <img src="https://img.shields.io/github/forks/licyk/ani2xcur-cli?style=flat&logo=github&logoColor=silver&color=bluegreen&labelColor=grey" alt="GitHub forks">
    </a>
    <a href="https://github.com/licyk/ani2xcur-cli/issues" style="margin: 2px;">
      <img src="https://img.shields.io/github/issues/licyk/ani2xcur-cli?style=flat&logo=github&logoColor=silver&color=bluegreen&labelColor=grey" alt="Issues">
    </a>
    <a href="https://github.com/licyk/ani2xcur-cli/commits/main" style="margin: 2px;">
      <img src="https://flat.badgen.net/github/last-commit/licyk/ani2xcur-cli/main?icon=github&color=green&label=last%20commit" alt="Commit">
    </a>
    <a href="https://github.com/licyk/ani2xcur-cli/actions/workflows/lint.yml" style="margin: 2px;">
      <img src="https://github.com/licyk/ani2xcur-cli/actions/workflows/lint.yml/badge.svg" alt="Ruff Lint">
    </a>
    <a href="https://github.com/licyk/ani2xcur-cli/actions/workflows/release.yml" style="margin: 2px;">
      <img src="https://github.com/licyk/ani2xcur-cli/actions/workflows/release.yml/badge.svg" alt="Release">
    </a>
    <a href="https://github.com/licyk/ani2xcur-cli/releases" style="margin: 2px;">
      <img src="https://img.shields.io/github/v/release/licyk/ani2xcur-cli?include_prereleases" alt="Release">
    </a>
    <a href="https://pypi.org/project/ani2xcur" style="margin: 2px;">
      <img src="https://img.shields.io/pypi/v/ani2xcur" alt="PyPI">
    </a>
    <a href="https://pypi.org/project/ani2xcur" style="margin: 2px;">
      <img src="https://img.shields.io/pypi/pyversions/ani2xcur.svg" alt="Python Version">
    </a>
  </p>

</div>

- [Ani2xcur CLI](#ani2xcur-cli)
- [简介](#简介)
- [功能特性](#功能特性)
- [安装](#安装)
- [使用](#使用)
  - [鼠标指针格式转换](#鼠标指针格式转换)
    - [Windows 转 Linux](#windows-转-linux)
    - [Linux 转 Windows](#linux-转-windows)
  - [鼠标指针管理](#鼠标指针管理)
    - [安装指针](#安装指针)
    - [卸载指针](#卸载指针)
    - [设置指针主题和大小](#设置指针主题和大小)
    - [查看指针信息](#查看指针信息)
    - [导出指针](#导出指针)
  - [ImageMagick 管理](#imagemagick-管理)
    - [自动下载并安装 ImageMagick](#自动下载并安装-imagemagick)
    - [从系统中卸载 ImageMagick](#从系统中卸载-imagemagick)
  - [更新 Ani2xcur CLI](#更新-ani2xcur-cli)
  - [查看 Ani2xcur CLI 使用的环境变量](#查看-ani2xcur-cli-使用的环境变量)
  - [查看 Ani2xcur CLI 版本信息](#查看-ani2xcur-cli-版本信息)
- [使用的项目](#使用的项目)
- [许可证](#许可证)

***

# 简介
Ani2xcur CLI 是一个强大且易于使用的命令行工具，专为鼠标指针主题的管理、转换和安装而设计，支持 Windows 平台与 Linux 平台。


# 功能特性
- **跨平台支持**: 完美兼容 Windows 和主流 Linux 桌面环境。
- **格式转换**:
  - 将 Windows 鼠标指针主题 (`.inf`, `.ani`, `.cur`) 转换为 Linux X11 格式。
  - 将 Linux X11 鼠标指针主题 (`index.theme`) 转换为 Windows 格式。
- **指针管理**:
  - **安装**: 轻松将本地或压缩包中的指针主题安装到系统中。
  - **卸载**: 按名称移除已安装的指针主题。
  - **设置**: 一键应用系统中的指针主题和调整指针大小。
  - **查看**: 列出所有已安装的指针主题，并显示当前使用的主题和大小。
  - **导出**: 将系统中的指针主题导出为文件，方便备份和分享。
- **智能识别**: 自动在压缩包或目录中查找指针配置文件 (`.inf` 或 `index.theme`)。
- **依赖管理**: 内置 ImageMagick 安装和卸载功能，简化转换前的准备工作。


# 安装
确保您的系统已安装 [Python](https://www.python.org) 3.10+。

```bash
pip install ani2xcur
```


# 使用
Ani2xcur CLI 提供了丰富的子命令来满足不同需求。可使用`--help`查看可用的命令。

```bash
ani2xcur --help
```


## 鼠标指针格式转换
Windows 鼠标指针主题和 Linux 鼠标指针主题并不能互相兼容，而 Ani2xcur CLI 可以将鼠标指针主题文件转换为对应平台的文件。

鼠标指针主题的转换功能依赖 [ImageMagick](https://imagemagick.org)，使用转换功能前需要安装 ImageMagick，而 Ani2xcur CLI 提供一键安装命令。

```bash
ani2xcur imagemagick install
```


### Windows 转 Linux
将 Windows 指针主题转换为 Linux X11 格式。

```bash
ani2xcur convert win2x <Windows 指针路径或者是鼠标指针压缩包下载链接>
```

- **高级选项**:
  - `--output-path <路径>`: 保存转换后的鼠标指针路径。
  - `--shadow`: 是否模拟 Windows 的阴影效果。
  - `--shadow-opacity <不透明度>`: 阴影的不透明度 (0 到 255)。
  - `--shadow-radius <分数值>`: 阴影模糊效果的半径 (宽度的分数值)。
  - `--shadow-sigma <分数值>`: 阴影模糊效果的西格玛值 (宽度的分数值)。
  - `--shadow-x <偏移量>`: 阴影的 x 偏移量 (宽度的分数值)。
  - `--shadow-y <偏移量>`: 阴影的 y 偏移量 (宽度的分数值)。
  - `--shadow-color`: 阴影的颜色 (十六进制颜色格式)。
  - `--scale <倍数>`: 按指定倍数缩放光标。
  - `--compress`: 转换完成后将鼠标指针打包成压缩包。
  - `--compress-format <压缩包格式>`: 打包成压缩包时使用的压缩包格式 (`.zip`|`.7z`|`.rar`|`.tar`|`.tar.Z`|`.tar.lz`|`.tar.lzma`|`.tar.bz2`|`.tar.7z`|`.tar.gz`|`.tar.xz`|`.tar.zst`)。


### Linux 转 Windows
将 Linux X11 指针主题转换为 Windows 格式。

```bash
ani2xcur convert x2win <Linux 指针路径或者是鼠标指针压缩包下载链接>
```

- **高级选项**:
  - `--output-path <路径>`: 保存转换后的鼠标指针路径。
  - `--scale <倍数>`: 按指定倍数缩放光标。
  - `--compress`: 转换完成后将鼠标指针打包成压缩包。
  - `--compress-format <压缩包格式>`: 打包成压缩包时使用的压缩包格式 (`.zip`|`.7z`|`.rar`|`.tar`|`.tar.Z`|`.tar.lz`|`.tar.lzma`|`.tar.bz2`|`.tar.7z`|`.tar.gz`|`.tar.xz`|`.tar.zst`)。


## 鼠标指针管理

### 安装指针
从本地路径（压缩包、`.inf` 文件或 `index.theme` 文件）安装指针主题。

```bash
ani2xcur cursor install <指针路径>
```

- **高级选项**:
  - `--install-path <安装路径>`: 自定义鼠标指针文件安装路径, 默认为鼠标指针配置文件中指定的安装路径。
  - `--use-inf-config-path`: (仅 Windows 平台) 使用 INF 配置文件中的鼠标指针安装路径。


### 卸载指针
按名称删除一个已安装的指针主题。

```bash
ani2xcur cursor uninstall <指针名称>
```


### 设置指针主题和大小
设置当前系统指针主题。

```bash
ani2xcur cursor set theme <指针名称>
```

设置指针大小。
```bash
ani2xcur cursor set size <大小值>
```

- **指针默认大小值**: 
  - Windows 系统中为`1`。
  - Linux 系统中为`24`。


### 查看指针信息
列出系统中所有已安装的指针。

```bash
ani2xcur cursor list
```

显示当前正在使用的指针主题和大小。

```bash
ani2xcur cursor status
```


### 导出指针
将已安装的指针导出到指定目录。

```bash
ani2xcur cursor export <指针名称> <导出路径>
```

- **高级选项**: 
  - `--custom-install-path <路径>`: 自定义鼠标指针配置文件在安装时的文件安装路径。


## ImageMagick 管理
Ani2xcur CLI 依赖 ImageMagick 进行指针转换。可以使用以下命令来管理它。

### 自动下载并安装 ImageMagick
```bash
ani2xcur imagemagick install
```

- **高级选项**:
  - `--install-path <安装路径>`: (仅 Windows 平台) 自定义安装 ImageMagick 的目录。
  - `-y`|`--yes`: 直接确认安装。


### 从系统中卸载 ImageMagick
```bash
ani2xcur imagemagick uninstall
```

- **高级选项**:
  - `-y`|`--yes`: 直接确认卸载。


## 更新 Ani2xcur CLI
```bash
ani2xcur update
```

- **高级选项**:
  - `--install-from-source`: 更新时是否从源码进行安装。
  - `--ani2xcur-source <Git 仓库链接>`: Ani2xcur 源仓库的 Git 链接。
  - `--win2xcur-source <Git 仓库链接>`: Win2xcur 源仓库的 Git 链接。


## 查看 Ani2xcur CLI 使用的环境变量
```bash
ani2xcur env
```


## 查看 Ani2xcur CLI 版本信息
```bash
ani2xcur version
```


# 使用的项目
- [Win2xcur](https://github.com/quantum5/win2xcur): 转换核心。
- [Breeze cursor](https://store.kde.org/p/999927): 鼠标指针补全文件。


# 许可证
- [GPL-3.0](LICENSE)
