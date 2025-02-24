#include <stdio.h>

int add(x, y){
    return x + y;
}

int main(){
    int x = 10;
    int y = 5;
    printf("%d\n", add(x, y));
    return 0;
}