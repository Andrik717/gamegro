# CI helper scripts

The active Android build is defined in `.github/workflows/android.yml`. It packages the live project directly from `scripts/game.gd`, `game_data/story.json`, and `assets/`.

`normalize_jpeg_assets.py` is an active pre-import step. It re-encodes JPEG assets in the staged build copy to a conservative baseline JPEG format so Godot can import them reliably. To normalize a local checkout before opening it in Godot, install Pillow and run `python ci/normalize_jpeg_assets.py assets`.

`patch_game.py`, `level_content.py`, and `chapter_mechanics.py` are legacy content-generation tools from an earlier prototype. They are not part of the active build. In particular, do not run `patch_game.py` against the current project: it rewrites the live gameplay script and targets the retired prototype.

The Android workflow compiles all helper scripts for syntax checking, but does not execute the legacy content-generation steps.
