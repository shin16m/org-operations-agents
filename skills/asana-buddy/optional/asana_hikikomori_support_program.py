#!/usr/bin/env python3
"""Create an Asana parent task (課題整理＋解決ストーリー) plus subtasks for hikikomori support program.

Requires after load_env_from_dotfile():
  - ASANA_TOKEN
  - Project GID: --project, or ASANA_PROJECT_ID / ASANA_PROJECT_GID / ASANA_PROJECT in .env
  - If none of the above: falls back to a known test project GID (see FALLBACK_PROJECT_GID) with stderr notice.

Windows console: progress lines use ASCII-only (gids/urls) so cp932 consoles do not fail on
Unicode punctuation in task titles. For full UTF-8 logging, set
PYTHONIOENCODING=utf-8 before running.

Idempotency: --if-not-exists skips creation when a top-level project task matches
EPIC_NAME exactly. Renamed epics in Asana or duplicate titles with different Unicode
hyphens will not match; use search in UI or API before re-running.

Usage:
  python asana_hikikomori_support_program.py --list-projects
  python asana_hikikomori_support_program.py -y
  python asana_hikikomori_support_program.py -y --project 1234567890
  python asana_hikikomori_support_program.py --dry-run -y
  python asana_hikikomori_support_program.py -y --if-not-exists
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handler_asana import create_task, get_token, load_env_from_dotfile  # noqa: E402
from asana_program_common import (  # noqa: E402
    create_subtasks_reversed,
    find_project_task_by_exact_name,
    list_accessible_projects,
    notes_from_legacy_body,
    resolve_project_with_fallback,
)

EPIC_NAME = "【ひきこもり支援2026-2027】課題整理と解決ストーリー（休息優先・非弁難）"

EPIC_NOTES = """■ 課題の整理（現状認識・支援の前提）
・一般的な定義では、仕事・就学など社会的役割を持たず、自宅等での生活が6か月以上続く状態を指すことが多い。調査・推計では15〜64歳でおよそ146万人規模といった規模感が示されることがあり、40代〜50代に相対的に多い傾向が語られることもある。
・「8050問題」（高齢の親と中高年の子の世帯）と重なるケースがあり、親の健康・経済・住まいの持続可能性が同時に論点になりやすい。
・背景は生物・心理・社会の要因が絡み合う（バイオサイコソーシャル）理解が主流であり、「怠け」や「意志の弱さ」だけで片付けない。当事者への非難は関係性と回復を損ないやすい。
・長期化しやすく、当事者だけでなく家族・地域が疲弊しやすい。支援は休息と安全を先に確保し、関係性の再構築、社会とのつながりの段階的回復、8050・家族ケアの持続可能性へと進めるストーリーが有効とされる。

■ 解決ストーリー（全体像）
【第1段階：安全・休息】
生活リズム・睡眠・栄養・暴力や自傷のリスクなど、身の安全と回復の土台を優先する。無理な外出や即時の社会復帰を迫らず、「休むこと」を正当化する。

【第2段階：関係性の再構築】
家族・近親者には心理教育と非難しない対話の訓練が有効なことが多い。専門家（医療・保健・福祉）の関与は評価・介入方針の判断に委ね、支援側は導線づくりと伴走に徹する。

【第3段階：社会接続の段階的回復】
小さな外出、短時間の対面、ピアや地域の居場所、就学・就労・日中活動への橋渡しを段階的に設計する。

【第4段階：8050／家族ケアの持続可能性】
親世代の健康・年金・貯蓄・住まい・成年後見などの論点を整理し、生活困窮や法的課題があれば専門窓口へつなぐ。外部資源（地域支援センター、精神保健福祉、生活困窮者自立支援、保健所等）と組み合わせる。

■ 主な相談・支援の窓口（地域差あり・公式情報で要確認）
・ひきこもり地域支援センター、精神保健福祉センター、生活困窮者自立支援制度に関する相談、保健所・保健センター等。
・当事者が表に出にくい「隠れひきこもり」への届き方（匿名相談、見守り、学校・職域からの相談）も設計に含める。

■ 本プロジェクトの進め方
下位タスクは柱ごとに進め、四半期ごとにKPIと前提を更新する。本メモや各タスクは医学的診断や治療指示ではない。心身の状態の評価・治療方針は必ず医師等の資格を持つ専門家に委ねる。"""


SUBTASKS: list[tuple[str, str, str]] = [
    (
        "【整理】状況の見取り図・支援マッピング（断定しない観察）",
        "当事者・家族・住環境・経済・就学就労歴を事実ベースで整理するテンプレを作る。ラベル付けや原因の断定は避け、次の一歩の選択肢を並べる。",
        "アセスメント・マッピング",
    ),
    (
        "【家族】心理教育：非難しない関わりと期待の調整",
        "責めない対話、小さな承認、境界線の例をまとめ家族向け資料の骨子を作る。必要に応じ家族支援の専門窓口をリスト化する。",
        "家族心理教育",
    ),
    (
        "【安全】休息・生活リズム・安全確保計画（回復の土台）",
        "睡眠・食事・運動・オンライン時間等の生活設計と、緊急時連絡・危険サインの共有ルールを文書化する。無理な外出強要はしない方針を明記する。",
        "休息・安全計画",
    ),
    (
        "【導線】外部紹介パス（地域支援センター・精神保健福祉・生活困窮支援・保健所）",
        "自治体差を前提に、相談先の種類・役割・持ち物目安を一覧化し、紹介文テンプレとフォロー手順を作る。",
        "外部紹介・地域包括",
    ),
    (
        "【隠れ】非顕在ケースへの届き方・匿名相談・見守り連携",
        "学校・職域・近所・配送等の接点からの気づきを扱うガイドライン草案と、プライバシーに配慮した共有ルールをまとめる。",
        "隠れひきこもり",
    ),
    (
        "【専門連携】併存する心身の困り・発達特性の整理（評価は専門家へ）",
        "支援側が行うのは困りごとの聞き取りと記録にとどめ、診断名の付与や治療方針の指示は行わない。医療・保健・福祉の専門家への委ね方を文書化する。",
        "併存課題のスクリーニング前提",
    ),
    (
        "【仲間】当事者・家族のピアと地域コミュニティ接続",
        "当事者会・家族会・地域サロン等の接続オプションを調査し、参加ハードルを下げる段階案を作る。",
        "ピア・コミュニティ",
    ),
    (
        "【段階】外出・対面関わりの段階目標（小さな成功の積み重ね）",
        "段階的目標の例（短時間・近距離・同伴可）と、後退したときの扱い方を含むプラン骨子を作る。",
        "段階的社会参加",
    ),
    (
        "【社会復帰】就学・就労・日中活動への橋渡し設計",
        "不登校支援、ジョブコーチ、就労移行、デイサービス等の選択肢を地域単位で洗い出し、遷移の分岐条件を文章化する。",
        "就学・就労の橋渡し",
    ),
    (
        "【8050】親世代の経済・老後・法的留意点の棚卸し",
        "年金・貯蓄・医療費・住居・成年後見等の確認項目をチェックリスト化し、専門家・自治体窓口への委ねどころを明記する。",
        "8050・家族ケア持続",
    ),
    (
        "【KPI】状態・負担・参加度のモニタリング指標",
        "当事者の安心感、家族のケア負担、外出頻度、相談接続数など、倫理に配慮した観測指標と更新頻度を定義する。",
        "モニタリングKPI",
    ),
    (
        "【汚名脱却】職場・学校向け理解促進メッセージ骨子",
        "「怠けではない」こと、合理的配慮・休職・復帰支援の考え方を、偏見を減らす言い回しで整理する。",
        "職場・学校の偏見対応",
    ),
    (
        "【四半期】前提見直しと次アクションのレビューテンプレ",
        "季節・家庭事件・政策情報の更新を踏まえ、目標とリスクを見直す手順を1枚にまとめる。",
        "四半期レビュー",
    ),
    (
        "【職域・学校】早期相談とつなぎ役の役割定義",
        "教員・人事・産業保健等が取るべき一歩と取るべきでない一歩を分け、専門窓口への橋渡しを標準化する。",
        "職域・教育連携",
    ),
    (
        "【生活困窮】経済的困難と支援制度の照会（自立支援等）",
        "生活困窮者自立支援制度や相談窓口の当たり方を整理し、申請に必要な情報の収集手順のみ支援側で用意する（認定判断は所管へ）。",
        "生活困窮・制度アクセス",
    ),
]


def main() -> None:
    p = argparse.ArgumentParser(description="Create hikikomori support story + subtasks in Asana")
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
        help="Print plan only; no tasks created (still loads token unless --list-projects).",
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

    project_id = resolve_project_with_fallback(args.project)

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

    create_subtasks_reversed(
        epic["gid"],
        SUBTASKS,
        token,
        notes_for_item=lambda item: notes_from_legacy_body(item[1], item[2]),
    )


if __name__ == "__main__":
    main()
