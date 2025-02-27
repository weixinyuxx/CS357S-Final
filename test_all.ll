target triple = "x86_64-pc-linux-gnu"

define i32 @main() {
  %x = add i32 0, 0
  %y = add i32 0, 0
  %reg1 = add i64 0, 0
  %reg2 = add i64 0, 0

  %sum = add i32 %x, %y
  
  %dest16 = add i64 %reg2, 5
  %dest0 = add i64 %reg2, %reg2
  %dest1 = sub i64 %reg2, %reg2
  %dest2 = mul i64 %reg2, %reg2

  ; %dest3 = shl i64 %reg2, %reg2
  %dest4 = lshr i64 %reg2, %reg2
  %dest5 = ashr i64 %reg2, %reg2

  %dest6 = and i64 %reg2, %reg2
  %dest7 = or i64 %reg2, %reg2
  %dest8 = xor i64 %reg2, %reg2
  
  ret i32 %sum

}