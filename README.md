# IBC Video Studio — presenter quality-test redesign

## Important limitation
This is a fast 15-second *style and pipeline test*. It creates a stylized presenter from Blender primitives, a procedural port environment, and both landscape and vertical compositions. It is **not yet a cinematic rigged character** and does not include true facial lip-sync. Approve the composition/pipeline before adding a properly licensed rigged character model.

## Files to add/replace in your existing repository
- Replace `.github/workflows/render-video.yml` with the version in this package.
- Add `scripts/ibc_presenter_test.py`.
- Add `data/narration.txt`.

The old `scripts/ibc_intro.py` and existing source files are not deleted; this new workflow uses the new test script only.

## Run
1. Commit these files to the existing repository.
2. Open **Actions → Render IBC Presenter Quality Test → Run workflow**.
3. Choose `both` for landscape and vertical previews.
4. Download the `ibc-presenter-quality-test` artifact from the completed run.

## Why it should be faster
- 15 seconds at 12 fps = 180 frames per format, versus the previous 720-frame 30-second render.
- Reduced Eevee samples and `ultrafast` FFmpeg encoding.
- It creates a short validation clip before attempting long videos.

## Audio/captions
The workflow uses Edge TTS voice `en-IN-NeerjaNeural` and requests subtitles from the same narration generation command, so caption timings are based on generated speech. Voice availability depends on the Edge TTS service and can change.

## Before production
Replace the primitive placeholder presenter with a licensed rigged character and add real gestures/facial lip-sync. Confirm the voice, subtitle timing, composition and render duration first. Then build the longer 10–30 minute scene pipeline.
