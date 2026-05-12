# Capability Rubric

## Image Generation

**Tools**: `generate_image`, `lora_generation`, `kontext_lora`

| Criterion | Success |
|-----------|---------|
| Output format | JSON with `"success": true` and `"result"` array of image URLs |
| File delivered | URLs resolve to valid PNG/JPG/WebP images |
| URL returned | At least one downloadable image URL in result array |
| Parameters | Correct model selected, prompt passed, num_images respected |
| Error handling | On failure: `"success": false` with actionable error message |

## Video Generation

**Tools**: `generate_video`, `video_modify`, `video_portrait`, `video_avatar`

| Criterion | Success |
|-----------|---------|
| Output format | Background mode: JSON with `"task_id"`. Completion: JSON with `"success": true` and result URL |
| File delivered | URL resolves to valid MP4 video |
| URL returned | Single downloadable video URL in result |
| Async workflow | Task submitted, task_id saved, status polled via `--check-task`, result delivered to user |
| Parameters | Model, duration, prompt, and reference inputs correctly passed |
| Error handling | On failure: `"success": false` with error; on timeout: task_id preserved for later check |

## Image Processing

**Tools**: `upscale_image`, `remove_background`, `replace_background`, `image_resize` (含旧 `image_extend` 能力), `image_remove_lighting`, `face_swap`, `correct_yellow_tint`

| Criterion | Success |
|-----------|---------|
| Output format | JSON with `"success": true` and `"result"` array of image URLs |
| File delivered | URLs resolve to valid processed images (PNG/JPG/WebP) |
| URL returned | At least one downloadable image URL in result array |
| Input handling | Local files converted via `--file`, URLs passed directly in `--params` |
| Transformation | Output visibly reflects the requested operation (higher res, no bg, extended canvas, etc.) |
| Error handling | On failure: `"success": false` with error; file-not-found errors clearly reported |

## Video Processing

**Tools**: `video_upscale`, `video_lipsync`, `video_reframe`, `video_speed`, `video_remove_background`, `video_compression`, `video_to_audio`

| Criterion | Success |
|-----------|---------|
| Output format | Background mode: JSON with `"task_id"`. Completion: JSON with `"success": true` and result URL |
| File delivered | URL resolves to valid processed MP4 video (or audio for `video_to_audio`) |
| URL returned | Single downloadable media URL in result |
| Async workflow | Task submitted, task_id saved, status polled, result delivered |
| Transformation | Output reflects requested operation (upscaled, synced audio, changed speed, etc.) |
| Error handling | On failure: `"success": false` with error; on timeout: task_id preserved |
