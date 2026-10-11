# IBC Video Studio

A separate, code-first Blender project for generating IBC's 30-second global import-export introduction. It does **not** modify or depend on the existing EXIM AI repository.

## What it produces

- Vertical 9:16 3D animation (720 × 1280 master render for a practical cloud-runner starting point)
- English voice-over generated during GitHub Actions using `edge-tts`
- English captions burned into the final MP4
- Final video saved as a downloadable GitHub Actions artifact

The first version uses procedural Blender objects and text, so no paid 3D assets are needed.

## Create the repository

1. On GitHub, create a **new, separate** repository named `IBC-Video-Studio`.
2. Upload these files to the new repository, preserving their folder paths, or push them with Git.
3. Open **Actions** and enable workflows if GitHub asks.
4. Select **Render IBC Intro Video** → **Run workflow**.
5. When it finishes, open the run and download the `ibc-intro-video` artifact.

The workflow is manual-only by default to avoid spending runner minutes on every commit.

## Customise before publishing

- Replace `YOUR_WHATSAPP_NUMBER` in `scripts/narration.txt` and `scripts/captions.srt` with your public business WhatsApp number.
- Review all service claims and the narration before publishing.
- Change the scene text and timings in `scripts/ibc_intro.py`.
- Edit `scripts/narration.txt` and `scripts/captions.srt` together so the spoken audio and subtitles stay aligned.
- For a logo, add a transparent PNG under `assets/` and extend the Blender script to load it.

## Important notes

- This workflow depends on network access to install Blender/FFmpeg and fetch the English voice from Microsoft Edge TTS. If that service is unavailable, the run may fail at the narration step.
- GitHub-hosted runners are CPU-based here; the first render can take a while. This starter intentionally uses Eevee and a 720 × 1280 master. Upscaling the final video does not add detail; increase Blender resolution only after testing render time.
- The Blender render is an animated brand explainer, not a photorealistic simulation of real shipping operations.
- No WhatsApp number is included yet. Replace the placeholder before publishing.
