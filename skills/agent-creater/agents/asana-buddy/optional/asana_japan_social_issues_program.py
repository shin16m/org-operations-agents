#!/usr/bin/env python3
"""Create an Asana parent task (story) plus themed subtasks for Japan social issues program.

Requires after load_env_from_dotfile():
  - ASANA_TOKEN
  - Project GID: --project, or ASANA_PROJECT_ID / ASANA_PROJECT_GID / ASANA_PROJECT in .env

Windows console: progress lines after creation use ASCII-only (gids/urls) so cp932
consoles do not fail on Unicode punctuation in task titles. For full UTF-8 logging,
set PYTHONIOENCODING=utf-8 before running.

Idempotency: --if-not-exists skips creation when a top-level project task matches
EPIC_NAME exactly (same limits as inflation script).

Usage:
  python asana_japan_social_issues_program.py --list-projects
  python asana_japan_social_issues_program.py -y
  python asana_japan_social_issues_program.py -y --project 1234567890
  python asana_japan_social_issues_program.py --dry-run -y
  python asana_japan_social_issues_program.py -y --if-not-exists
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

# Same-directory import when run as script
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import (  # noqa: E402
    ASANA_BASE,
    create_task,
    get_token,
    load_env_from_dotfile,
)


def resolve_project_id(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for key in ("ASANA_PROJECT_ID", "ASANA_PROJECT_GID", "ASANA_PROJECT"):
        v = os.getenv(key)
        if v:
            return v.strip()
    return None


def find_project_task_by_exact_name(project_gid: str, name: str, token: str) -> str | None:
    """Return task gid if a task in the project has exactly this name, else None."""
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
    print("利用可能なプロジェクト（アーカイブ除く）:\n")
    for w in workspaces:
        wgid, wname = w["gid"], w.get("name", "")
        pr = requests.get(
            f"{ASANA_BASE}/projects",
            params={"workspace": wgid, "opt_fields": "name,gid,archived", "limit": 100},
            headers=headers,
        )
        pr.raise_for_status()
        rows = [x for x in pr.json()["data"] if not x.get("archived")]
        print(f"ワークスペース: {wname} ({wgid}) — {len(rows)} 件")
        for p in rows:
            print(f"  {p['gid']}\t{p.get('name', '')}")
        print()


def create_subtask(parent_gid: str, name: str, notes: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"data": {"name": name, "notes": notes, "parent": parent_gid}}
    r = requests.post(f"{ASANA_BASE}/tasks", json=payload, headers=headers)
    r.raise_for_status()
    return r.json()["data"]


EPIC_NAME = "【日本の社会課題】統合ストーリーとワークストリーム（少子高齢化起点の連鎖課題）"

EPIC_NOTES = """■ 前提（根）
急速な少子高齢化・人口減少が根幹にあり、労働力不足・社会保障費増大・地方過疎が連鎖する。貧困・格差固定化、環境、災害、教育・DX遅れも同時に進み、相互に強化し合う。

■ 解決に向けたストーリー（3幕構成）
【第1幕：見える化と優先順位】
連鎖構造を一枚の因果マップに落とし、地域・組織ごとの「今いちばん効くレバー」を定量・定性で並べる。国のデジタル田園都市国家構想やSDGs/サステナ事業と接続し、打ち手のポートフォリオを決める。

【第2幕：地域と働き方の両立】
一極集中と過疎のトレードオフを前提に、リモート・移住・二拠点、介護と仕事の両立、非正規格差と生産性の改善をセットで設計する。デジタルデバイド解消を横串に入れ、誰も取り残さない導線を作る。

【第3幕：次世代とレジリエンス】
子どもの貧困・教育格差、メンタルヘルス・孤立（いじめ・不登校・ヤングケアラー等）に投資しつつ、食品ロス・海洋プラスチック・気候変動と、地震・台風激甚化に耐えるBCPを並走させる。行政DXとインフラ老朽化対策で社会システムの耐久性を上げる。

■ 本プロジェクトの進め方
下位タスクをテーマ別に進行し、四半期ごとに因果マップとKPIを更新する。"""


SUBTASKS: list[tuple[str, str, str]] = [
    (
        "【1 人口・地域】生産年齢人口×社会保障のシナリオとKPI",
        "年金・医療・介護の逼迫と労働力不足をつなぐシナリオ（悲観・中立・楽観）を整理し、監視KPIを定義する。",
        "人口構造・地域",
    ),
    (
        "【1 人口・地域】過疎・一極集中の可視化とダッシュボード要件",
        "人口移動・産業・税財源などのデータソースを洗い出し、意思決定用の可視化要件をまとめる。",
        "人口構造・地域",
    ),
    (
        "【1 人口・地域】独居高齢・介護離職のヒアリングと支援メニュー案",
        "当事者・自治体・事業者ヒアリング計画を立て、孤立防止と離職防止の支援パッケージ案を作る。",
        "人口構造・地域",
    ),
    (
        "【2 経済・働き方】子どもの貧困・ひとり親の施策マップ",
        "公的支援と民間プログラムを整理し、申請漏れ・情報到達のボトルネックを特定する。",
        "経済・働き方・格差",
    ),
    (
        "【2 経済・働き方】デジタルデバイドのターゲット定義と伴走設計",
        "対象者像・チャネル・支援オペレーションを定義し、固定化を防ぐ伴走モデルを草案する。",
        "経済・働き方・格差",
    ),
    (
        "【2 経済・働き方】長時間労働・非正規格差・生産性の論点整理",
        "過労リスク、賃金格差、生産性指標を関連付けてガイドライン初稿を作る。",
        "経済・働き方・格差",
    ),
    (
        "【2 経済・働き方】ジェンダー平等の現状調査（管理職・育児・賃金）",
        "女性管理職比率、家事育児負担、男女賃金格差の内部/外部ベンチを取り、改善テーマを列挙する。",
        "経済・働き方・格差",
    ),
    (
        "【3 社会・環境・安全】メンタルヘルス・孤立の連携マップ",
        "いじめ・不登校・若年自殺・ヤングケアラー等について学校・医療・NPOとの連携候補をリスト化する。",
        "社会・環境・安全",
    ),
    (
        "【3 社会・環境・安全】食品ロス・海洋プラスチック・気候の施策案",
        "事業・地域レベルで実行可能なアクションメニューと測定指標のたたき台を作る。",
        "社会・環境・安全",
    ),
    (
        "【3 社会・環境・安全】災害BCPと激甚化想定の訓練シナリオ更新",
        "地震・台風等の想定被害と復旧優先度を見直し、訓練シナリオを更新する。",
        "社会・環境・安全",
    ),
    (
        "【4 教育・システム】教育格差是正プログラムの調査",
        "家庭経済と学習機会のギャップを埋める奨学金・学習支援・塾外活動等のベストプラクティスを調査する。",
        "教育・社会システム",
    ),
    (
        "【4 教育・システム】インフラ老朽化×行政DXの優先投資リスト",
        "社会インフラのリスクとDX施策をマトリクスし、優先順位のたたき台を作る。",
        "教育・社会システム",
    ),
    (
        "【横串】SDGs／サステナ事業ポートフォリオとKPI整合",
        "事業ポートフォリオをSDGs目標にマッピングし、重複とギャップを整理する。",
        "横串",
    ),
    (
        "【横串】国策（例：デジタル田園都市国家）と自組織施策のギャップ分析",
        "政策トレンドと自社/自組織の施策を対照し、追加で取るべきテーマを抽出する。",
        "横串",
    ),
]


def main() -> None:
    p = argparse.ArgumentParser(description="Create Japan social issues story + subtasks in Asana")
    p.add_argument("--project", default=None, help="Asana project GID (default: ASANA_PROJECT_ID env)")
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation before creating tasks.",
    )
    p.add_argument(
        "--list-projects",
        action="store_true",
        help="List accessible project GIDs and exit.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan only; no tasks created.",
    )
    p.add_argument(
        "--if-not-exists",
        action="store_true",
        help="If a top-level task in the project already has EPIC_NAME exactly, exit 0 without creating.",
    )
    args = p.parse_args()

    load_env_from_dotfile()
    token = get_token()

    if args.list_projects:
        list_accessible_projects(token)
        return

    project_id = resolve_project_id(args.project)
    if not project_id:
        print(
            "エラー: プロジェクトGIDがありません。--project を指定するか、"
            ".env に ASANA_PROJECT_ID（または ASANA_PROJECT_GID / ASANA_PROJECT）を設定してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.if_not_exists:
        existing = find_project_task_by_exact_name(project_id, EPIC_NAME, token)
        if existing:
            print(f"skip: epic already exists gid={existing} (exact name match)")
            return

    if args.dry_run:
        print(
            f"dry-run: would create 1 parent + {len(SUBTASKS)} subtasks "
            f"in project_gid={project_id}"
        )
        return

    if not args.yes:
        print(f"親タスク1件＋子タスク{len(SUBTASKS)}件をプロジェクト {project_id} に作成します。よいですか？ (y/N): ", end="")
        if input().strip().lower() != "y":
            print("中止します。")
            sys.exit(0)

    epic = create_task(project_id, EPIC_NAME, EPIC_NOTES, token)
    print("created_parent", epic.get("gid"), epic.get("permalink_url", ""))

    # Asana のサブタスク一覧は「後から作ったものが上」に並ぶことが多い。
    # 上から順に消化したいときは SUBTASKS の先頭が画面上で最上段になるよう、
    # 作成順をリストの逆にして最後に先頭要素を作る。
    for title, body, pillar in reversed(SUBTASKS):
        notes = f"柱: {pillar}\n\n{body}"
        sub = create_subtask(epic["gid"], title, notes, token)
        print("created_subtask", sub.get("gid"))


if __name__ == "__main__":
    main()
