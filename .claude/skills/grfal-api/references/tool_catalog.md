# GRFal Tool Catalog - Detailed Parameters

Complete parameter reference for ~53 user-facing GRFal API tools. Admin-only pipeline tools (`comic_*`, `drama_*`, `cf_*`) are not listed here — query `GET /api/tools` for those.

> Call any tool via: `python call_grfal.py --tool <name> --params '<json>' [--file key=path]`

## Image Generation

### generate_image
Text-to-image and image-to-image generation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Text prompt describing the image |
| reference_images | List[str] | [] | Reference images (URLs or base64). Use `--file reference_images=path` |
| model | str | "gpt" | Model: gpt (gpt-image-2, default), gemini, grok, flux, seedream, qwen, wan, runway, vidu, kling, ideogram, hunyuan, zimage, **firered** (image-edit only, needs ≥1 ref) |
| num_images | int | 2 | Number of images to generate |
| aspect_ratio | str / None | None | 可选指定（`landscape_16_9` / `portrait_16_9` / `landscape_4_3` / `portrait_4_3` / `square_hd` / `landscape_21_9` / `portrait_21_9`）。**留空 / `"auto"` / `""` 都走 LLM 据 prompt 自动推断**（前端永远传 `"auto"` 是为了对齐 Gradio 严格 input 校验）。非法值由 normalize_aspect_ratio 兜底。 |

```bash
# Text-to-image
python call_grfal.py --tool generate_image --params "{\"prompt\": \"a cute cat\", \"model\": \"gemini\"}"

# Image-to-image (with reference)
python call_grfal.py --tool generate_image --params "{\"prompt\": \"make it more colorful\"}" --file reference_images=input.png

# FireRed Edit (image-only, 1-7 reference images required, good for portrait makeup / style transfer / element fusion)
python call_grfal.py --tool generate_image --params "{\"prompt\": \"add natural makeup and enhance skin tone\"}" --file reference_images=portrait.png

# ZImage (text-to-image only, NSFW-capable realistic model with built-in LoRA)
# Best for: photorealistic portraits, candid snapshots, film grain aesthetic
# Reference prompt: "amateur digital snapshot, candid, smartphone capture, high ISO noise, direct on-camera flash, visible pores, detailed skin texture. A beautiful young woman with a realistic natural body taking a mirror selfie in a dimly lit motel bathroom. She is completely nude, displaying highly detailed and accurate anatomical features, natural skin imperfections and subtle sweat. Messy hair, intimate and raw erotic atmosphere, slight lens distortion, uncensored"
python call_grfal.py --tool generate_image --params "{\"prompt\": \"amateur digital snapshot, visible pores, detailed skin texture. A woman posing in natural light\", \"model\": \"zimage\", \"num_images\": 1}"
```

### lora_generation
Generate images using LoRA presets.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Text prompt |
| reference_images | List[str] | [] | Reference images (max 1, for depth/canny control only) |
| preset | str | required | LoRA preset name |
| model | str | "flux_dev" | Model: flux_dev, flux_pro, qwen, flux2, z_image |
| ref1_type | str | "参考构图" | Reference type: 参考构图 (depth), 参考轮廓 (canny) |

### kontext_lora
Kontext style transfer with LoRA presets.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Input images. Use `--file image_paths=path` |
| preset | str | required | Kontext preset (e.g., "Kontext X2风格", "Kontext P2徽章") |

### image_batch_edit
Batch-edit a list of images with the same prompt (and optional shared reference images).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images to edit. Use `--file image_paths=path` |
| multimodal | dict | required | `{"text": "<prompt>", "files": [<optional_ref_paths>]}`. Files are shared refs added to every edit |
| model_type | str | "gpt" | Model: gpt (default, gpt-image-2), gemini, flux, ... — same matrix as `generate_image` |

```bash
python "<skill_path>/scripts/call_grfal.py" --tool image_batch_edit \
  --params "{\"multimodal\": {\"text\": \"add subtle film grain and warm tones\", \"files\": []}, \"model_type\": \"gpt\"}" \
  --file image_paths=a.png --file image_paths=b.png --file image_paths=c.png
```

### image_mask_edit
Local edit by binary mask (gpt-image-2 mask edit). Mask is RGBA PNG: alpha > 0 = edit, alpha == 0 = preserve. Server composites the result with the original outside the masked region (FAL gpt-image-2/edit otherwise repaints whole image).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_path | str | required | Source image. Use `--file image_path=path` |
| mask_path | str | required | RGBA PNG mask. Use `--file mask_path=path` |
| multimodal | dict | required | `{"text": "<prompt>", "files": []}` |
| model_type | str | "gpt" | Model (only gpt is well-validated for mask edit) |
| num_images | int | 1 | Number of variants |

### image_erase
Erase the masked region (no prompt, no replacement — pure inpainting fill). Local LaMa-style fallback after FAL.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_path | str | required | Source image. Use `--file image_path=path` |
| mask_path | str | required | RGBA PNG. alpha > 0 = erase target. Use `--file mask_path=path` |

### generate_panorama
360° equirectangular panorama. Fixed 2:1 / 2048×1024. Backends: fal → azure (gpt-image-2). Use a photo-sphere viewer to browse.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| multimodal | dict | required | `{"text": "<scene description>", "files": [<optional_ref>]}`. Optional ref guides composition |

```bash
python "<skill_path>/scripts/call_grfal.py" --tool generate_panorama \
  --params "{\"multimodal\": {\"text\": \"sunrise over a misty alpine lake, photorealistic equirectangular 360 panorama\", \"files\": []}}"
```

---

## Image Processing

### liveportrait
Adjust face expressions. All params range -1.0 to 1.0 (0 = no change); wink is 0.0 to 1.0.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Face images. Use `--file image_paths=path` |
| rotate_pitch | float | 0 | Pitch rotation (nodding), -1~1 |
| rotate_yaw | float | 0 | Yaw rotation (shaking head), -1~1 |
| rotate_roll | float | 0 | Roll rotation (tilting head), -1~1 |
| blink | float | 0 | Blink, -1~1 |
| eyebrow | float | 0 | Eyebrow raise/lower, -1~1 |
| wink | float | 0 | Single-eye wink, 0~1 |
| pupil_x | float | 0 | Pupil horizontal shift, -1~1 |
| pupil_y | float | 0 | Pupil vertical shift, -1~1 |
| aaa | float | 0 | Mouth open (aaa), -1~1 |
| eee | float | 0 | Mouth shape (eee), -1~1 |
| woo | float | 0 | Mouth shape (woo), -1~1 |
| smile | float | 0 | Smile, -1~1 |

### upscale_image
Image super-resolution.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images to upscale. Use `--file image_paths=path` |
| model | str | None | Model: SeedVR, Crystal, Topaz, Recraft, Ideogram, Sima, Flux |
| scale | int | 2 | Upscale factor |

### remove_background
AI background removal.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| add_edge | bool | false | Add white edge around subject |

### replace_background
Replace background with AI-generated one.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| background_prompt | str | required | Description of new background |
| light_direction | str | "无" | Light direction for compositing |

### image_resize
Unified resize / outpaint entry. Auto-routes to one of three paths based on input
(transparent to caller):

- **Transparent PNG** → local PIL (preserves alpha)
- **Safe-zone preset (X2双端 / P2双端) or explicit safe_width/safe_height** → AI edge fill
  via `fal-ai/gpt-image-2/edit` (game art "phone + pad" dual-screen adaptation)
- **Other** → `fal-ai/smart-resize` (2K nano-banana-pro recomposition)

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| preset | str | "" | Aspect preset (overrides width/height). One of: `1:1` `16:9` `9:16` `4:3` `3:4` `4:5` `5:4` `X2双端` `P2双端` |
| width | int | 0 | Target width (px). Required when preset is empty |
| height | int | 0 | Target height (px). Required when preset is empty |
| safe_width | int | 0 | Safe-zone width. Non-zero enables dual-screen mode (main visual fits inside, edges AI-filled) |
| safe_height | int | 0 | Safe-zone height. Used together with safe_width |

**Examples**
- Resize to 1080×1920: `preset=9:16` (or `width=1080 height=1920`)
- X2 dual-screen adaptation: `preset=X2双端` (auto: 1440×1920 + safe 1080×1920)
- Custom dual-screen: `width=1600 height=2400 safe_width=1200 safe_height=2400`

### image_remove_lighting
Remove uneven lighting, restore uniform illumination.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |

### image_group_photo
Multi-character composite photo.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Character images. Use `--file image_paths=path` |
| prompt | str | required | Scene description |

### face_swap
Face swap - replace the head in a body image with a face from a reference image. Supports multiple models.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| body_image | str | required | Body image (the base image to keep). Use `--file body_image=path` |
| face_image | str | required | Face reference image (head to transplant). Use `--file face_image=path` |
| model | str | "HY-WU Edit (默认)" | Model: "HY-WU Edit (默认)" (best quality), "Flux LoRA", "Qwen 2511 LoRA" |
| prompt | str | (see below) | Swap instruction prompt. Can be customized for specific needs |

**Models:**
- **HY-WU Edit (默认)**: Native image editing model, best overall quality, safety checker disabled
- **Flux LoRA**: Flux Klein 9B + custom head_swap LoRA
- **Qwen 2511 LoRA**: Qwen image edit + custom head_swap LoRA

**Default prompt** (recommended, produces best results):
```
head_swap: start with Picture 1 as the base image, keeping its lighting, environment, and background. remove the head from Picture 1 completely and replace it with the head from Picture 2, strictly preserving the hair, eye color, nose structure of Picture 2. copy the direction of the eye, head rotation, micro expressions from Picture 1, high quality, sharp details, 4k. Describe the expression in Picture 1 and copy it to the new image.
```

```bash
# Face swap with default model (HY-WU Edit, recommended)
python call_grfal.py --tool face_swap --file body_image=body.png --file face_image=face.png

# Face swap with specific model
python call_grfal.py --tool face_swap --file body_image=body.png --file face_image=face.png --params "{\"model\": \"Flux LoRA\"}"

# Face swap with custom prompt
python call_grfal.py --tool face_swap --file body_image=body.png --file face_image=face.png --params "{\"prompt\": \"head_swap: replace the head in Picture 1 with the face from Picture 2, keep the hairstyle from Picture 2, match the lighting of Picture 1\"}"
```

### image_camera_angle
Change camera viewing angle.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| horizontal_angle | float | 0 | Horizontal rotation angle |
| vertical_angle | float | 0 | Vertical rotation angle |

### image_keyframe
Generate video keyframes/storyboards.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Reference images. Use `--file image_paths=path` |
| prompt | str | required | Keyframe description |

### image_layered
AI automatic layer separation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images to separate. Use `--file image_paths=path` |

### image_split
Split image into sub-images and upscale each.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |

---

## Video Generation

### generate_video
Text-to-video and image-to-video generation with advanced control modes.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Video description |
| reference_images | List[str] | [] | Reference images/videos. Use `--file reference_images=path` (can specify multiple times) |
| ref_types | str | "" | Reference types (comma-separated): "首帧图像,尾帧图像,元素参考,参考视频". If omitted, first image defaults to 首帧, others to 元素参考 |
| model | str | required | Model: seadance, hailuo, veo3, sora, vidu, kling, wan, runway, **grok**, **happyhorse** |
| duration | int | varies | Duration in seconds (model-dependent, see notes below) |
| aspect_ratio | str / None | None | 可选指定（"16:9" / "9:16" / "21:9" / "9:21" 等）。**留空 / `"auto"` / 脏值都走自动推断**（prompt 显式比例 → 参考素材尺寸 → LLM 推断，依次降级）。前端约定永远传 `"auto"` 来对齐 Gradio 严格 input 校验。 |

**Advanced Control Modes:**
- **首帧 (First Frame)**: Control starting frame only
- **首尾帧 (fflf)**: Control both start and end frames
- **元素参考 (Element)**: Insert specific elements/characters into video
- **fflf + 元素 (fflf_element)**: Kling only - combine start/end frames + element references
- **参考视频 (Video Reference)**: Generate video from reference video (max 10s for Kling, 15s for Seadance)
- **参考音频 (Audio Reference)**: Seadance 2.0 only - reference audio for voice/music/sound cloning

**Model Notes:**
- **seadance** (即梦豆包2.0, Seedance 2.0): Most versatile model. Supports all modes + audio reference + web search.
  - **Multimodal reference**: Mix up to 9 images + 3 videos + 3 audio files in a single request
  - **Audio reference** (`ref_types` includes "参考音频"): Clone voice timbre, music melody, or dialogue from audio files (.wav/.mp3)
  - **Video editing**: Upload source video as "参考视频" + optional ref images + edit instructions in prompt (e.g., "replace X with Y in 视频1")
  - **Video extending**: Upload 1-3 video clips as "参考视频" + transition descriptions to stitch them into a continuous video
  - **Web search**: Automatically enabled for text-only mode; model decides whether to search based on prompt
  - Duration: 4-15s (auto by default), aspect ratios: 21:9/16:9/4:3/1:1/3:4/9:16
  - Generates audio by default (video includes sound)
  - Prompt format: use "图片N", "视频N", "音频N" to reference the Nth image/video/audio in order
- **grok** (Grok Imagine Video by xAI): Element/reference mode only — multi-reference images to video (up to 4 images). No text-only or single first-frame mode.
- **happyhorse** (阿里百炼 HappyHorse 1.0): 全模式视频生成（text/ff/element/video_reference）。视频默认带音频直出（不可关闭推理音频）。
  - **t2v** (text-to-video): 文生视频，prompt 必填
  - **i2v** (ff, image-to-video): 首帧图生视频
  - **r2v** (element): 元素参考，最多 9 张参考图
  - **video-edit** (video_reference): 视频改写，可选附加参考图（双入口：generate_video with ref_types="参考视频" 或 video_modify）
  - Duration: 3-15s (integer), 分辨率 720P/1080P (默认 1080P)
  - Backends: aliyun (主，全模式) + fal failover (仅 text/ff，element/video_reference 仅 aliyun)
  - 账号需在百炼控制台申请加白后激活；watermark 默认 false（true 在右下角加 "Happy Horse" 字样）
- For video files, they will be auto-detected as videos; set `ref_types` to "参考视频"
- For audio files (.wav/.mp3), they will be auto-detected; `ref_types` auto-set to "参考音频" (Seadance only)
- **vidu**: Supports text, first-frame, first+last-frame (fflf), element reference (up to 7 images), and video reference (up to 4 images + 2 videos).
  - Element mode uses viduq3-mix (strongest multi-entity consistency, audio output enabled by default)
  - fflf mode uses viduq3-pro (audio output enabled by default)
  - Video reference mode uses viduq2-pro (only model supporting video references)
  - Duration: 1-16s (q3), 0-10s (q2-pro). Aspect ratios: 16:9, 9:16, 4:3, 3:4, 1:1
- Kling model supports advanced features such as fflf_element and video_reference

```bash
# Text-to-video
python call_grfal.py --tool generate_video --params "{\"prompt\": \"a cat walking\", \"model\": \"kling\"}" --timeout 600

# Image-to-video (first frame control)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"camera slowly pans\", \"model\": \"kling\"}" --file reference_images=keyframe.png --timeout 600

# First + last frame control (fflf)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"smooth transition\", \"model\": \"kling\", \"ref_types\": \"首帧图像,尾帧图像\"}" --file reference_images=start.png --file reference_images=end.png --timeout 600

# First frame + element reference (fflf_element, Kling only)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"character walks through scene\", \"model\": \"kling\", \"ref_types\": \"首帧图像,元素参考,元素参考\"}" --file reference_images=bg.png --file reference_images=char1.png --file reference_images=char2.png --timeout 600

# Video reference mode (video-to-video)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"make it more cinematic\", \"model\": \"kling\", \"ref_types\": \"参考视频\", \"duration\": 10}" --file reference_images=input.mp4 --timeout 600

# Grok Imagine - multi-reference element mode (up to 4 images)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"the characters interact in an epic battle scene\", \"model\": \"grok\", \"ref_types\": \"元素参考,元素参考\"}" --file reference_images=char1.png --file reference_images=char2.png --timeout 600

# Seedance 2.0 - multimodal reference (images + video + audio)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"参考图片1的角色形象，使用视频1的运镜方式，音色参考音频1\", \"model\": \"seadance\", \"ref_types\": \"元素参考,参考视频,参考音频\"}" --file reference_images=character.png --file reference_images=camera_ref.mp4 --file reference_images=voice_ref.mp3 --timeout 600

# Seedance 2.0 - video editing (replace object in video)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"将视频1中的香水替换成图片1中的面霜，运镜不变\", \"model\": \"seadance\", \"ref_types\": \"参考视频,元素参考\"}" --file reference_images=source_video.mp4 --file reference_images=replacement.png --timeout 600

# Seedance 2.0 - video extending (stitch 2-3 clips)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"视频1画面结束后，镜头转场进入室内，接视频2\", \"model\": \"seadance\", \"ref_types\": \"参考视频,参考视频\"}" --file reference_images=clip1.mp4 --file reference_images=clip2.mp4 --timeout 600

# HappyHorse - text-to-video (t2v)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"a horse galloping across a sunset prairie, cinematic\", \"model\": \"happyhorse\", \"duration\": 5}" --timeout 600

# HappyHorse - image-to-video (i2v / 首帧)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"the character starts to dance gracefully\", \"model\": \"happyhorse\", \"duration\": 5}" --file reference_images=keyframe.png --timeout 600

# HappyHorse - element reference (r2v, max 9 images)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"角色在城市夜景中奔跑\", \"model\": \"happyhorse\", \"ref_types\": \"元素参考,元素参考\"}" --file reference_images=char.png --file reference_images=scene.png --timeout 600

# HappyHorse - video edit (video_reference)
python call_grfal.py --tool generate_video --params "{\"prompt\": \"换成赛博朋克风格的霓虹夜景\", \"model\": \"happyhorse\", \"ref_types\": \"参考视频\"}" --file reference_images=input.mp4 --timeout 600
```

---

## Video Processing

### video_upscale
Video super-resolution (2x upscale).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| model | str | varies | Upscale model |

### video_modify
Modify video style or elements (video editing with AI).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| prompt | str | required | Modification description |
| model | str | varies | Model: kling, wan, runway, happyhorse |
| reference_images | List[str] | [] | Optional reference images for style/element control |

**Model Notes:**
- Kling: Uses o3/pro model, max 10s duration, supports reference images
- Wan: Video editing with style transfer
- Runway: Video-to-video transformation
- HappyHorse (阿里百炼 video-edit): max 15s, 等价于 generate_video + ref_types="参考视频"

```bash
# Basic video style modification
python call_grfal.py --tool video_modify --params "{\"prompt\": \"make it look like watercolor painting\", \"model\": \"kling\"}" --file video_path=input.mp4 --timeout 600

# Video editing with reference image
python call_grfal.py --tool video_modify --params "{\"prompt\": \"transfer the style\", \"model\": \"kling\"}" --file video_path=input.mp4 --file reference_images=style_ref.png --timeout 600
```

### video_to_audio
Generate audio/soundtrack for video.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| prompt | str | "" | Audio description |

### video_lipsync
Synchronize lip movements with audio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| audio_path | str | required | Audio file. Use `--file audio_path=path` |
| sync_mode | str | "latentsync" | `latentsync`=高质量(慢), `lipsync`=快速(质量稍低) |

### video_portrait
Video-driven character animation / motion transfer.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_path | str | required | Character image (single). Use `--file image_path=path` |
| video_path | str | required | Driving video. Use `--file video_path=path` |
| portrait_mode | str | required | `视频替换角色`=用图片替换视频中的人物, `视频动作驱动图片`=用视频动作驱动静态图片 |

### video_avatar
Audio-driven avatar animation. Generates a talking video by driving a character image with audio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_path | str | required | Character image (single). Use `--file image_path=path` |
| audio_path | str | required | Audio file (mp3/wav). Use `--file audio_path=path` |
| prompt | str | "" | Optional video description |

### video_reframe
Change video aspect ratio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| target_ratio | str | required | Target: 16:9, 9:16, 1:1, 4:3, 3:4 |

### video_remove_background
Remove video background.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |

### video_speed
Change video playback speed.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| speed | float | required | Speed multiplier: 0.25 to 4.0 (1.0 = original, >1 faster, <1 slower) |

### video_remove_watermark
Automatically detect and remove watermarks from video. Uses LLM vision to detect watermark positions on the first frame, then calls bria video eraser to remove them.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |

```bash
python call_grfal.py --tool video_remove_watermark --file video_path=watermarked.mp4 --timeout 600
```

### export_sbs_video
Export side-by-side transparent video (for Unity).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| input_videos | List[str] | required | Videos to export. Use `--file input_videos=path` |
| quality | int | required | Output quality |

### video_inpainting
Erase a moving object from a video by describing it (LLM finds it on the first frame, Bria video eraser removes across all frames).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Source video. Use `--file video_path=path` |
| mask_prompt | str | required | Description of what to erase, e.g. "the red car in the foreground" |
| enable_pass2 | bool | false | Run a second cleanup pass for stubborn artifacts (slower) |
| num_inference_steps | int | 30 | Sampling steps (10-50) |

```bash
python "<skill_path>/scripts/call_grfal.py" --tool video_inpainting \
  --params "{\"mask_prompt\": \"the floating microphone in the center\"}" --file video_path=interview.mp4 --timeout 900
```

---

## Utility & Special

### virtual_tryon
Virtual clothes try-on.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| model_image | str | required | Model/person image. Use `--file model_image=path` |
| garment_image | str | required | Garment image. Use `--file garment_image=path` |

### describe_media
Describe image or video content using AI. Returns a text description.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| media_path | str | required | Image or video. Use `--file media_path=path` |
| media_type | str | "auto" | Force type: auto, image, video |

### seedance_prompt_reverse
Reverse-engineer a Seedance 2.0 multi-shot timestamp prompt from an existing video. Uses two analysis passes (motion + per-shot detail) and merges them programmatically.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Source video. Use `--file video_path=path` |

Returns a string formatted as Seedance 2.0 expects: `[0-2s] ... [2-5s] ... [5-8s] ...`. Feed it back into `generate_video` with `model="seadance"`.

### synthesize_card
Card compositing (content + frame overlay). Uses @batch_image_process decorator.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| content_image_path | str | required | Content image. Use `--file content_image_path=path` (or image_paths for batch) |
| frame_image_path | str | required | Frame image (with transparent holes). Use `--file frame_image_path=path` |

### correct_yellow_tint
Fix yellow color cast in images.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| strength | int | required | Correction strength |
| red_adj | int | required | Red channel adjustment |
| green_adj | int | required | Green channel adjustment |
| blue_adj | int | required | Blue channel adjustment |
| saturation_adj | int | required | Saturation adjustment |

### vector_generation
Generate vector graphics (SVG).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Description |
| jfile | str | required | Template name |
| size | str | required | Output size |

### screenshot_localization
Multi-language screenshot localization. Uses GPT Image 2, outputs at platform-native dimensions.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Screenshots. Use `--file image_paths=path` |
| languages | List[str] | required | Language codes: ru-RU, en-US, fr-FR, de-DE, id, it-IT, pt-PT, es-ES, ja-JP, ko-KR, zh-TW, ar-SA, tr-TR, vi-VN, th-TH, pt-BR, es-MX, ms-MY, hi-IN, zh-HK, fil-PH |
| platform | str | required | Platform: android, ios, ipad |
| extra_prompt | str | "" | Additional localization instructions |

### pdf_enhancement
PDF text clarity enhancement (via Gemini).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| pdf_file | str | required | PDF file. Use `--file pdf_file=path` |
| custom_prompt | str | None | Custom enhancement prompt |
| max_concurrency | int | 4 | Max parallel processing |

### pdf_compression
Compress PDF file size.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| pdf_file | str | required | PDF file. Use `--file pdf_file=path` |
| image_quality | int | 75 | Image quality (1-100) |
| compress_images | bool | true | Whether to compress images |
| max_image_size | int | None | Max image dimension in pixels |
| remove_metadata | bool | true | Remove metadata |

---

## 3D & Training

### generate_3d
3D model generation from image.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | [] | Reference images (for image-to-3D). Use `--file image_paths=path` |
| model | str | required | Model: hunyuan, rodin, meshy, tripo_v31, tripo_p1, trellis |
| face_limit | int | varies | Max face count for mesh |

**Model details:**

| Model | Output | Face Limit | Notes |
|-------|--------|------------|-------|
| hunyuan | FBX | 10k-1500k | 支持多视角(最多4张图)，推荐 |
| rodin | FBX | 阈值映射 | 多图合成(最多7张)，质量可控 |
| meshy | FBX | 100-300k | 支持多视角(最多4张) |
| tripo_v31 | FBX | 48-2000k | Tripo 3.1，雕塑级精度，支持多视角(4张)，geometry_quality/quad 等 |
| tripo_p1 | GLB | 48-20000 | Tripo P1，低多边形，支持多视角(4张)，~2秒出网格 |
| trellis | FBX | 100k-2000k | 单图生成 |

```bash
# Tripo 3.1 (高精度FBX)
python call_grfal.py --tool generate_3d --params "{\"model\": \"tripo_v31\", \"face_limit\": 100000}" --file image_paths=input.png

# Tripo P1 (低多边形GLB，快速)
python call_grfal.py --tool generate_3d --params "{\"model\": \"tripo_p1\", \"face_limit\": 5000}" --file image_paths=input.png
```

### reduce_face
Reduce 3D model face/polygon count (uses Tencent Hunyuan 3D).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| model_file | str | required | 3D model file (GLB/OBJ). Use `--file model_file=path` |

### train_model
LoRA model training.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| zip_file | str | required | Training data ZIP. Use `--file zip_file=path` |
| mode | str | required | Training mode |
| trigger_word | str | "" | LoRA trigger word |

### query_training_status
Poll FAL training task status.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| model_name | str | required | FAL model id, e.g. `fal-ai/flux-pro-trainer` or `fal-ai/flux-lora-fast-training` |
| request_id | str | required | The request_id returned by `train_model` |

### generate_motion
Text-to-3D-motion (humanoid animation clip).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Action description, e.g. "a person walks forward and waves" |
| duration | float | 5.0 | Clip length in seconds |
| guidance_scale | float | 5.0 | Prompt adherence |
| seed | int | 0 | Random seed (0 = random) |

### generate_pbr_material
Generate or extract PBR material maps (albedo / normal / roughness / metallic / height). Three modes via `image_role`:
- `提取材质` (default with image): photo → tileable PBR
- `生成PBR通道` (with texture image): existing color texture → PBR channels
- (no image, prompt-only): text → tileable PBR

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| multimodal | dict | required | `{"text": "<material description>", "files": [<optional_image>]}` |
| image_role | str | "提取材质" | "提取材质" or "生成PBR通道" |
| tiling_mode | str | "both" | "both" / "horizontal" / "vertical" / "none" |
| upscale_factor | int | 0 | 0=no upscale, 2/4 = post upscale |

---

## Creative Workflows

### creative_workflow
End-to-end creative pipeline (character design, PPT, game sprite sheet, etc.).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| user_input | str | required | Creative brief/instructions |
| tool_id | str | "ppt_generation" | Workflow: **sprite_sheet**, p2_fighter_design, x2_hero_design, p2_festival_design, p2_carrier_design, p2_mech_design, p2_mech_skin_design, ppt_generation |
| reference_files | List[str] | [] | Reference files. Use `--file reference_files=path` |

**sprite_sheet** — AI 生成游戏角色多动作精灵图（sheet-first 流水线）：
- 模型一次性出整张 N×M 网格 sheet（洋红 #FF00FF 底色）→ 本地色键扣背景 → 切帧 → baseline 对齐 → 拼合干净 sheet + 单帧透明 PNG
- 同一角色所有动作一次出图，避免逐帧漂移（待机/行走/攻击/死亡等）
- 可上传参考图作为角色外观基础（使用 `--file reference_files=path`）

```bash
# 游戏角色精灵图（纯文字描述）
python call_grfal.py --tool creative_workflow \
  --params "{\"tool_id\": \"sprite_sheet\", \"user_input\": \"一个中世纪骑士，需要待机、行走、攻击、死亡四个动作\"}" \
  --timeout 600

# 带参考图（以自有角色图为基础）
python call_grfal.py --tool creative_workflow \
  --params "{\"tool_id\": \"sprite_sheet\", \"user_input\": \"这个角色，生成待机、行走、攻击三个动作\"}" \
  --file reference_files=my_character.png \
  --timeout 600

# 其他 creative_workflow 示例
python call_grfal.py --tool creative_workflow --params "{\"user_input\": \"design a sci-fi mech\", \"tool_id\": \"p2_mech_design\"}" --timeout 600
```

---

## Local Processing Tools

### video_compression
Compress video using H.265/HEVC encoding via ffmpeg.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_file | str | required | Input video file. Use `--file video_file=path` |
| crf | int | 28 | Quality control (0-51). Higher = smaller file, lower quality |
| preset | str | "slower" | Encoding speed preset: ultrafast/superfast/veryfast/faster/fast/medium/slow/slower/veryslow |
| max_height | int | 1080 | Max output height in pixels (1080 = 1080p) |
| audio_bitrate | str | "64k" | Audio bitrate (32k/64k/96k/128k/192k) |

```bash
python call_grfal.py --tool video_compression --file video_file=input.mp4
python call_grfal.py --tool video_compression --file video_file=input.mp4 --params "{\"crf\": 24, \"preset\": \"slow\", \"max_height\": 720}"
```

### extract_video_frames
Extract first/last/keyframes from a video via local ffmpeg.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_file | str | required | Input video. Use `--file video_file=path` |
| extract_first | bool | true | Extract first frame |
| extract_last | bool | true | Extract last frame |
| extract_keyframes | bool | true | Extract I-frame keyframes |
| max_keyframes | int | 20 | Max keyframes to output |

```bash
python call_grfal.py --tool extract_video_frames --file video_file=input.mp4
python call_grfal.py --tool extract_video_frames --file video_file=input.mp4 --params "{\"extract_keyframes\": false, \"extract_first\": true, \"extract_last\": true}"
```

---

## Audio Generation

### text_to_speech
TTS via Gemini audio. 30 voices, 80+ languages. Supports single-speaker and multi-speaker ("Name: dialogue" format auto-detected).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| text | str | required | Text to synthesize. Supports tags: `[sigh]` `[laughing]` `[whispering]` `[short pause]` |
| voice | str | "Kore" | Voice name (single-speaker mode). 30 available (Kore, Puck, Charon, ...) |
| style_instructions | str | "" | Tone/style directive, e.g. "Read in a calm professional tone" |
| temperature | float | 1.0 | Sampling temperature |
| output_format | str | "mp3" | mp3 / wav / ogg_opus |
| language_code | str | "" | BCP-47 lang code; empty = auto |
| speakers_mapping | dict | null | Multi-speaker: `{"Alice": "Kore", "Bob": "Puck"}` (only used when text has ≥2 "Name:" prefixes) |

```bash
# Single-speaker
python call_grfal.py --tool text_to_speech --params "{\"text\": \"Hello, how are you today?\", \"voice\": \"Kore\"}"

# Multi-speaker (auto-detected from "Name: line" format)
python call_grfal.py --tool text_to_speech --params "{\"text\": \"Alice: Hi Bob!\\nBob: Hey Alice, good to see you.\", \"speakers_mapping\": {\"Alice\": \"Kore\", \"Bob\": \"Puck\"}}"
```

### generate_music
Music generation via MiniMax Music v2.6 (vocals + arrangement + instrumentation).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Music style description (genre, mood, BPM). 10-2000 chars |
| lyrics | str | "" | Lyrics, newline-separated. Supports structure tags: `[Verse]` `[Chorus]` `[Bridge]` etc. Max 3500 chars |
| is_instrumental | bool | false | Instrumental only (no vocals) |
| lyrics_optimizer | bool | false | When true and lyrics empty, auto-generate lyrics from prompt |

```bash
python call_grfal.py --tool generate_music --params "{\"prompt\": \"City Pop, 80s retro, groovy synth bass, warm female vocal, 104 BPM\", \"lyrics_optimizer\": true}"
python call_grfal.py --tool generate_music --params "{\"prompt\": \"lo-fi hip hop, chill, rainy night\", \"is_instrumental\": true}"
```

### generate_sound_effect
Sound effect generation via ElevenLabs SFX v2.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| text | str | required | SFX description, e.g. "footsteps in a thunderstorm", "sci-fi laser gun" |
| duration_seconds | float | 0 | Length in seconds (0.5-22). 0 = auto |
| prompt_influence | float | 0.3 | 0-1, higher = more faithful to prompt |

```bash
python call_grfal.py --tool generate_sound_effect --params "{\"text\": \"sci-fi laser gun firing\", \"duration_seconds\": 3}"
```
