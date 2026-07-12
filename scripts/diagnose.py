#!/usr/bin/env python3
"""
质量文化成熟度诊断脚本
输入：10个问题的得分（0-5分制）
输出：JSON格式的诊断结果
"""

import argparse
import json
import sys

# 五级成熟度定义
LEVELS = {
    1: {
        "name": "无知觉期",
        "range": [0, 10],
        "特征": "质量全靠检验，出了问题罚检验员",
        "原话": "质量是质量部的事",
        "描述": "企业还没有形成质量文化意识，质量完全依赖检验部门。出了问题第一反应是追责，而不是解决问题。这种状态下，检验员成了背锅侠，一线员工能躲就躲。"
    },
    2: {
        "name": "觉醒期",
        "range": [11, 20],
        "特征": "开始用SPC、8D等工具，但停留在救火阶段",
        "原话": "质量是技术活",
        "描述": "企业开始意识到质量需要工具和方法，但使用是被动的、应急的。出了问题才想起来用8D，分析完就完事，下次照样出问题。质量是质量工程师的事，和我无关。"
    },
    3: {
        "name": "管控期",
        "range": [21, 30],
        "特征": "有体系、有流程、有KPI，但员工被动执行",
        "原话": "质量是规定的动作",
        "描述": "企业有完整的质量管理体系，但员工把质量当成'规定动作'，做是因为要过审核，不做也没人管。质量是流程的事，不是我主动想做的事。"
    },
    4: {
        "name": "预防期",
        "range": [31, 40],
        "特征": "全员参与质量改善，FMEA/防错成为习惯",
        "原话": "质量是每个人的事",
        "描述": "质量意识深入人心，员工主动发现问题、提出改善。不再是'你要我做'，而是'我应该做'。防错和FMEA成为工作习惯，而不是应付审核的文档。"
    },
    5: {
        "name": "卓越期",
        "range": [41, 50],
        "特征": "质量成为企业核心竞争力，供应商和客户都受益",
        "原话": "质量是我们的品牌",
        "描述": "质量成为企业的核心竞争力和品牌标签。不只是内部做得好，还输出标准给供应商，帮助客户成功。竞争对手来参观学习，行业标杆地位稳固。"
    }
}

# 各等级推荐的启动阶段
LEVEL_TO_PHASE = {
    1: "第一阶段",
    2: "第一阶段",
    3: "第二阶段",
    4: "第三阶段",
    5: "第三阶段"
}

# 维度名称
DIMENSIONS = [
    "问题响应思维",
    "主动报告意愿",
    "质量目标分解",
    "新人质量培训",
    "领导质量重视度",
    "跨部门协同",
    "质量复盘机制",
    "改善建议氛围",
    "根因分析深度",
    "质量文化载体"
]


def validate_score(score):
    """验证分数是否在0-5范围内"""
    try:
        s = int(score)
        if 0 <= s <= 5:
            return s
        else:
            raise ValueError(f"分数 {s} 不在0-5范围内")
    except ValueError as e:
        raise ValueError(f"无效分数 '{score}': {e}")


def calculate_level(total_score):
    """根据总分计算成熟度等级"""
    for level, info in LEVELS.items():
        min_score, max_score = info["range"]
        if min_score <= total_score <= max_score:
            return level
    # 如果超出范围，返回最接近的等级
    if total_score < 10:
        return 1
    else:
        return 5


def generate_recommendations(level, scores):
    """生成个性化建议"""
    recommendations = []
    
    # 找出得分最低的维度
    min_score = min(scores)
    min_indices = [i for i, s in enumerate(scores) if s == min_score]
    
    for idx in min_indices:
        dim_name = DIMENSIONS[idx]
        if min_score <= 1:
            recommendations.append(f"【紧急】{dim_name}是当前最大短板，建议优先解决")
        elif min_score <= 2:
            recommendations.append(f"【重要】{dim_name}需要重点改善")
    
    return recommendations


def main():
    parser = argparse.ArgumentParser(description="质量文化成熟度诊断")
    parser.add_argument("--scores", required=False,
                        help="10个问题得分，逗号分隔，如: 3,2,4,1,2,3,2,1,2,3（与 --input 二选一）")
    parser.add_argument("--input", required=False,
                        help="JSON 输入：文件路径或 JSON 字符串，需含 scores 键，"
                             "如 {\"scores\":[3,2,4,1,2,3,2,1,2,3],\"industry\":\"制造业\"}")
    parser.add_argument("--industry", required=False, default="",
                        help="行业标识，用于差异化建议提示（如 制造业/服务业/建筑业/医疗/研发型）")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                        help="输出格式，默认json")
    
    args = parser.parse_args()
    
    # 解析分数（--input 优先，其次 --scores）
    industry = args.industry
    try:
        if args.input:
            raw = args.input.strip()
            if raw.startswith("{"):
                data = json.loads(raw)
            else:
                with open(raw, "r", encoding="utf-8") as f:
                    data = json.load(f)
            scores_raw = data.get("scores")
            if not scores_raw:
                raise ValueError("JSON 中未找到 scores 键")
            if isinstance(scores_raw, str):
                score_strs = scores_raw.split(",")
            else:
                score_strs = [str(x) for x in scores_raw]
            if data.get("industry"):
                industry = data["industry"]
        elif args.scores:
            score_strs = args.scores.split(",")
        else:
            raise ValueError("必须提供 --scores 或 --input 之一")
        if len(score_strs) != 10:
            raise ValueError(f"需要10个分数，实际收到{len(score_strs)}个")
        scores = [validate_score(s) for s in score_strs]
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        sys.exit(1)
    
    # 计算结果
    total_score = sum(scores)
    avg_score = total_score / 10
    level = calculate_level(total_score)
    level_info = LEVELS[level]
    recommended_phase = LEVEL_TO_PHASE[level]
    recommendations = generate_recommendations(level, scores)
    if industry:
        recommendations.append(
            f"【行业提示】按'{industry}'行业特征给出建议，活动落地请结合该行业现场条件裁剪")
    
    # 构建输出
    result = {
        "status": "success",
        "诊断结果": {
            "总得分": total_score,
            "平均得分": round(avg_score, 1),
            "满分": 50,
            "得分率": f"{round(avg_score/5*100, 1)}%"
        },
        "成熟度等级": {
            "等级": level,
            "名称": level_info["name"],
            "典型特征": level_info["特征"],
            "经典原话": level_info["原话"],
            "详细描述": level_info["描述"]
        },
        "推荐启动阶段": recommended_phase,
        "各维度得分": {
            DIMENSIONS[i]: scores[i] for i in range(10)
        },
        "个性化建议": recommendations,
        "解读": f"你们企业的质量文化处于'{level_info['name']}'，{level_info['描述']}。建议从{recommended_phase}开始推进质量文化建设。"
    }
    
    if args.format == "text":
        # 文本格式输出
        lines = [
            "=" * 50,
            "质量文化成熟度诊断报告",
            "=" * 50,
            f"总得分: {total_score}/50 (得分率{result['诊断结果']['得分率']})",
            f"成熟度等级: Level {level} - {level_info['name']}",
            f"典型特征: {level_info['特征']}",
            f"经典原话: '{level_info['原话']}'",
            "",
            f"推荐从【{recommended_phase}】开始推进",
            "",
            "各维度得分:",
        ]
        for i, dim in enumerate(DIMENSIONS):
            score = scores[i]
            bar = "■" * score + "□" * (5 - score)
            lines.append(f"  {dim}: {bar} ({score}/5)")
        
        if recommendations:
            lines.append("")
            lines.append("重点改善建议:")
            for rec in recommendations:
                lines.append(f"  - {rec}")
        
        lines.extend([
            "",
            "=" * 50,
            result["解读"]
        ])
        print("\n".join(lines))
    else:
        # JSON格式输出
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
