#pragma once
/*
 * LinkPast native dual-hero vital state.
 * Plain integer data, no graphics, SDL, SNES RAM address or ROM dependency.
 * The active hero is represented in Zelda3's existing link_health_current
 * and link_magic_power; the inactive hero remains in a separate snapshot.
 * This is runtime practice-session data, not an extension of the save file.
 */
#include <stdbool.h>
#include <stdint.h>

enum {
  kLinkPastHeroLink = 0,
  kLinkPastHeroZelda = 1,
  kLinkPastHeroCount = 2,
};

typedef struct LinkPastHeroVitals {
  uint8_t hearts;
  uint8_t magic;
} LinkPastHeroVitals;

typedef struct LinkPastPartyVitals {
  LinkPastHeroVitals hero[kLinkPastHeroCount];
  uint8_t active;
  bool paired;
} LinkPastPartyVitals;

static inline void LinkPastParty_Clear(LinkPastPartyVitals *party) {
  for (unsigned i = 0; i < kLinkPastHeroCount; ++i) {
    party->hero[i].hearts = 0;
    party->hero[i].magic = 0;
  }
  party->active = kLinkPastHeroLink;
  party->paired = false;
}

static inline uint8_t LinkPastParty_Clamp(uint8_t value, uint8_t cap) {
  return value < cap ? value : cap;
}

static inline bool LinkPastParty_Start(LinkPastPartyVitals *party,
                                       unsigned active,
                                       uint8_t hearts, uint8_t magic,
                                       uint8_t heart_capacity) {
  if (active >= kLinkPastHeroCount || party->paired || heart_capacity == 0 ||
      hearts == 0) return false;
  uint8_t bounded_hearts = LinkPastParty_Clamp(hearts, heart_capacity);
  /* A fresh companion begins with the controlled hero's current, not full,
   * vitals. This avoids obtaining a free fully healed hero by pairing. */
  for (unsigned i = 0; i < kLinkPastHeroCount; ++i) {
    party->hero[i].hearts = bounded_hearts;
    party->hero[i].magic = magic;
  }
  party->active = (uint8_t)active;
  party->paired = true;
  return true;
}

static inline bool LinkPastParty_Switch(LinkPastPartyVitals *party,
                                        unsigned target,
                                        uint8_t current_hearts,
                                        uint8_t current_magic,
                                        uint8_t heart_capacity,
                                        LinkPastHeroVitals *next) {
  if (!party->paired || target >= kLinkPastHeroCount ||
      target == party->active || heart_capacity == 0 ||
      current_hearts == 0) return false;
  party->hero[party->active].hearts =
      LinkPastParty_Clamp(current_hearts, heart_capacity);
  party->hero[party->active].magic = current_magic;
  *next = party->hero[target];
  next->hearts = LinkPastParty_Clamp(next->hearts, heart_capacity);
  if (next->hearts == 0) return false;
  party->active = (uint8_t)target;
  return true;
}

static inline bool LinkPastParty_Stop(LinkPastPartyVitals *party,
                                      uint8_t current_hearts,
                                      uint8_t current_magic,
                                      uint8_t heart_capacity) {
  if (!party->paired) return false;
  party->hero[party->active].hearts =
      LinkPastParty_Clamp(current_hearts, heart_capacity);
  party->hero[party->active].magic = current_magic;
  party->paired = false;
  return true;
}
