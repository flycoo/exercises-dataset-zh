"""验证中文数据、离线页面数据和数据库导出的完整性。"""
import json
import re
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class LocalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = read("data/exercises.json")
        cls.translated = read("data/exercises.zh-CN.json")

    def test_records_and_names(self):
        self.assertEqual(len(self.translated), 1324)
        self.assertEqual(len({x["id"] for x in self.translated}), 1324)
        self.assertEqual([x["id"] for x in self.original], [x["id"] for x in self.translated])
        for old, new in zip(self.original, self.translated):
            with self.subTest(id=old["id"]):
                self.assertEqual(new["name_en"], old["name"])
                self.assertRegex(new["name"], r"[\u4e00-\u9fff]")
                # JM、L、T、V、W、Y 是约定的动作或形状名称。
                self.assertNotRegex(new["name"].replace("JM", ""), r"[a-z]{2}")
                self.assertNotRegex(new["name"], r"[a-z]")
                for key in ("instructions", "instruction_steps", "image", "gif_url", "attribution", "media_id", "created_at"):
                    self.assertEqual(old[key], new[key])
                self.assertTrue(new["instruction_steps"]["zh"])
                for key in ("image", "gif_url"):
                    self.assertTrue((ROOT / new[key]).is_file(), new[key])

    def test_term_coverage_and_schemas(self):
        for filename, dataset in [("exercises.schema.json", self.original), ("exercises.zh-CN.schema.json", self.translated)]:
            schema = read("data/" + filename)
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(dataset)
        terms = read("locales/zh-CN/terms.json")
        for old, new in zip(self.original, self.translated):
            for key in ("category", "body_part", "equipment", "target", "muscle_group"):
                self.assertEqual(new[key], terms[old[key]])
            self.assertEqual(new["secondary_muscles"], [terms[x] for x in old["secondary_muscles"]])

    def test_offline_data_and_reproducible_build(self):
        generated = ["data/exercises.zh-CN.json", "data/exercises.zh-CN.js", "data/exercises.zh-CN.schema.json"]
        before = {name: (ROOT / name).read_bytes() for name in generated}
        subprocess.run([sys.executable, str(ROOT / "scripts/build-localization.py")], check=True, capture_output=True)
        self.assertEqual(before, {name: (ROOT / name).read_bytes() for name in generated})
        script = (ROOT / generated[1]).read_text(encoding="utf-8")
        self.assertEqual(json.loads(script.split("const EXERCISES = ", 1)[1].strip().removesuffix(";")), self.translated)
        for page in ("index.html", "setup.html"):
            html = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn('<html lang="zh-CN">', html)
            self.assertIn('<script src="data/exercises.zh-CN.js"></script>', html)
            self.assertIn("© Gym visual", html)

    def test_sql_exports(self):
        output = subprocess.check_output(["node", str(ROOT / "tests/sql-exports.cjs")])
        pages = json.loads(output.decode("utf-8"))
        self.assertEqual(pages["index.html"], pages["setup.html"])
        required = {"instructions_zh", "instructions_fr", "media_id", "attribution"}
        for db, export in pages["setup.html"].items():
            self.assertEqual(export["inserts"].count("INSERT INTO exercises ("), 1324)
            for column in required:
                self.assertRegex(export["ddl"], rf"\b{column}\s+")
                self.assertIn(column, export["inserts"].split("VALUES", 1)[0])
            self.assertIn("四分之三程仰卧起坐", export["inserts"])
            if db == "mssql":
                self.assertIn("NVARCHAR", export["ddl"])
                self.assertIn("N'四分之三程仰卧起坐'", export["inserts"])
            if db == "mysql":
                self.assertIn("utf8mb4", export["ddl"])
        export = pages["setup.html"]["sqlite"]
        with sqlite3.connect(":memory:") as connection:
            connection.executescript(export["ddl"] + export["inserts"])
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM exercises").fetchone()[0], 1324)
            rows = connection.execute("SELECT id,name,instructions_zh,instructions_fr,media_id,attribution,secondary_muscles FROM exercises ORDER BY id").fetchall()
            by_id = {x["id"]: x for x in self.translated}
            for identity, name, zh, fr, media, attribution, muscles in rows:
                expected = by_id[identity]
                self.assertEqual((name, zh, fr, media, attribution), (expected["name"], expected["instructions"]["zh"], expected["instructions"]["fr"], expected["media_id"], expected["attribution"]))
                self.assertEqual(json.loads(muscles), expected["secondary_muscles"])


if __name__ == "__main__":
    unittest.main()
