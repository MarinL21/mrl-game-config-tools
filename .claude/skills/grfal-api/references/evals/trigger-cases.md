# Trigger Cases

## Should Trigger (15)

| # | Prompt | Expected Tool |
|---|--------|---------------|
| 1 | "Generate an image of a dragon flying over mountains" | `generate_image` |
| 2 | "帮我画一个宇宙飞船" | `generate_image` |
| 3 | "Create a 5-second video of waves crashing on rocks" | `generate_video` |
| 4 | "Upscale this image to 4x resolution" | `upscale_image` |
| 5 | "Remove the background from photo.png" | `remove_background` |
| 6 | "Compress this video to reduce file size" | `video_compression` |
| 7 | "Generate a 3D model of a chair from this sketch" | `generate_3d` |
| 8 | "做一个虚拟试穿，把这件衣服穿到模特上" | `virtual_tryon` |
| 9 | "把这张图片超分放大" | `upscale_image` |
| 10 | "抠图，去掉背景" | `remove_background` |
| 11 | "Use grfal to make AI art of a cyberpunk cityscape" | `generate_image` |
| 12 | "Extend this image to 16:9 aspect ratio" | `image_resize` (preset=`16:9`) |
| 13 | "Add lip sync to this video using the audio file" | `video_lipsync` |
| 14 | "文生视频：一只猫在草地上奔跑" | `generate_video` |
| 15 | "Train a LoRA model on these reference images" | `train_model` |

## Should NOT Trigger (10)

| # | Prompt | Reason |
|---|--------|--------|
| 1 | "Edit this Python script to fix the bug" | Code editing, not media generation |
| 2 | "Search for images of cats on Google" | Web search, not generation |
| 3 | "Resize the terminal window" | System operation, not image resize |
| 4 | "Describe this function's behavior" | Code analysis, not media description |
| 5 | "Compress this JSON file" | Data compression, not video compression |
| 6 | "Remove the background process" | Process management, not bg removal |
| 7 | "Generate a random password" | Utility task, not media generation |
| 8 | "Create a video call meeting" | Scheduling, not video generation |
| 9 | "Upscale the logging verbosity" | Configuration, not image upscale |
| 10 | "Make a 3D array in numpy" | Programming, not 3D model generation |
