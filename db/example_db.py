from pathlib import Path
# from pprint import pprint

def load_db(data_dir:str ="db/example/") -> dict:
    """Load the files from specified directory."""
    output = {}
    data_path = Path(data_dir)
    for file_ in data_path.iterdir():
        if ".csv" not in file_.name:
            continue
        file_lines = file_.read_text().splitlines()
        file_key = file_.name.replace(".csv", "")
        output[file_key] = []

        colnames = file_lines[0].split("\t")
        file_lines = file_lines[1:]

        for fline in file_lines:
            fline = fline.split("\t")
            output[file_key].append({
                colnames[line_idx]: fline[line_idx]
                for line_idx in range(len(fline))
            })

    return output
