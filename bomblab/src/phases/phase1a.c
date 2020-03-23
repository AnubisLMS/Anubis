/* 
 * phase1a.c - The user's input must match the specified string 
 */
void phase_1(char *input)
{
#if defined(PROBLEM)
    if (strings_not_equal(input, "SOME_STRING_SET") != 0)
	explode_bomb();
#elif defined(SOLUTION)
    printf("SOME_STRING_GET\n"); 
#else
    invalid_phase("1a");
#endif    
}

