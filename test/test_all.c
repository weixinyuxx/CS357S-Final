#include <stdio.h>
int main() {
    int x = 0;
    int y = 0;
    int reg1 = 0;
    int reg2 = 0;

    int sum = x + y;
    printf("%d\n", sum);
    int dest16 = reg2 + 5;
    printf("%d\n", sum);
    int dest0 = reg2 + reg2;
    printf("%d\n", dest0);
    int dest1 = reg2 - reg2;
    printf("%d\n", dest1);
    int dest2 = reg2 * reg2;
    printf("%d\n", dest2);

    // int dest3 = reg2 << reg2;
    // printf("%d\n", dest3);
    // int dest4 = (unsigned int)(reg2) >> reg2;
    // printf("%d\n", dest4);
    // int dest5 = reg2 >> reg2;
    // printf("%d\n", dest5);

    int dest6 = reg2 & reg2;
    printf("%d\n", dest6);
    int dest7 = reg2 | reg2;
    printf("%d\n", dest7);
    int dest8 = reg2 ^ reg2;
    printf("%d\n", dest8);
    
    return 0;
}
