# Real editor acceptance test

Run on an authorized host with Pixelorama and an approved bridge. This is a manual/agent execution protocol, not a claim that it has already passed.

## Record the environment

Record OS, Node version, Pixelorama version, bridge commit, plugin SHA-256/API version, agent version, and the exposed MCP tool list. Keep secrets and personal paths out of public evidence. Save all unsaved user work without overwriting its intended destination; note the previously active project.

## Test sequence

1. Confirm loopback health and a real MCP read. Do not count configuration presence alone.
2. In a new 16×16 project, draw a 4×4 rectangle with one batch. Capture the canvas. Save a new `.pxo` and export a 16×16 PNG to a dedicated test folder.
3. Reopen the project and decode the PNG. Confirm dimensions, pixel location/color, alpha and editable data; compare actual pixels where practical.
4. Make a second layer, edit only that layer, then undo/redo. Verify both image state and layer targeting. Do not assume the server supports undo for every operation.
5. Make a short three-frame loop with a stable anchor and different frame durations. Verify each frame, shared canvas size, duration semantics, spritesheet ordering, and save/reopen persistence.
6. Test an intentional version/configuration failure without damaging a user project. If a command times out, inspect its state before any retry. Do not inject infinite loops or unsafe scripts to simulate a timeout.
7. Capture the exported result at native resolution and enlarged nearest-neighbor scale; visually inspect it. Restore the user's previously active project when safe. Report artifacts as cleanup candidates rather than deleting them.

## Evidence levels

Report dependency build, bridge health, MCP reads, drawing/export round trip, animation/undo, and visual inspection separately. Stop a failing branch safely and continue independent checks. Only mark a gate passed with its actual evidence. A successful Linux test does not certify Windows, and a smoke-test rectangle does not demonstrate high-quality artistic output.
