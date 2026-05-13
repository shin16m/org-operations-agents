#!/usr/bin/env python3
"""Create parent + subtasks for AI agent adoption barriers (issue-story-planner handoff).

Handoff-aligned notes: subtask bodies use ## 背景 / ## 概要 / ## 完了条件; pillar is prefixed as 柱:.

Usage:
  python asana_ai_agent_adoption_program.py --list-projects
  python asana_ai_agent_adoption_program.py -y --dry-run
  python asana_ai_agent_adoption_program.py -y --if-not-exists
  python asana_ai_agent_adoption_program.py -y --project <GID>
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import (  # noqa: E402
    ASANA_BASE,
    create_task,
    get_token,
    load_env_from_dotfile,
)

FALLBACK_PROJECT_GID = "1214771428861230"


def resolve_project_id(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for key in ("ASANA_PROJECT_ID", "ASANA_PROJECT_GID", "ASANA_PROJECT"):
        v = os.getenv(key)
        if v:
            return v.strip()
    return None


def find_project_task_by_exact_name(project_gid: str, name: str, token: str) -> str | None:
    headers = {"Authorization": f"Bearer {token}"}
    url: str | None = f"{ASANA_BASE}/projects/{project_gid}/tasks"
    params: dict[str, str | int] = {"opt_fields": "name,gid", "limit": 100}
    while url:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        body = r.json()
        for t in body.get("data") or []:
            if (t.get("name") or "") == name:
                return str(t["gid"])
        next_page = body.get("next_page") or {}
        url = next_page.get("uri")
        params = {}
    return None


def list_accessible_projects(token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(
        f"{ASANA_BASE}/users/me",
        params={"opt_fields": "workspaces.gid,workspaces.name"},
        headers=headers,
    )
    r.raise_for_status()
    workspaces = r.json()["data"].get("workspaces") or []
    print("projects (non-archived):\n")
    for w in workspaces:
        wgid, wname = w["gid"], w.get("name", "")
        pr = requests.get(
            f"{ASANA_BASE}/projects",
            params={"workspace": wgid, "opt_fields": "name,gid,archived", "limit": 100},
            headers=headers,
        )
        pr.raise_for_status()
        rows = [x for x in pr.json()["data"] if not x.get("archived")]
        print(f"workspace: {wname} ({wgid}) count={len(rows)}")
        for p in rows:
            print(f"  {p['gid']}\t{p.get('name', '')}")
        print()


def create_subtask(parent_gid: str, name: str, notes: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": {"name": name, "notes": notes, "parent": parent_gid}}
    r = requests.post(f"{ASANA_BASE}/tasks", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()["data"]


EPIC_NAME = "【普及阻害要因】AIエージェントの技術・組織・信頼性の整理と対策ストーリー"

EPIC_NOTES = """■ 課題点の整理（現状認識）
- 技術・実用: 誤情報（ハルシネーション）リスク、判断プロセスのブラックボックス化、学習データ外の最新情報への弱さ、複雑・非定型業務での自律実行の限界。
- 組織・運用: ソフトウェア・データの未統合（サイロ化）、導入コストと専門人材不足、補助ツールとしてのガイドライン・ガバナンス未整備。
- セキュリティ・信頼: 機密データを扱う際の漏えい・不正アクセスリスク、公平性・バイアス等の倫理的精査の必要性。

■ 解決ストーリー（全体像）
1) 利用境界を先に固定し、人間の承認・検証点（human-in-the-loop）を明文化する。
2) データとツールの接続地図を作り、エージェントが参照してよい情報源と禁止領域を揃える。
3) 運用で効く信頼対策（出力検証、根拠の出し方、エスカレーション）をパイロットに載せる。
4) 判断ログと説明可能性の要件を満たす設計にし、監査・再現に耐える形にする。
5) 知識更新（公式ドキュメント、法改正、社内ナレッジ）の取り込み方針を決める。
6) セキュリティ・データ分類に基づく利用ポリシーを整備する。
7) 人材・学習・支援体制を現実的な計画に落とす。
8) パイロットの KPI・撤退条件で拡張可否を評価する。

■ 本バンドルの進め方
- 子タスクは着手順で並べている。Asana 投入時は API の表示慣習に合わせ逆順で作成する。
- 各子の notes は issue-story-planner v1.1 準拠（背景・概要・完了条件の見出し連結）。"""


SUBTASKS: list[tuple[str, str, str]] = [
    (
        "【ガバナンス】利用シナリオと human-in-the-loop 境界の明文化",
        """## 背景
普及が進まない背景の一つに、エージェントに任せる範囲と人が必ず介在すべき点が曖昧なまま導入が進み、事故・不信につながるリスクがある。

## 概要
対象業務を列挙し、自動化・提案のみ・人の承認必須などの段階分類と、エスカレーション条件を1枚にまとめる。

## 完了条件
利用境界の表（業務×自動化レベル×承認者）がレビュー可能な形で共有され、ステークホルダーから「運用に載せられる」合意が得られている。""",
        "ガバナンス",
    ),
    (
        "【連携】既存システム・データの接続可否マップ（サイロ可視化）",
        """## 背景
データがサイロ化しているとエージェントが参照できず、価値が出ない／無理な連携でセキュリティリスクが増える、の両方が起きやすい。

## 概要
主要システム・データストア・API・権限境界を洗い出し、エージェントが読み書き可能な範囲を仮置きしたマップを作る。

## 完了条件
システム一覧とデータの所在、参照可否（読取/書込/禁止）、オーナー、次アクション（連携要否）が表形式で揃っている。""",
        "データ・統合",
    ),
    (
        "【信頼性】出力検証と根拠提示の運用ルール（ハルシネーション対策）",
        """## 背景
正確性が100%保証されない前提で、誤情報をそのまま業務判断に使うと損害・コンプライアンス問題になり得る。

## 概要
業務カテゴリ別に、必須の検証ステップ（二次確認、公式ソース照合、人の承認）と、ユーザー向けの注意文言を定義する。

## 完了条件
検証チェックリストと承認フローが文書化され、少なくとも1つのパイロット業務に適用できる状態になっている。""",
        "信頼性・運用",
    ),
    (
        "【信頼性】判断ログと説明可能性の要件定義（ブラックボックス対策）",
        """## 背景
結論の根拠が追えないと、監査・インシデント対応・改善ができず、組織としての採用が進みにくい。

## 概要
保持すべきログ項目（入力要約、参照した知識源、ツール呼出、モデル/プロンプト版）と保存期間・閲覧権限の要件案を書く。

## 完了条件
要件が箇条書きで固まり、技術検討（実装方式は別タスク）に渡せるレビュー用ドキュメントになっている。""",
        "信頼性・監査",
    ),
    (
        "【技術】最新情報・社内ナレッジの取り込み方針（RAG/ツール連携の整理）",
        """## 背景
学習データにない情報に弱い点は、ツール連携や検索拡張で緩和できる一方、コストと鮮度・権限管理が課題になる。

## 概要
優先する情報源（公式、社内Wiki、チケット等）と更新頻度、参照時の権限チェックの考え方を整理する。

## 完了条件
情報源リストと優先順位、更新オーナー、パイロットで試す最小構成が決まっている。""",
        "技術",
    ),
    (
        "【セキュリティ】データ分類とエージェント利用ポリシー草案",
        """## 背景
機密を扱うほど、漏えい・誤送信・過剰な学習利用のリスクが増え、明文化されたポリシーなしに運用できない。

## 概要
データ分類（公開/社内限定/個人情報/機密等）ごとに、エージェントへの投入可否・マスキング・保管をルール化する草案を作る。

## 完了条件
分類×許可操作のマトリクスが1枚あり、法務・セキュリティレビューに回せるドラフトになっている。""",
        "セキュリティ",
    ),
    (
        "【組織】スキルギャップと学習・支援体制の整理（導入コストの見える化）",
        """## 背景
構築・運用に高度スキルが必要な印象が、現場の諦めや外注依存だけに偏ると持続可能にならない。

## 概要
必要スキル（データ、ML/LLM、アプリ連携、セキュリティ）をタスク単位に分解し、内製/研修/パートナーの割当案と概算工数を出す。

## 完了条件
ロール別のスキルマップと90日の学習・支援計画のたたき台が共有されている。""",
        "組織・人材",
    ),
    (
        "【横串】パイロット計画と KPI・撤退条件の合意",
        """## 背景
課題が多面的なため、一度に全面展開すると失敗が見えにくく、学習が回らない。小さく測る必要がある。

## 概要
対象業務・期間・成功指標（品質、時間、インシデント件数等）と、継続/縮小/中止の条件を定義し合意形成する。

## 完了条件
パイロットのスコープ文書に KPI と撤退条件が明記され、承認者が割り当てられている。""",
        "横串",
    ),
]


def main() -> None:
    p = argparse.ArgumentParser(description="Create AI agent adoption epic + subtasks in Asana")
    p.add_argument("--project", default=None, help="Asana project GID (default: ASANA_PROJECT_* env)")
    p.add_argument("-y", "--yes", action="store_true", help="Skip confirmation before creating tasks.")
    p.add_argument("--list-projects", action="store_true", help="List accessible project GIDs and exit.")
    p.add_argument("--dry-run", action="store_true", help="Print plan only; no tasks created.")
    p.add_argument(
        "--if-not-exists",
        action="store_true",
        help="If a top-level project task matches EPIC_NAME exactly, exit without creating.",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if args.list_projects:
        list_accessible_projects(token)
        return

    project_id = resolve_project_id(args.project)
    if not project_id:
        project_id = FALLBACK_PROJECT_GID
        print(
            f"warn: using fallback project_gid={FALLBACK_PROJECT_GID} "
            "(set ASANA_PROJECT_ID or pass --project)",
            file=sys.stderr,
        )

    if args.if_not_exists:
        existing = find_project_task_by_exact_name(project_id, EPIC_NAME, token)
        if existing:
            print(f"skip: epic already exists gid={existing}")
            return

    if args.dry_run:
        print(f"dry-run: 1 parent + {len(SUBTASKS)} subtasks project_gid={project_id}")
        return

    if not args.yes:
        print(f"Create 1 parent + {len(SUBTASKS)} subtasks in {project_id}? (y/N): ", end="")
        if input().strip().lower() != "y":
            print("aborted.")
            sys.exit(0)

    epic = create_task(project_id, EPIC_NAME, EPIC_NOTES, token)
    print("created_parent", epic.get("gid"), epic.get("permalink_url", ""))

    for title, body, pillar in reversed(SUBTASKS):
        notes = f"柱: {pillar}\n\n{body}"
        sub = create_subtask(epic["gid"], title, notes, token)
        print("created_subtask", sub.get("gid"))


if __name__ == "__main__":
    main()
