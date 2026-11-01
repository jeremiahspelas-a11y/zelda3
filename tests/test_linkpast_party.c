#include <assert.h>
#include <stdio.h>
#include "../src/linkpast_party.h"

int main(void) {
  LinkPastPartyVitals p = {0};
  LinkPastHeroVitals next = {0};

  /* Pairing does not grant a free refill. */
  assert(LinkPastParty_Start(&p, kLinkPastHeroZelda, 12, 73, 24));
  assert(p.active == kLinkPastHeroZelda);
  assert(p.hero[0].hearts == 12 && p.hero[1].hearts == 12);
  assert(p.hero[0].magic == 73 && p.hero[1].magic == 73);
  assert(!LinkPastParty_Start(&p, 0, 12, 73, 24));

  /* Zelda takes damage and spends magic. Link still has his own vitals. */
  assert(LinkPastParty_Switch(&p, kLinkPastHeroLink, 8, 21, 24, &next));
  assert(next.hearts == 12 && next.magic == 73);
  assert(p.hero[kLinkPastHeroZelda].hearts == 8);
  assert(p.hero[kLinkPastHeroZelda].magic == 21);
  assert(!LinkPastParty_Switch(&p, kLinkPastHeroLink, 12, 73, 24, &next));

  /* Link fights, then Zelda reappears with exactly her prior injuries. */
  assert(LinkPastParty_Switch(&p, kLinkPastHeroZelda, 5, 50, 24, &next));
  assert(next.hearts == 8 && next.magic == 21);
  assert(p.hero[kLinkPastHeroLink].hearts == 5);
  assert(p.hero[kLinkPastHeroLink].magic == 50);

  /* A later heart-capacity decrease cannot load invalid health. */
  assert(LinkPastParty_Switch(&p, kLinkPastHeroLink, 8, 20, 4, &next));
  assert(next.hearts == 4 && next.magic == 50);

  /* Never switch to an invalid hero or from zero HP. */
  assert(!LinkPastParty_Switch(&p, 2, 4, 50, 24, &next));
  assert(!LinkPastParty_Switch(&p, 1, 0, 50, 24, &next));

  assert(LinkPastParty_Stop(&p, 3, 19, 24));
  assert(!p.paired);
  assert(p.hero[kLinkPastHeroLink].hearts == 3);
  assert(p.hero[kLinkPastHeroLink].magic == 19);
  assert(!LinkPastParty_Switch(&p, 1, 3, 19, 24, &next));
  LinkPastParty_Clear(&p);
  assert(!p.paired && !p.hero[0].hearts && !p.hero[1].hearts);

  assert(!LinkPastParty_Start(&p, 2, 12, 73, 24));
  assert(!LinkPastParty_Start(&p, 0, 0, 73, 24));
  assert(!LinkPastParty_Start(&p, 0, 12, 73, 0));
  puts("PASS: hero vitals persist independently, no free healing on pairing");
  return 0;
}
