#include <stdio.h>
int main() {
    int p = 4;
    int result = 1;
    for (int i = 0; i < p; i++) {
        result = result << 1;
    }
    printf("Result: %d\n", result);
    return 0;
}