define i32 @add_two(i32 %x, i32 %y, i64 %reg1, i64 %reg2) {

  %sum = add i32 %x, %y
  
  %dest16 = add i64 %reg2, 5
  %dest0 = add i64 %reg2, %reg2
  %dest1 = sub i64 %reg2, %reg2
  %dest2 = mul i64 %reg2, %reg2

  %dest3 = shl i64 %reg2, %reg2
  %dest4 = lshr i64 %reg2, %reg2
  %dest5 = ashr i64 %reg2, %reg2

  %dest6 = and i64 %reg2, %reg2
  %dest7 = or i64 %reg2, %reg2
  %dest8 = xor i64 %reg2, %reg2
  
  ret i32 %sum

}