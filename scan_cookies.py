
import os, sqlite3, shutil, tempfile, glob, json
ROAM = r"C:\Users\刘亮\AppData\Roaming\@deepseek-ai\dsh-desktop"
dbs = glob.glob(os.path.join(ROAM, "**", "Cookies"), recursive=True)
print("db files:", len(dbs))
for db in dbs:
    tmp = os.path.join(tempfile.gettempdir(), "c_%d.db" % abs(hash(db)))
    try:
        shutil.copy2(db, tmp)
        for suf in ("-wal", "-shm"):
            if os.path.exists(db + suf):
                shutil.copy2(db + suf, tmp + suf)
        con = sqlite3.connect(tmp)
        n = con.execute("select count(*) from cookies").fetchone()[0]
        hosts = [r[0] for r in con.execute("select distinct host_key from cookies").fetchall()]
        print("---", db.replace(ROAM, "~"), "rows:", n)
        print("   hosts:", hosts[:25])
    except Exception as e:
        print("ERR", db, e)
