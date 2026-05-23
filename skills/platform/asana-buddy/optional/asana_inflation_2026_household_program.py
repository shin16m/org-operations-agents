#!/usr/bin/env python3
"""Create an Asana parent task (課題整理＋対策ストーリー) plus subtasks for 2026-2027 inflation / household program.

Requires after load_env_from_dotfile():
  - ASANA_TOKEN
  - Project GID: --project, or ASANA_PROJECT_ID / ASANA_PROJECT_GID / ASANA_PROJECT in .env
  - If none of the above: falls back to a known test project GID (see FALLBACK_PROJECT_GID) with stderr notice.

Windows console: progress lines use ASCII-only (gids/urls) so cp932 consoles do not fail on
Unicode punctuation in task titles (e.g. en-dash). For full UTF-8 logging, set
PYTHONIOENCODING=utf-8 before running.

Idempotency: --if-not-exists skips creation when a top-level project task matches
EPIC_NAME exactly. Renamed epics in Asana or duplicate titles with different Unicode
hyphens will not match; use search in UI or API before re-running.

Usage:
  python asana_inflation_2026_household_program.py --list-projects
  python asana_inflation_2026_household_program.py -y
  python asana_inflation_2026_household_program.py -y --project 1234567890
  python asana_inflation_2026_household_program.py --dry-run -y
  python asana_inflation_2026_household_program.py -y --if-not-exists
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

EPIC_NAME = "【物価・家計2026-2027】複合プレッシャー下の課題整理と対策ストーリー"

EPIC_NOTES = """■ 課題点の整理（現状認識）
・2026年前後の日本の物価は、円安による輸入価格上昇、エネルギー・資源価格、人手不足に伴うコスト上昇が重なり、複合的な上振れ圧力が続く見通し。
・CPIはおおむね3%台前半で推移しやすく、2026年度はおおよそ2.8%前後、2027年度はおおよそ2.3%前後といった「高止まりからの緩やかな低下」シナリオが語られる一方、食料・エネルギーなど生活必需品への打撃は相対的に大きい。
・名目賃金の伸びが物価に追いつかない局面では実質賃金が伸び悩み、同じ金額で買える量・サービスが減る（生活実感の悪化）。
・地政学リスク（例：ウクライナ情勢）や物流・原材料・労務費の上昇が、価格に粘着性をもたらしやすい。

■ 対策ストーリー（全体像）
【政府・政策】令和7年総合経済対策を中心に、低所得者向け支援（給付付き税額控除）、所得税の「年収の壁」160万円への引き上げ、住民税非課税世帯への定額減税（2〜4万円/人）など、家計のキャッシュフローに直接効く施策が束ねられている。あわせて、中小企業の適正な価格転嫁（労務費を含む）を後押しし、コスト増を価格に反映させることで、賃金・分配の改善につなげる意図がある。

【事業者】原材料・物流・人件費の変動を可視化し、取引条件・価格改定の根拠を整備する。適正な価格転嫁は「売上防衛」だけでなく、賃上げ余地を確保するための前提条件でもある。

【家計】固定費（通信・保険・サブスク等）の棚卸し、省エネ、買い物・調達の見直しによりキャッシュアウトを抑える。政策の要点（誰が・いつ・どう受け取れるか）を把握し、申請漏れを防ぐ。余剰資金の運用を検討する場合はNISA等も選択肢だが、元本割れリスクを含むため自己責任で設計する。

■ 本プロジェクトの進め方
下位タスクは柱（マクロ、家計、エネルギー、政策、投資リテラシー等）ごとに進め、四半期ごとに前提（為替・エネルギー・賃金）を更新する。"""


SUBTASKS: list[tuple[str, str, str]] = [
    (
        "【マクロ】2026-2027物価・為替・エネルギーの監視ダッシュボード要件",
        "CPI（総合・食料・エネルギー）、為替、原油・LNG、賃金統計の更新頻度と閾値アラートを定義し、四半期レビューの議事項目テンプレを作る。",
        "マクロ・物価モニタリング",
    ),
    (
        "【マクロ】高止まりシナリオ（2.8%→2.3%）と悪化シナリオの分岐条件",
        "ベース・悪化ケースのトリガー（円安深化、地政学ショック、賃金追随度）を文章化し、家計・事業の意思決定に使う前提セットをまとめる。",
        "マクロ・物価モニタリング",
    ),
    (
        "【家計】固定費の棚卸し（通信・保険・サブスク）と削減優先度",
        "契約更新日・解約条件・代替プランを一覧化し、削減インパクトと手間のマトリクスで優先順位を付ける。",
        "家計・固定費",
    ),
    (
        "【家計】食費・日用品の調達ルール（店舗/EC/まとめ買い）の見直し",
        "単価の追跡方法、ブランド代替、季節商材の活用、食品ロス削減を含めた購買ポリシーを文書化する。",
        "食料・エネルギー調達",
    ),
    (
        "【エネルギー】住宅の省エネ行動リストと投資回収の試算",
        "行動（設定温度、断熱、LED、待機電力）と設備投資（エアコン等）のコスト対効果をざっくり試算し、実行スケジュールを作る。",
        "エネルギー",
    ),
    (
        "【エネルギー】電気・ガスプラン比較の評価軸（単価だけでない契約条件）",
        "基本料金、従量単価、更新条件、再生可能比率などの比較軸を整理し、切替チェックリストを作る。",
        "エネルギー",
    ),
    (
        "【所得】実質賃金・ボーナス・副業のキャッシュフロー影響を整理",
        "税・社保控除後の手取りと物価の関係を月次で見える化する簡易モデル（スプレッドシート等）の要件を定義する。",
        "実質賃金・所得",
    ),
    (
        "【SME/価格】コスト内訳と適正価格転嫁の説明資料テンプレ",
        "原材料・物流・人件費の変動を取引先に示すための根拠資料の章立てと、改定交渉のタイムライン案を作る。",
        "SME・価格転嫁",
    ),
    (
        "【政策】令和7年総合経済対策の要点マップ（対象者×施策×受取導線）",
        "給付付き税額控除、所得税の壁引き上げ、住民税非課税世帯の定額減税などを対象者軸で整理し、確認すべき公式情報源のリンク集を作る。",
        "政策リテラシー（総合経済対策）",
    ),
    (
        "【政策】申請・手続きカレンダー（期限・必要書類の仮置き）",
        "確定情報は都度公式で確認する前提で、社内/家族向けのチェック項目とリマインダー運用案を作る。",
        "政策リテラシー（総合経済対策）",
    ),
    (
        "【投資】NISA・長期分散の学習計画（リスク・元本割れの明記）",
        "投資は元本保証がなく損失の可能性がある。目的・期間・許容下落を定めたうえで、学習リソースと誤解しやすい点（分散、コスト、売買タイミング）をリスト化する。いかなる投資助言も本タスクでは行わない。",
        "投資・NISAリテラシー",
    ),
    (
        "【脆弱世帯】低所得・単身・子育て世帯の支援メニュー照会",
        "自治体の生活支援、相談窓口、学校給食関連費、住宅支援等を地域単位で洗い出し、情報到達のボトルネックを記録する。",
        "脆弱世帯",
    ),
    (
        "【食料・エネルギー】備蓄・代替調達チャネル（災害×物価の両面）",
        "非常食ローテーションと日常の食料調達を両立させる在庫方針、燃料・暖房の代替手段の検討項目をまとめる。",
        "食料・エネルギー調達",
    ),
    (
        "【シナリオ】2026-2027家計シミュレーション（3ケース）",
        "物価・賃金・金利の仮定を3パターン置き、可処分所得と貯蓄率の感度を試算する。前提の更新ルールを添える。",
        "シナリオ計画2026-2027",
    ),
    (
        "【横串】四半期レビュー：KPIと次アクションのテンプレ運用",
        "物価前提・固定費・エネルギー・政策受取・投資学習の進捗を1枚にまとめるレビュー手順を定義する。",
        "横串",
    ),
]


def main() -> None:
    p = argparse.ArgumentParser(description="Create inflation/household story + subtasks in Asana")
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
