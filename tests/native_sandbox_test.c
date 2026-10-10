/* Exercise patched host logic without a ROM, window, or audio device.
 * Only OS dialogs/window title and game audio/save I/O are replaced by spies. */
#define main Zelda3GameMain
#define SDL_ShowMessageBox TestMessageBox
#define SDL_SetWindowTitle TestWindowTitle
#define ZeldaRenderAudio TestRenderAudio
#define ZeldaDiscardUnusedAudioFrames TestDiscardAudio
#define SaveLoadSlot TestSaveLoadSlot
#include "native_sandbox_main.inc"
#undef main

static int test_choice, test_dialog_result, test_dialog_calls;
static int test_save_calls, test_discard_calls;
static char test_title[128];

int SDLCALL TestMessageBox(const SDL_MessageBoxData *data, int *choice) {
  assert(data->numbuttons == 4);
  test_dialog_calls++;
  *choice = test_choice;
  return test_dialog_result;
}
void SDLCALL TestWindowTitle(SDL_Window *window, const char *title) {
  (void)window;
  snprintf(test_title, sizeof(test_title), "%s", title);
}
void TestRenderAudio(int16 *buffer, int samples, int channels) {
  (void)buffer; (void)samples; (void)channels;
  assert(!"Test supplied audio should not require engine rendering");
}
void TestDiscardAudio(void) { test_discard_calls++; }
void TestSaveLoadSlot(int cmd, int which) {
  (void)cmd; (void)which;
  test_save_calls++;
}

int main(void) {
  assert(SDL_Init(0) == 0);
  g_audio_mutex = SDL_CreateMutex();
  assert(g_audio_mutex);

  g_sdl_audio_mixer_volume = 80;
  test_choice = 1;
  HandleCommand(kKeys_Controls + 5, true);
  assert(g_native_sandbox_active && g_sdl_audio_mixer_volume == 0);
  assert(!g_native_sandbox_start_pending && g_input1_state == 0);
  assert(strstr(test_title, "PRACTICE"));
  NativeSandboxSetActive(true);
  HandleCommand(kKeys_VolumeUp, true);
  assert(g_sdl_audio_mixer_volume == 0);
  for (uint32 command = kKeys_Save; command <= kKeys_Save_Last; command++)
    HandleCommand(command, true);
  assert(test_save_calls == 0);
  HandleCommand(kKeys_Load, true);
  assert(test_save_calls == 1);

  uint8 input[16], output[16];
  memset(input, 0x22, sizeof(input));
  memset(output, 0xff, sizeof(output));
  g_audiobuffer = g_audiobuffer_cur = input;
  g_audiobuffer_end = input + sizeof(input);
  AudioCallback(NULL, output, sizeof(output));
  for (size_t i = 0; i < sizeof(output); i++) assert(output[i] == 0);
  assert(g_audiobuffer_cur == g_audiobuffer_end && test_discard_calls == 1);

  test_choice = 2;
  assert(!NativeSandboxShowMenu());
  assert(!g_native_sandbox_active && g_sdl_audio_mixer_volume == 80);
  assert(strcmp(test_title, kWindowTitle) == 0);
  HandleCommand(kKeys_Save, true);
  assert(test_save_calls == 2);
  HandleCommand(kKeys_VolumeUp, true);
  assert(g_sdl_audio_mixer_volume > 80);

  test_choice = 0;
  HandleCommand(kKeys_Controls + 5, true);
  assert(g_native_sandbox_start_pending && g_input1_state == 0);
  HandleCommand(kKeys_Controls + 5, false);
  assert(g_native_sandbox_start_pending);
  g_native_sandbox_start_pending = false;
  assert(NativeSandboxShowMenu());
  test_choice = 3;
  assert(!NativeSandboxShowMenu());
  test_choice = -1;
  assert(!NativeSandboxShowMenu());
  test_dialog_result = -1;
  assert(!NativeSandboxShowMenu() && !g_native_sandbox_menu_open);
  test_dialog_result = 0;
  g_native_sandbox_menu_open = true;
  int calls = test_dialog_calls;
  assert(!NativeSandboxShowMenu() && test_dialog_calls == calls);
  g_native_sandbox_menu_open = false;

  g_sdl_audio_mixer_volume = SDL_MIX_MAXVOLUME;
  g_audiobuffer_cur = input;
  AudioCallback(NULL, output, sizeof(output));
  assert(memcmp(output, input, sizeof(input)) == 0);
  SDL_DestroyMutex(g_audio_mutex);
  SDL_Quit();
  puts("PASS: practice enter/leave, volume restore/mute, save guard, audio buffers, START, cancel/error/reentry");
  return 0;
}
