#include <stdio.h>

void print32(u_int32_t n) {
    printf("The %d th instruction aborted\n", n);
}
void print64(u_int64_t n) {
    printf("The %llu th instruction aborted\n", n);
}
