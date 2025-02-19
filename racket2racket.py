from jinja2 import Environment, FileSystemLoader
import subprocess
import re

def render(expr, type, exclude, tmp_path):
    """Render the template racket file with the given parameters, writing to `tmp_path`."""
    try:
        assert type[0] == 'i'
        type = int(type[1:])
    except:
        return None
    rktop = [
            "bvadd", "bvsub", "bvmul",
            "bvshl", "bvlshr", "bvashr",
            "bvand", "bvor", "bvxor",
            "bveq"
    ]
    rktop = list(set(rktop) - set(exclude))
    rktop = " ".join(rktop)
    data = {"expr": expr, "type": type, "rktop": rktop}

    # Set up the Jinja environment
    env = Environment(loader=FileSystemLoader("."))  # Load templates from current directory

    # Load the template file
    template = env.get_template("racket_template.rkt")
    racket_code = template.render(data)

    with open(tmp_path, "w") as f:
        f.write(racket_code)
    return 1

def racket_run(tmp_path):
    """Run the temporary racket file in `tmp_path`, and extract the generated expression."""
    process = subprocess.Popen(
        ["racket", tmp_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    pattern = re.compile(r"\(define\s+\(alter_op %reg1 %reg2\)\s*(\(.+\))")
    for line in process.stdout:
        # print(line)
        match = pattern.search(line)
        if match:
            return match.group(1)
    return None

def r2r(expr, type, exclude, tmp_path="tmp.rkt"):
    """Translate from racket to racket code."""
    if render(expr, type, exclude, tmp_path) == None:
        return None
    result = racket_run(tmp_path)
    if result == None:
        return None
    return result

print(r2r("(bvadd %reg2 %reg2)", "i64", ["bvadd"]))
