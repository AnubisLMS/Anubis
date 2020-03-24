/* 
 * phase4c.c - A recursive function to sort out.  
 *
 *          0, if n=0
 * F(n,b) = b, if n=1, 
 *          b + F(n-1, b) + F(n-2, b), if n>1
 * 
 * For a randomly chosen n, student must enter matching F(n, b) and b.
 */

int func4(int n, int base) {
    if (n <= 0) {
	return 0;
    }
    if (n == 1) {
	return base;
    }
    return base + func4(n-1, base) + func4(n-2, base);
}

void phase_4(char *input) {
#if defined(PROBLEM)
    int n, base, val, result, numScanned;

    numScanned = sscanf(input, "%d %d", &val, &base);
    if ((numScanned != 2) || (base < MIN_BASE) || (base > MAX_BASE)) {
	explode_bomb();
    }

    n = SEQ_INDEX_SET;
    result = func4(n, base);

    if (result != val) {
	explode_bomb();
    }
#elif defined(SOLUTION)
    printf("%d %d %s\n", func4(SEQ_INDEX_GET, SEQ_BASE_GET), SEQ_BASE_SET, SECRET_PHRASE);
#else
    invalid_phase("4c");
#endif
}

