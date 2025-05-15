import fsspec, json, hashlib
from datetime import datetime, timezone

minio_cfg = {
    "client_kwargs": {"endpoint_url": "http://localhost:9000"},
    "key": "minioadmin",
    "secret": "minioadmin",
    "anon": False
}

fs = fsspec.filesystem("s3", **minio_cfg)
try:
    summary_files = fs.glob("fusion-lake/posterior/*.json")
except Exception as e:
    print(f"Failed to list posterior summaries: {e}")
    summary_files = []

ledger_path = "fusion-lake/ledger/Γ.csv"
for file_path in summary_files:
    try:
        # Read JSON content and compute hash
        with fs.open(file_path, "rb") as f:
            data = f.read()
        summary = json.loads(data.decode("utf-8"))
        scene_id = summary.get("scene_id", file_path.split("/")[-1].replace(".json", ""))
        mean_val = summary.get("mean")
        var_val = summary.get("variance")
        sha256_hash = hashlib.sha256(data).hexdigest()
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as e:
        print(f"Skipping ledger entry for {file_path}: {e}")
        continue

    # Append or create ledger CSV
    try:
        if fs.exists(ledger_path):
            old_content = fs.open(ledger_path, "rb").read().decode("utf-8")
        else:
            old_content = ""
        new_line = f"{scene_id},{sha256_hash},{timestamp},Γ,{mean_val},{var_val}\n"
        if old_content == "":
            header = "scene_id,sha256,timestamp_utc,stage,mean,variance\n"
            content = header + new_line
        else:
            content = old_content
            if not content.endswith("\n"):
                content += "\n"
            content += new_line
        with fs.open(ledger_path, "wb") as f:
            f.write(content.encode("utf-8"))
    except Exception as e:
        print(f"Failed to update ledger for {scene_id}: {e}")
