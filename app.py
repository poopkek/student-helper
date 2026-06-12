from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DB = "student_helper.db"


def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS notes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT,
description TEXT,
deadline TEXT,
status TEXT
)
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():

    search = request.args.get("search", "")

    conn = sqlite3.connect(DB)

    if search:

        notes = conn.execute(
            """
            SELECT * FROM notes
            WHERE title LIKE ?
            OR description LIKE ?
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:

        notes = conn.execute(
            "SELECT * FROM notes"
        ).fetchall()

        conn.close()

    completed_count = 0

    for note in notes:

        if len(note) > 4 and note[4] == "Выполнено":

            completed_count += 1

    return render_template(
        "index.html",
        notes=notes,
        search=search,
        completed_count=completed_count
    )


@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        deadline = request.form["deadline"]
        status = "В процессе"

        conn = sqlite3.connect(DB)

        conn.execute(
            """
            INSERT INTO notes
            (title, description, deadline, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                description,
                deadline,
                status
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = sqlite3.connect(DB)

    if request.method == "POST":

        title = request.form["title"]

        description = request.form["description"]

        deadline = request.form["deadline"]

        conn.execute(
            """
            UPDATE notes
            SET title=?,
                description=?,
                deadline=?
            WHERE id=?
            """,
            (
                title,
                description,
                deadline,
                id
            )
        )

        conn.commit()

        conn.close()

        return redirect("/")

    note = conn.execute(
        "SELECT * FROM notes WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        note=note
    )

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect(DB)

    conn.execute(
        "DELETE FROM notes WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/done/<int:id>")
def done(id):

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        UPDATE notes
        SET status='Выполнено'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()

    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)