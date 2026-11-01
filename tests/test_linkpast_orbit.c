#include <assert.h>
#include <stdio.h>
#include "../src/linkpast_orbit.h"

static void path_case(int8_t vx, int8_t vy) {
  const uint16_t endx = 350, endy = 420;
  const unsigned start = LinkPast_OrbitStartAngle(vx, vy);
  int ox, oy;
  LinkPast_OrbitOffset(start, &ox, &oy);
  const uint16_t cx = (uint16_t)(endx - ox), cy = (uint16_t)(endy - oy);
  uint16_t x, y;
  LinkPast_OrbitPosition(cx, cy, start, 0, &x, &y);
  assert(x == endx && y == endy);
  int count = 0, changed = 0;
  uint16_t prevx = x, prevy = y;
  for (int frame = 0; frame < kLinkPastOrbitFrames; ++frame) {
    LinkPast_OrbitPosition(cx, cy, start, frame, &x, &y);
    if (x != prevx || y != prevy) changed++;
    int dx = (int)x - (int)cx, dy = (int)y - (int)cy;
    assert(dx >= -kLinkPastOrbitRadius && dx <= kLinkPastOrbitRadius);
    assert(dy >= -kLinkPastOrbitRadius && dy <= kLinkPastOrbitRadius);
    assert(dx * dx + dy * dy >= 100 && dx * dx + dy * dy <= 160);
    prevx = x; prevy = y; count++;
  }
  assert(count == 54 && changed >= 30);
  assert(LinkPast_OrbitAngle(start, 0) == LinkPast_OrbitAngle(start, 27));
  assert(LinkPast_OrbitAngle(start, 54) == start);
}
int main(void) {
  path_case(1, 0); path_case(-1, 0);
  path_case(0, 1); path_case(0, -1);
  path_case(1, 1); path_case(1, -1);
  path_case(-1, 1); path_case(-1, -1);
  puts("PASS: eight directions, entry continuity, two revolutions, bounded radius");
  return 0;
}
