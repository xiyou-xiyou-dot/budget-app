from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_PATH = "budget.db"


def get_db():
    """连接数据库，返回 connection 对象"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 让查询结果可以用列名访问
    return conn


def init_db():
    """初始化数据库，创建表"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            type      TEXT    NOT NULL,   -- 'income' 或 'expense'
            category  TEXT    NOT NULL,   -- 分类，如 '餐饮'、'工资'
            amount    REAL    NOT NULL,   -- 金额
            note      TEXT,              -- 备注（可为空）
            date      TEXT    NOT NULL    -- 日期，格式 YYYY-MM-DD
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    """首页：展示所有记录 + 收支汇总"""
    conn = get_db()

    records = conn.execute(
        "SELECT * FROM records ORDER BY date DESC, id DESC"
    ).fetchall()

    total_income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM records WHERE type = 'income'"
    ).fetchone()[0]

    total_expense = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM records WHERE type = 'expense'"
    ).fetchone()[0]

    conn.close()

    balance = total_income - total_expense
    return render_template(
        "index.html",
        records=records,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )


@app.route("/add", methods=["POST"])
def add():
    """接收表单，添加一条记录"""
    record_type = request.form["type"]
    category    = request.form["category"].strip()
    amount      = float(request.form["amount"])
    note        = request.form.get("note", "").strip()
    date        = request.form["date"]

    conn = get_db()
    conn.execute(
        "INSERT INTO records (type, category, amount, note, date) VALUES (?, ?, ?, ?, ?)",
        (record_type, category, amount, note, date),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete(record_id):
    """删除指定 id 的记录"""
    conn = get_db()
    conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0",debug=True)
