target triple = "x86_64-pc-linux-gnu"

define i32 @main() {

  %x = add i32 0, 0
  call void @sdc_check_i32(i32 %x, i32 0)

  %y = add i32 0, 0
  call void @sdc_check_i32(i32 %y, i32 0)

  %reg1 = add i64 0, 0
  call void @sdc_check_i64(i64 %reg1, i64 0)

  %reg2 = add i64 0, 0
  call void @sdc_check_i64(i64 %reg2, i64 1)

  %dest_1 = mul i32 %x, 4294967295
  %dest_2 = sub i32 %y, %dest_1
  %sum = add i32 %x, %y
  call void @sdc_check_i32(i32 %sum, i32 %dest_2)
  
  %dest_3 = sub i64 %reg2, 18446744073709551611
  %dest16 = add i64 %reg2, 5
  call void @sdc_check_i64(i64 %dest16, i64 %dest_3)
  %dest_4 = mul i64 2, %reg2
  %dest_5 = lshr i64 %dest_4, 0
  %dest0 = add i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest0, i64 %dest_5)
  %dest_6 = lshr i64 1, 9223372036854775806
  %dest1 = sub i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest1, i64 %dest_6)
  %dest18 = mul i64 %reg2, %reg2
  %dest2 = mul i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest2, i64 %dest18)

  ; %dest3 = shl i64 %reg2, %reg2

  %dest4 = lshr i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest4, i64 0)
  %dest_7 = lshr i64 %reg2, 63
  %dest_8 = mul i64 %dest_7, 18446744073709551615
  %dest5 = ashr i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest5, i64 %dest_8)


  %dest6 = and i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest6, i64 %reg2)

  %dest7 = or i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest7, i64 %reg2)

  %dest8 = xor i64 %reg2, %reg2
  call void @sdc_check_i64(i64 %dest8, i64 0)
  
  ret i32 %sum

}

define void @sdc_check_i32(i32 %reg1, i32 %reg2) {
entry:
    %cmp = icmp ne i32 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @abort()
    br label %done

done:
    ret void
}

define void @sdc_check_i64(i64 %reg1, i64 %reg2) {
entry:
    %cmp = icmp ne i64 %reg1, %reg2
    br i1 %cmp, label %abort, label %done

abort:
    call void @abort()
    br label %done

done:
    ret void
}

declare void @abort()
