#pragma once
/* LinkPast: integer-only orbit math for Zelda3's original ancilla system.
 * At 60 Hz, 54 frames = 0.9s; 32 angular steps = two revolutions.
 */
#include <stdint.h>

enum {
  kLinkPastOrbitFrames = 54,
  kLinkPastOrbitOutboundFrames = 12,
  kLinkPastOrbitRadius = 12,
};

static inline void LinkPast_OrbitOffset(unsigned angle, int *x, int *y) {
  static const int8_t xx[16] = {12,11,8,5,0,-5,-8,-11,-12,-11,-8,-5,0,5,8,11};
  static const int8_t yy[16] = {0,5,8,11,12,11,8,5,0,-5,-8,-11,-12,-11,-8,-5};
  *x = xx[angle & 15];
  *y = yy[angle & 15];
}

/* Choose the point on the circle behind its center relative to flight. */
static inline unsigned LinkPast_OrbitStartAngle(int8_t vx, int8_t vy) {
  if (vx > 0) return vy > 0 ? 10 : vy < 0 ? 6 : 8;
  if (vx < 0) return vy > 0 ? 14 : vy < 0 ? 2 : 0;
  return vy > 0 ? 12 : 4;
}

static inline unsigned LinkPast_OrbitAngle(unsigned start_angle, unsigned tick) {
  return (start_angle + (tick * 32u) / kLinkPastOrbitFrames) & 15u;
}

static inline void LinkPast_OrbitPosition(uint16_t cx, uint16_t cy,
                                           unsigned start_angle, unsigned tick,
                                           uint16_t *x, uint16_t *y) {
  int dx, dy;
  LinkPast_OrbitOffset(LinkPast_OrbitAngle(start_angle, tick), &dx, &dy);
  *x = (uint16_t)(cx + dx);
  *y = (uint16_t)(cy + dy);
}
