from jinja2 import Environment, FileSystemLoader
import subprocess
import re

def render(expr, type, exclude, tmp_path, reg1, reg2):
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
    data = {"expr": expr, "type": type, "rktop": rktop, "left": reg1, "right": reg2}

    # Set up the Jinja environment
    env = Environment(loader=FileSystemLoader("."))  # Load templates from current directory

    # Load the template file
    template = env.get_template("racket_template.rkt")
    racket_code = template.render(data)

    with open(tmp_path, "w") as f:
        f.write(racket_code)
    return 1

def racket_run(tmp_path, reg1, reg2):
    """Run the temporary racket file in `tmp_path`, and extract the generated expression."""
    process = subprocess.Popen(
        ["racket", tmp_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    result = ""
    count = 0
    for line in process.stdout:
        # print(line)
        if count == 0:
            count += 1
            continue
        if (line == "#f\n"):
            return None
        result += line
    temp = f"(define (alter_op {reg1} {reg2}) "
    result = result[len(temp):]
    result = result[:-2]
    return result

def r2r(expr, type, exclude, reg1, reg2, tmp_path="tmp.rkt"):
    """Translate from racket to racket code."""
    if reg1 == reg2:
        reg1 = "%tmp_alter"
    if render(expr, type, exclude, tmp_path, reg1, reg2) == None:
        return None
    result = racket_run(tmp_path, reg1, reg2)
    if result == None:
        return None
    return result

print(r2r("(bvadd %reg2 %reg2)", "i64", ["bvadd"], "%reg1", "%reg2"))

