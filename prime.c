#include <stdio.h>

// Function to perform prime factorization
void primeFactorization(int n) {
    printf("Prime factors of %d: ", n);

    // Step 1: Divide by 2 while even
    while (n % 2 == 0) {
        printf("%d ", 2);
        n /= 2;
    }

    // Step 2: Check for odd factors from 3 onwards
    for (int i = 3; i * i <= n; i += 2) {
        while (n % i == 0) {
            printf("%d ", i);
            n /= i;
        }
    }

    // Step 3: If n is still greater than 1, it's a prime number itself
    if (n > 1) {
        printf("%d", n);
    }

    printf("\n");
}

// Driver Code
int main() {
    int num;
    printf("Enter a number: ");
    scanf("%d", &num);
    
    if (num <= 1) {
        printf("Enter a number greater than 1.\n");
    } else {
        primeFactorization(num);
    }

    return 0;
}