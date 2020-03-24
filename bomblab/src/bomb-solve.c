/*
 * bomb-solve.c - driver for a bomb that prints its own solution
 */
#include "phases.h"
#include "support.h"
#include <stdio.h>

FILE *infile;

int main() {
  char *input = "";

  initialize_bomb_solve();
  phase_1(input);
  phase_2(input);
  phase_3(input);
  phase_4(input);
  phase_5(input);
  phase_6(input);
  secret_phase();
  return 0;
}
