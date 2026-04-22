#!/usr/bin/env python3
"""Compatibility wrapper around the unified DFZR pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

import novel_pipeline


def handle_init(args: argparse.Namespace) -> int:
    return novel_pipeline.init_project(args.project_name, args.target_dir, args.mode, args.force)


def handle_prepare_chapter(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_path).expanduser().resolve()
    novel_pipeline.prepare_chapter(
        project_dir,
        args.chapter_num,
        args.chapter_title,
        force=args.force,
    )
    print(f"项目目录: {project_dir}")
    print(f"章节: {novel_pipeline.chapter_label(args.chapter_num)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold novel project files and chapter runtime files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="初始化小说项目目录")
    init_parser.add_argument("project_name", help="项目名")
    init_parser.add_argument("--target-dir", default=".", help="项目创建目录，默认当前目录")
    init_parser.add_argument("--mode", choices=tuple(novel_pipeline.MODE_LABELS), default="single", help="项目结构模式")
    init_parser.add_argument("--force", action="store_true", help="覆盖已有模板文件")
    init_parser.set_defaults(handler=handle_init)

    chapter_parser = subparsers.add_parser("prepare-chapter", help="创建章节过程文件和正文壳子")
    chapter_parser.add_argument("project_path", help="项目根目录")
    chapter_parser.add_argument("--chapter-num", type=int, required=True, help="章节号")
    chapter_parser.add_argument("--chapter-title", default="未命名章节", help="章节标题")
    chapter_parser.add_argument("--force", action="store_true", help="覆盖已有文件")
    chapter_parser.set_defaults(handler=handle_prepare_chapter)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
