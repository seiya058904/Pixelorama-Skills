# Drawing and quality

Read for substantial drawing, animation, or tileset work. Optimize for a good asset and a small number of meaningful calls, not maximum pixel count.

## Art direction

Agree with the brief on purpose, dimensions, camera angle, style, transparency, palette, and lighting. Default to 32×32 icons, roughly 48–64 px simple characters, or 16×16 tiles only when unspecified; these are starting points, not quality guarantees. Work at the actual target resolution and inspect both 1× and 4–8× nearest-neighbor previews.

Use a consistent outline and short shade ramps. Small sprites often need only 6–16 colors; larger scenes may need more. Establish a recognizable silhouette before details. Prefer coherent pixel clusters and clean diagonals over random dithering, noisy single pixels, pillow shading, or uncontrolled soft gradients. A detailed enlarged image that is unreadable at 1× is not finished.

For a set of assets, keep a shared palette, perspective, scale, light direction, outline weight, and padding. Store that brief beside the artwork when helpful; do not rewrite the shared skill with private project preferences.

## Make changes predictably

Inspect active project, layer visibility/locks, selected frame, selection mask, dimensions, and background before drawing. Target explicit project/frame/layer handles when available; re-read state after creating, moving, or removing frames/layers. Serialize mutations even if the agent can call tools in parallel. Stop if the user is concurrently changing the same canvas and state becomes ambiguous.

Use shapes for geometry and bulk pixel commands for detail. Compute coordinate arrays outside tool messages where practical, respect payload limits, and send one bounded batch per logical region. Never perform one tool round trip per pixel. Keep undo enabled and checkpoint before risky changes. If a tool is unavailable, choose a supported equivalent; do not guess its schema from this guide.

Use `capture_canvas_image` for visual critique and available palette/validation tools for measurable checks. Preserve intended isolated highlights rather than indiscriminately deleting every single pixel. Make up to three targeted improvement passes, retaining the better version. Without image input, inspect measurable properties but state the visual limitation.

## Recipes

**Icon or item.** Create the canvas, block silhouette, add coherent shading, and separate details only where useful. Review recognizability at 1×, edge cleanup, padding, and transparency. Save `.pxo`, then export transparent PNG at native size; make any enlarged preview a separately named file.

**Character animation.** Establish a strong keyframe, then duplicate and modify moving parts. Check whether cels are linked before editing so one frame does not unexpectedly alter others. Keep dimensions, body proportions, pivot/feet anchor, facing direction, palette, and lighting stable. Review every frame in short loops and the last-to-first transition; use a contact sheet and playback when possible. For longer sequences, review every frame mechanically plus all key poses/transitions visually. Never call an animation smooth solely because its frame count matches.

Read the actual FPS and duration multiplier semantics. Do not assume duration is milliseconds. Do not crop frames independently: retain a shared canvas and pivot. Export a spritesheet or frame sequence plus frame order/timing metadata when the consumer needs it. GIF is a preview when its palette/transparency limits do not meet the asset brief; preserve PNG frames or `.pxo` as the source.

**Tiles or repeating textures.** Define tile size, padding, and grid boundaries first. Inspect a 3×3 repeat, not merely matching edge pixels. Use an available seam diagnostic without treating it as proof of visual quality. For a terrain set, inspect transitions as well as individual tiles. Verify sheet dimensions are multiples of the intended tile grid.

**Edit existing art.** Open and inspect the project, save a separate working copy, then modify only the requested region/layers/frames. Preserve untouched pixels, metadata, hidden layers, and timing. Compare before/after, then save and export without flattening the only editable copy.

**Game delivery.** Use Godot resource exporters only when requested and actually exposed. Validate image references and import settings in the target project when accessible. A generated `.tres` alone does not prove successful engine import.

## Complex artwork and references

This bridge provides editor operations, not a trained image-generation model. Use authorized user references or an authorized image model for an initial concept only when appropriate. Importing a PNG does not recover semantic layers, consistent animation, or clean pixel clusters automatically. Check background removal so subject-colored edges are not erased; preserve alpha and deliberately remap the palette. Do not add a paid service or upload a private reference without permission.

## Delivery gate

Save the native project before export. Verify output existence, dimensions, requested frames, cell order, timing, transparent background, and lack of clipping. Reopen the `.pxo` and decode exported images when feasible. Inspect the actual exports rather than only the canvas. Report exact paths, dimensions and frame count, plus any visual, runtime, or engine-import check not completed. Never rename a PNG to `.pxo` or present a prepared script as an executed drawing.
