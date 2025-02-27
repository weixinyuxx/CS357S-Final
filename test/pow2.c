#include <stdio.h>
int main() {
    int n = 5;
    int p = 8;
    for (int i = 0; i < p; i++) {
        n = n << 1;
    }
    print32(n);
    return 0;
}