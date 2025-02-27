#include <stdio.h>
int main() {
    int n = 5;
    int p = 8;
    for (int i = 0; i < p; i++) {
        p = p << 1;
    }
    printf("Result: %d\n", p);
    return 0;
}