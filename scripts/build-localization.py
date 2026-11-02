"""从原始数据和中文词表生成中文 JSON、离线浏览数据和 Schema。"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path, value, *, compact=False):
    text = json.dumps(value, ensure_ascii=False, indent=None if compact else 2)
    (ROOT / path).write_text(text + "\n", encoding="utf-8", newline="\n")


def build():
    source = read("data/exercises.json")
    names = read("locales/zh-CN/names.json")
    terms = read("locales/zh-CN/terms.json")
    ids = {item["id"] for item in source}
    if set(names) != ids:
        raise ValueError(f"中文名称与源数据 ID 不一致：缺少 {ids - set(names)}，多余 {set(names) - ids}")
    translated = copy.deepcopy(source)
    for item in translated:
        item["name_en"] = item["name"]
        item["name"] = names[item["id"]]
        if not item["instructions"].get("zh") or not item["instruction_steps"].get("zh"):
            raise ValueError(f"缺少中文动作说明：{item['id']}")
        for key in ("category", "body_part", "equipment", "target", "muscle_group"):
            item[key] = terms[item[key]]
        item["secondary_muscles"] = [terms[value] for value in item["secondary_muscles"]]
    write("data/exercises.zh-CN.json", translated)
    # 经典脚本支持 file:// 直接打开，无需 fetch 或本地服务器。
    payload = json.dumps(translated, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    (ROOT / "data/exercises.zh-CN.js").write_text(
        "// 自动生成，请编辑 locales/zh-CN/ 后运行构建脚本。\nconst EXERCISES = " + payload + ";\n", encoding="utf-8", newline="\n")
    schema = read("data/exercises.schema.json")
    schema["$id"] = "https://github.com/flycoo/exercises-dataset-zh/blob/main/data/exercises.zh-CN.schema.json"
    schema["title"] = "中文健身动作数据集"
    schema["description"] = "简体中文元数据与多语言动作说明；name_en 保留英文名称，ID 和媒体路径与原始数据一致。"
    exercise = schema["$defs"]["exercise"]
    exercise["properties"]["body_part"]["enum"] = [terms[x] for x in exercise["properties"]["body_part"]["enum"]]
    descriptions = {
        "id": "四位数字动作 ID，与原始数据一致。", "name": "简体中文动作名称。",
        "category": "中文身体部位分类，与 body_part 一致。", "body_part": "中文身体部位。",
        "equipment": "中文器械名称。", "instructions": "以语言代码为键的完整动作说明。",
        "instruction_steps": "以语言代码为键的有序动作步骤。", "muscle_group": "中文协同肌群。",
        "secondary_muscles": "中文辅助肌群列表。", "target": "中文主要目标肌群。",
        "media_id": "原始媒体引用 ID。", "image": "180×180 缩略图相对路径。",
        "gif_url": "180×180 动画 GIF 相对路径。", "attribution": "保留的原始媒体版权署名。",
        "created_at": "原始记录创建时间，ISO 8601 格式。"}
    for key, description in descriptions.items():
        exercise["properties"][key]["description"] = description
    exercise["properties"]["name_en"] = {"type": "string", "minLength": 1, "description": "原始英文名称，用于英文搜索和来源核对。"}
    exercise["required"].append("name_en")
    schema["$defs"]["languageMap"]["description"] = "以 ISO 639-1 语言代码为键的说明文本。"
    schema["$defs"]["languageStepsMap"]["description"] = "以 ISO 639-1 语言代码为键的步骤数组。"
    write("data/exercises.zh-CN.schema.json", schema)
    print(f"已生成 {len(translated)} 条中文动作记录、离线脚本和 Schema。")


if __name__ == "__main__":
    build()
