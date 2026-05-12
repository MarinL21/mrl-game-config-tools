---
name: grfal-api
description: |
  GRFal AI media tools via direct HTTP API.
  Image/video/3D/audio generation and processing (upscale, remove bg, extend, resize, lipsync, reframe, compress, video frame extraction).
  Also: virtual try-on, LoRA training, face swap, PDF processing, describe media, TTS, music & SFX generation.
  Also creative pipelines: game character sprite sheet (AI multi-action game sprites),
  storyboard expansion (1 panel → 8 cinematic scene variants, style-consistent).
  Triggers: "generate image", "generate video", "upscale", "remove background",
  "3D model", "PBR material", "PBR texture", "材质生成", "贴图",
  "virtual try-on", "lora", "grfal", "AI art", "compress video",
  "image processing", "video editing", "face swap", "grok video",
  "seedance", "seadance", "豆包视频", "即梦", "视频编辑", "视频延长",
  "音频参考", "多模态视频",
  "happyhorse", "happy horse", "百炼视频", "通义万相视频", "dashscope video",
  "sprite sheet", "game sprite", "game character sprites", "pixel art character",
  "storyboard", "storyboard expand", "分镜拓展", "分镜扩展", "分镜延伸",
  "精灵图", "游戏角色精灵图", "像素角色", "角色动作帧", "游戏角色生成",
  "画图", "帮我画", "P图", "修图", "生成图片", "视频生成",
  "抠图", "超分", "换背景", "扩图", "文生图", "文生视频", "视频压缩",
  "TTS", "text to speech", "语音合成", "配音", "多角色配音",
  "music generation", "音乐生成", "生成音乐", "BGM",
  "sound effect", "SFX", "音效生成", "生成音效",
  "extract video frames", "视频帧截取", "视频抽帧", "首帧", "尾帧", "关键帧",
  "panorama", "360 panorama", "全景图", "360 全景", "等距柱状", "equirectangular",
  "mask edit", "局部修图", "蒙版编辑", "image erase", "擦除", "抹除元素",
  "video inpainting", "视频擦除", "视频抹除", "视频去物体", "视频遮罩",
  "text to motion", "动作生成", "3D 动作", "motion generation"
---

# GRFal API - Direct HTTP Tool Calling

Call ~50 GRFal AI tools via HTTP POST. The full schema (~78 tools, including admin-only pipelines) is at `GET /api/tools`.

## Quick Start

Replace `<skill_path>` with the base directory provided by the system (shown as "Base directory for this skill: ...").

### 第一步：首次使用必须先登录认证

**遇到"未认证，请提供有效的 Bearer token 或登录 session"错误时，运行这条命令：**

```bash
python "<skill_path>/scripts/call_grfal.py" --auth-bootstrap
```

执行后会自动打开浏览器 → 在浏览器中登录 GRFal → 登录成功后脚本自动获取 token 并缓存到本地。之后所有调用无需再登录，token 自动续期（有效期 30 天）。

> Token 缓存位置：`~/.config/grfal-api/token_store.json`
> 如果超过 30 天没用，重新跑一次 `--auth-bootstrap` 即可。

### 第二步：正常调用

```bash
python "<skill_path>/scripts/call_grfal.py" --tool generate_image --params "{\"prompt\": \"a cute cat\", \"model\": \"gpt\", \"num_images\": 1}"
```

> **重要：** 必须使用绝对路径调用脚本，禁止使用 `cd <dir> && python3 call_grfal.py` 模式，否则会被 exec preflight 拦截。始终用 `python3 "<skill_path>/scripts/call_grfal.py"` 格式。

如果脚本检测到无缓存 token，也会自动触发浏览器授权流程（等同于 `--auth-bootstrap`）。出现以下输出时：

```
{"info": "No token available. Starting automatic device flow authorization..."}
{"info": "Browser opened for authorization."}
```

→ 告知用户 **"请在浏览器中完成授权"**，等待即可（建议 timeout 设 120s+），授权后脚本自动继续。

## Configuration

API endpoint: `https://grfal.tap4fun.com` (company intranet required). Override with `--url` or `GRFAL_API_URL` env var.

<details>
<summary>Advanced: Auth methods, troubleshooting, and overrides</summary>

**Auth is automatic** (device flow). For headless/CI environments:

```bash
# Bootstrap from active web login session
python "<skill_path>/scripts/call_grfal.py" --auth-bootstrap

# Or manually set a refresh token
python "<skill_path>/scripts/call_grfal.py" --set-refresh-token <token>
```

Token cache: `~/.config/grfal-api/token_store.json` (access token 12h, refresh token 30d auto-renewal).

**Auth priority** (high→low): CLI `--bearer-token` → env `GRFAL_BEARER_TOKEN` → cached token → auto-refresh → device flow.

**Troubleshooting:**

| Symptom | Fix |
|---------|-----|
| HTTP 401 on first use | Run `--auth-bootstrap` or complete device flow in browser |
| HTTP 401 after working | Token expired (>30d idle), re-run `--auth-bootstrap` |
| HTTP 403 | Check scopes with admin |

**Other overrides:** `--public-url` (rewrite result URLs), `--insecure` (skip SSL), `--no-auth-interactive` (disable browser popup).
</details>

## Core Workflow

### Result format

```json
{"success": true, "result": ["https://...url1.png"], "backend": "fal"}
{"success": false, "error": "descriptive error message"}
```

Result URLs are directly downloadable.

### File inputs

| Method | Usage | When |
|--------|-------|------|
| **URL (recommended)** | `--params "{\"image_paths\": [\"https://...\"]}"` | File already has a public URL |
| **Local file** | `--file image_paths=C:\path\image.png` | Local file, auto-converts to base64 |
| **Base64 inline** | `--params "{\"image_paths\": [\"data:image/png;base64,...\"]}"` | Already have base64 |

Multiple files with same key: `--file image_paths=file1.png --file image_paths=file2.png`

### Timeout & Async Mode

| Scope | Default | Mode |
|-------|---------|------|
| Image tools | 300s (5 min) | Synchronous |
| Video/3D/training tools | 1800s (30 min) | **Async polling** |

**Async polling mode** (automatic for video/3D/training):
- Task is submitted, returns immediately with task_id
- Polls server every 15s for status
- More reliable for long-running tasks (no connection timeout)
- Use `--sync` to force synchronous mode if needed

**Background task mode** (automatic for very long tasks):

These tools **automatically** use background mode (return task_id, no waiting):
- Video: `generate_video`, `video_avatar`, `video_lipsync`, `video_portrait`, `video_upscale`, `video_modify`
- Training: `train_model`
- Other: `screenshot_localization`, `pdf_enhancement`

```bash
# Automatic background mode
python "<skill_path>/scripts/call_grfal.py" --tool video_avatar --params "..."
# → {"task_id": "video_avatar_xxx", "note": "using background mode automatically"}

# Check status later
python "<skill_path>/scripts/call_grfal.py" --check-task video_avatar_xxx
# → {"status": "running"} OR {"success": true, "result": "..."}

# Force polling mode (override background)
python "<skill_path>/scripts/call_grfal.py" --tool video_avatar --sync --params "..."
```

**Agent workflow for background tasks:**
1. Call tool → get task_id immediately
2. **IMPORTANT: Save the task_id** — you'll need it to check status later
3. Tell user: "Task submitted (task_id: xxx), I'll check back in a few minutes"
4. Set a reminder/cron job to check status in 2-5 minutes
5. Use `--check-task <task_id>` to poll until completed
6. If still running, set another check; if done, deliver result to user

### List tools

```bash
python "<skill_path>/scripts/call_grfal.py" --list-tools
```

## Tool Selection Guide

Choose the right tool by task. For **detailed parameters**, read [references/tool_catalog.md](references/tool_catalog.md).

| Task | Tool | Key Params |
|------|------|------------|
| Text/image → image | `generate_image` | prompt, model (default: **gpt** = gpt-image-2), reference_images |
| NSFW realistic photo | `generate_image` | prompt, model=**zimage** (text-to-image only, built-in LoRA, no safety checker) |
| Portrait makeup / style transfer / element fusion | `generate_image` | prompt, model=**firered** (image-edit only, needs ≥1 ref image, max 7) |
| LoRA preset image | `lora_generation` | prompt, preset, model |
| Style transfer | `kontext_lora` | image_paths, preset |
| Image upscale | `upscale_image` | image_paths, model, scale |
| Remove background | `remove_background` | image_paths |
| Replace background | `replace_background` | image_paths, background_prompt |
| Resize image / extend canvas (unified) | `image_resize` | image_paths, preset (`1:1` / `16:9` / `9:16` / `4:3` / `3:4` / `4:5` / `5:4` / `X2双端` / `P2双端`) **or** width+height [+safe_width+safe_height] |
| Batch edit images (same prompt) | `image_batch_edit` | image_paths, multimodal (prompt+ref), model_type=gpt |
| Mask edit (local edit by mask) | `image_mask_edit` | image_path, mask_path (PNG RGBA), multimodal, model_type=gpt |
| Erase area by mask | `image_erase` | image_path, mask_path |
| 360° equirectangular panorama | `generate_panorama` | multimodal (text + optional ref), 2:1 / 2048×1024 fixed |
| Game character sprite sheet (AI multi-action) | `creative_workflow` | user_input, tool_id=**sprite_sheet** |
| Storyboard expansion (1 image → 8 scenes) | `creative_workflow` | tool_id=**storyboard_expand**, reference_files |
| Text/image → video | `generate_video` | prompt, model, reference_images, ref_types, duration |
| Seedance 2.0 multimodal video | `generate_video` | prompt, model=**seadance**, ref_types (mix 首帧/元素参考/参考视频/参考音频), max 9img+3video+3audio |
| Seedance 2.0 video editing | `generate_video` | prompt, model=**seadance**, ref_types="参考视频,元素参考", upload source video + ref images |
| Seedance 2.0 video extending | `generate_video` | prompt, model=**seadance**, ref_types="参考视频,参考视频,...", upload 1-3 video clips to stitch |
| Grok video (multi-ref element mode) | `generate_video` | prompt, model=**grok**, ref_types="元素参考", max 4 images |
| HappyHorse 视频（百炼 t2v/i2v/r2v/video-edit） | `generate_video` | prompt, model=**happyhorse**, ref_types (text/首帧/元素参考 max 9/参考视频), duration 3-15s. 视频自带音频直出 |
| Video from video | `generate_video` | prompt, model, reference_images (video), ref_types="参考视频", duration (≤10s for Kling, ≤15s for Seadance/HappyHorse) |
| Video upscale | `video_upscale` | video_path |
| Video style change | `video_modify` | video_path, prompt, model (kling/wan/runway/**happyhorse**), reference_images. For Seedance 2.0 editing, use `generate_video` with 参考视频 mode instead |
| Add audio to video | `video_to_audio` | video_path, prompt |
| Lip sync | `video_lipsync` | video_path, audio_path, sync_mode (latentsync=高质量/lipsync=快速) |
| Character animation | `video_portrait` | image_path, video_path, portrait_mode (视频替换角色/视频动作驱动图片) |
| Audio-driven avatar | `video_avatar` | image_path, audio_path, prompt (optional: video description) |
| Change aspect ratio | `video_reframe` | video_path, target_ratio |
| Remove video background | `video_remove_background` | video_path, export_platform (none/sbs), export_quality (CRF, default 18) |
| Video BG removal + SBS export (one step) | `video_remove_background` | video_path, export_platform=**sbs**, export_quality |
| Export SBS video (standalone) | `export_sbs_video` | input_videos (file list), quality (CRF int, required) |
| Video erase / inpainting | `video_inpainting` | video_path, mask_prompt (LLM 找物体), enable_pass2 |
| Reverse-engineer Seedance 2.0 multi-shot prompt from a video | `seedance_prompt_reverse` | video_path |
| PBR material (text → tileable PBR) | `generate_pbr_material` | prompt, tiling_mode, upscale_factor |
| PBR material (photo → extract) | `generate_pbr_material` | prompt, image, image_role=提取材质 |
| PBR material (texture → PBR maps) | `generate_pbr_material` | image, image_role=生成PBR通道 |
| Image → 3D (高精度FBX) | `generate_3d` | image_paths, model=tripo_v31/hunyuan/rodin/meshy/trellis, face_limit. **多视角**：hunyuan/meshy/tripo_v31/tripo_p1 都支持最多 4 张 |
| Image → 3D (低多边形GLB) | `generate_3d` | image_paths, model=tripo_p1, face_limit (48-20000) |
| Text → 3D motion | `generate_motion` | prompt, duration (default 5s), guidance_scale, seed |
| Query training status | `query_training_status` | model_name (e.g. fal-ai/flux-lora-fast-training), request_id |
| Describe media | `describe_media` | media_path, prompt |
| Face swap | `face_swap` | body_image, face_image, model (HY-WU Edit默认/Flux LoRA/Qwen 2511 LoRA) |
| Virtual try-on | `virtual_tryon` | model_image, garment_image |
| Extract video frames | `extract_video_frames` | video_file, extract_first/last/keyframes, max_keyframes (local ffmpeg) |
| Text-to-speech (TTS) | `text_to_speech` | text, voice (30 voices), style_instructions, speakers_mapping (auto multi-speaker) |
| Music generation | `generate_music` | prompt, lyrics, is_instrumental, lyrics_optimizer (MiniMax Music v2.6) |
| Sound effect (SFX) | `generate_sound_effect` | text, duration_seconds (0.5-22), prompt_influence (ElevenLabs SFX v2) |
| Creative pipeline | `creative_workflow` | user_input, tool_id |

Additional tools: `generate_pbr_material`, `image_remove_lighting`, `image_group_photo`, `image_camera_angle`, `image_keyframe`, `image_layered`, `image_split`, `video_speed`, `synthesize_card`, `correct_yellow_tint`, `vector_generation`, `screenshot_localization`, `pdf_enhancement`, `pdf_compression`, `video_compression`, `reduce_face`, `train_model`.

> 内部工作流（不通过此 skill 暴露，仅在 UI / 内部 agent 使用）：`comic_generation` / `drama_generation`（端到端漫画/短剧）+ `cf_*` 买量素材工厂全套（爆款入库 / 归因 / 衍生 / 视频还原）。需要请直接调 `/api/tools` 看 schema。

## Common Examples

```bash
# Generate image
python "<skill_path>/scripts/call_grfal.py" --tool generate_image --params "{\"prompt\": \"a cute cat in space\", \"model\": \"gemini\", \"num_images\": 2}"

# Game character sprite sheet (AI-generated, multi-action pixel art)
python "<skill_path>/scripts/call_grfal.py" --tool creative_workflow --params "{\"tool_id\": \"sprite_sheet\", \"user_input\": \"一个中世纪骑士，需要待机、行走、攻击、死亡四个动作\"}"

# Sprite sheet with reference image (upload your own character ref)
python "<skill_path>/scripts/call_grfal.py" --tool creative_workflow \
  --params "{\"tool_id\": \"sprite_sheet\", \"user_input\": \"这个角色，需要待机、行走、攻击三个动作\"}" \
  --file reference_files=my_character.png

# Storyboard expansion: upload 1 storyboard panel → get 8 style-consistent cinematic scene variants
python "<skill_path>/scripts/call_grfal.py" --tool creative_workflow \
  --params "{\"tool_id\": \"storyboard_expand\", \"user_input\": \"延伸出8个有故事感的相关场景\"}" \
  --file reference_files=my_storyboard.png

# Remove background (local file)
python "<skill_path>/scripts/call_grfal.py" --tool remove_background --file image_paths=C:\Users\photo.png

# Generate video from image (first frame control)
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"camera slowly zooms in\", \"model\": \"kling\"}" --file reference_images=keyframe.png

# Generate video with first + last frame control
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"smooth transition\", \"model\": \"kling\", \"ref_types\": \"首帧图像,尾帧图像\"}" --file reference_images=start.png --file reference_images=end.png

# Video-to-video (reference video mode)
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"make it more cinematic\", \"model\": \"kling\", \"ref_types\": \"参考视频\", \"duration\": 10}" --file reference_images=input.mp4

# Seedance 2.0 multimodal (image + video + audio references)
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"参考图片1的角色，使用视频1的运镜，音色参考音频1\", \"model\": \"seadance\", \"ref_types\": \"元素参考,参考视频,参考音频\"}" --file reference_images=char.png --file reference_images=camera.mp4 --file reference_images=voice.mp3

# Seedance 2.0 video editing (replace object)
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"将视频1中的香水替换成图片1中的面霜\", \"model\": \"seadance\", \"ref_types\": \"参考视频,元素参考\"}" --file reference_images=source.mp4 --file reference_images=product.png

# HappyHorse t2v (text-to-video, 自带音频)
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"a horse galloping across a sunset prairie\", \"model\": \"happyhorse\", \"duration\": 5}"

# HappyHorse video-edit (改写已有视频)
python "<skill_path>/scripts/call_grfal.py" --tool generate_video --params "{\"prompt\": \"换成赛博朋克风格的霓虹夜景\", \"model\": \"happyhorse\", \"ref_types\": \"参考视频\"}" --file reference_images=input.mp4

# Video background removal + SBS export (recommended one-step workflow)
python "<skill_path>/scripts/call_grfal.py" --tool video_remove_background --params "{\"export_platform\": \"sbs\", \"export_quality\": 18}" --file video_path=input.mp4

# Standalone SBS export (if you already have a WebM with alpha channel)
python "<skill_path>/scripts/call_grfal.py" --tool export_sbs_video --params "{\"quality\": 18}" --file input_videos=transparent.webm

# Upscale image
python "<skill_path>/scripts/call_grfal.py" --tool upscale_image --file image_paths=low_res.png --params "{\"model\": \"SeedVR\"}"

# Describe an image
python "<skill_path>/scripts/call_grfal.py" --tool describe_media --file media_path=screenshot.png --params "{\"prompt\": \"describe this image in detail\"}"
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Connection failed | Server not running / not on intranet | Start GRFal or connect to company network |
| SSL certificate error | Self-signed cert | Use `--insecure` or install CA cert |
| HTTP 401 | Missing or invalid auth token | Run `--auth-bootstrap` or `--set-refresh-token`; see Auth Troubleshooting above |
| HTTP 403 | Token lacks required scopes or expired | Re-run `--auth-bootstrap`; check scopes with admin |
| Timeout | Long-running task | Increase `--timeout` |
| Tool not found | Invalid tool name | Run `--list-tools` to check |
| File not found | Wrong local path | Verify file path exists |

## Troubleshooting with Server Logs

**IMPORTANT**: When encountering unexplained errors (task disappears, unexpected failures, backend issues), **always check server logs first**:

```bash
# View systemd journal (real-time server output)
python "<skill_path>/scripts/call_grfal.py" --view-logs

# View more lines
python "<skill_path>/scripts/call_grfal.py" --view-logs --log-lines 500

# View specific date's runtime log
python "<skill_path>/scripts/call_grfal.py" --view-logs grfal_20260204.log
```

**When to check logs:**
- Task submitted but result never arrives
- Unexpected "task not found" errors
- Backend failover issues
- Any error message that doesn't make sense

**Log types:**
- `systemd-journal` (default): Real-time stdout/stderr from systemd service
- `grfal_YYYYMMDD.log`: Daily runtime logs with detailed processing info

**Web UI**: https://grfal.tap4fun.com/api/logs/viewer

## Transport

`grfal-api` uses direct HTTP POST to `/api/call` (sync). All external callers go through the
`@tool` registry via either this sync endpoint or the browser-facing `/gradio_api/call/{tool}`
SSE protocol.

## Evals
See references/evals/
