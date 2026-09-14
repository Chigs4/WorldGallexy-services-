
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, os, secrets
from datetime import datetime

app = Flask(__name__)
DB = os.environ.get("WG_DB", "worldgallexy_test.db")
ADMIN_PIN = os.environ.get("WG_ADMIN_PIN", "1234")  # change before sharing publicly

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, phone TEXT NOT NULL, email TEXT NOT NULL,
        service TEXT NOT NULL, area TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT NOT NULL, phone TEXT NOT NULL, service TEXT NOT NULL,
        description TEXT NOT NULL, area TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL, worker_id INTEGER NOT NULL,
        amount REAL NOT NULL, message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'submitted',
        created_at TEXT NOT NULL
    );
    """)
    con.commit(); con.close()

@app.route("/")
def home():
    con=db()
    workers=con.execute("SELECT * FROM workers WHERE status='approved' ORDER BY id DESC").fetchall()
    jobs=con.execute("SELECT * FROM jobs WHERE status='open' ORDER BY id DESC").fetchall()
    con.close()
    return render_template("index.html", workers=workers, jobs=jobs)

@app.post("/worker/apply")
def worker_apply():
    f=request.form
    con=db()
    con.execute("""INSERT INTO workers(name,phone,email,service,area,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (f["name"],f["phone"],f["email"],f["service"],f["area"],datetime.utcnow().isoformat()))
    con.commit(); con.close()
    return redirect(url_for("home")+"#workers")

@app.post("/job")
def job():
    f=request.form
    con=db()
    con.execute("""INSERT INTO jobs(customer,phone,service,description,area,created_at)
                   VALUES(?,?,?,?,?,?)""",
                (f["customer"],f["phone"],f["service"],f["description"],f["area"],datetime.utcnow().isoformat()))
    con.commit(); con.close()
    return redirect(url_for("home")+"#jobs")

@app.post("/quote")
def quote():
    f=request.form
    con=db()
    worker=con.execute("SELECT id FROM workers WHERE id=? AND status='approved'",(f["worker_id"],)).fetchone()
    if not worker:
        con.close(); return "Worker not approved",400
    con.execute("""INSERT INTO quotes(job_id,worker_id,amount,message,created_at)
                   VALUES(?,?,?,?,?)""",
                (f["job_id"],f["worker_id"],float(f["amount"]),f["message"],datetime.utcnow().isoformat()))
    con.commit(); con.close()
    return redirect(url_for("home")+"#jobs")

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST" and request.form.get("pin")==ADMIN_PIN:
        con=db()
        pending=con.execute("SELECT * FROM workers WHERE status='pending'").fetchall()
        jobs=con.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
        quotes=con.execute("""SELECT q.*, w.name worker_name, j.service job_service
                              FROM quotes q JOIN workers w ON w.id=q.worker_id
                              JOIN jobs j ON j.id=q.job_id ORDER BY q.id DESC""").fetchall()
        con.close()
        return render_template("admin.html",pending=pending,jobs=jobs,quotes=quotes)
    return render_template("admin_login.html")

@app.post("/admin/worker/<int:wid>/<action>")
def worker_action(wid, action):
    if request.form.get("pin") != ADMIN_PIN: return "Unauthorized",403
    if action not in ("approved","rejected"): return "Bad action",400
    con=db(); con.execute("UPDATE workers SET status=? WHERE id=?",(action,wid)); con.commit(); con.close()
    return redirect(url_for("admin"))

@app.post("/admin/job/<int:jid>/close")
def close_job(jid):
    if request.form.get("pin") != ADMIN_PIN: return "Unauthorized",403
    con=db(); con.execute("UPDATE jobs SET status='closed' WHERE id=?",(jid,)); con.commit(); con.close()
    return redirect(url_for("admin"))

@app.route("/api/jobs/<int:jid>")
def job_quotes(jid):
    con=db()
    rows=con.execute("""SELECT q.amount,q.message,w.name,w.service,w.area
                        FROM quotes q JOIN workers w ON w.id=q.worker_id
                        WHERE q.job_id=? ORDER BY q.amount ASC""",(jid,)).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

init()
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
