class DestReg:
    def __init__(self):
        self.reg_num = 0
    def alt_dest(self):
        self.reg_num += 1
        return f"%dest_{self.reg_num}"

def rkt2llvm(rkt_str, type, dest_reg):
    """Given a rkt string, returns a list of llvm instructions."""
    assert rkt_str.startswith('(') and rkt_str.endswith(')')
    inst, dest, _ = rkt2llvm_helper(rkt_str, 0, type, dest_reg)
    return inst, dest

opcode_mapping = {"bvadd":"add", "bvsub":"sub", "bvmul":"mul", "bvshl":"shl", "bvlshr":"lshr", "bvashr":"ashr",
                  "bvand":"and", "bvor":"or", "bvxor":"xor"}

def find_whitespace(rkt_str, start):
    """Returens the index of the first whitespace (' ' or '\n')"""
    while (rkt_str[start] != ' ' and rkt_str[start] != '\n'):
        start += 1
    return start

def skip_whitespace(rkt_str, start):
    while (rkt_str[start] == ' ' or rkt_str[start] == '\n'):
        start += 1
    return start

def rkt2llvm_helper(rkt_str, iterator, type, dest_reg):
    """Given a rkt string and an iterator, returns a list of instructions and the final destination, and the iterator."""
    first_space = find_whitespace(rkt_str, iterator)
    first_start = skip_whitespace(rkt_str, first_space)
    opcode = rkt_str[iterator+1:first_space]
    if (rkt_str[first_start] == '('):
        first_inst, first_dest, iterator = rkt2llvm_helper(rkt_str, first_start, type, dest_reg)
    else:
        iterator = find_whitespace(rkt_str, first_start)
        first_inst = []
        first_dest = rkt_str[first_start:iterator]
    # iterator points to the space between the first and the second operator
    iterator = skip_whitespace(rkt_str, iterator)
    second_start = iterator
    if (rkt_str[second_start] == '('):
        second_inst, second_dest, iterator = rkt2llvm_helper(rkt_str, second_start, type, dest_reg)
    else:
        iterator = rkt_str.find(')', iterator)
        second_inst = []
        second_dest = rkt_str[second_start:iterator]
    # iterator points to the last closing parenthesis
    iterator += 1
    inst = []
    dest = ""
    if opcode == "bv":
        val = int(first_dest[2:], 16)
        inst = []
        dest = str(val)
    else:
        dest = dest_reg.alt_dest()
        inst = (
            first_inst
            + second_inst
            + [f"{dest} = {opcode_mapping[opcode]} {type} {first_dest}, {second_dest}"]
        )
    return inst, dest, iterator

# rkt = "(bvshl %reg2 (bvlshr (bv #x0000000000010000 64) (bv #x0000000000000010 64)))"

# rkt = """(bvxor 
#    (bvand (bv #x4000000000000000 64) (bv #x0000000000000009 64))
#    (bvmul (bv #x0000000000000002 64) %reg2))"""
# print(
#     rkt2llvm(
#         rkt, "i64", DestReg()
#     )
# )
