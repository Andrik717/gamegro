# CI helper scripts

The active Android build is defined in `.github/workflows/android.yml`. It packages the live project directly from `scripts/game.gd`, `game_data/story.json`, and `assets/`.

`patch_game.py`, `level_content.py`, and `chapter_mechanics.py` are legacy content-generation tools from an earlier prototype. They are not part of the active build. In particular, do not run `patch_game.py` against the current project: it rewrites the live gameplay script and targets the retired prototype.

The Android workflow compiles these Python files for syntax checking, but does not execute their content-generation steps.
