# Use after python3 install.py .; the normal engine stays source-compatible.
include Makefile

.PHONY: test-native-sandbox
test-native-sandbox: $(OBJS)
	sed 's/^\#undef main$$/\#undef main\n\#define main Zelda3GameMain/' src/main.c > tests/native_sandbox_main.inc
	$(CC) $(CFLAGS) -iquote src -UNDEBUG tests/native_sandbox_test.c $(filter-out src/main.o,$(OBJS)) -o tests/native_sandbox_test $(LDFLAGS) $(SDLFLAGS)
	./tests/native_sandbox_test
