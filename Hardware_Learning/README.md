# Hardware Learning (interactive)

This mini-app teaches hardware components (Desktops, Servers, Routers, Switches) using interactive SVG diagrams and a simple quiz.

Run locally:

```bash
pip install -r Basic-Storage/Hardware_Learning/requirements.txt
python Basic-Storage/Hardware_Learning/app.py
```

Open http://127.0.0.1:8000 in your browser.

To add photos or richer diagrams, place images under `Basic-Storage/Hardware_Learning/static/images/real/` and update `components.json` `image` fields to the filename.

Tips for replacing images and adjusting connector coordinates:

- Add a photo: `static/images/real/my_desktop.jpg` and set the component `image` to `real/my_desktop.jpg`.
- Tweak connector coordinates in `components.json` to match pixel positions in the diagram's SVG viewBox (default 720x400).
- After updating coordinates, reload the page; hotspot and wiring endpoints will align with the new image.

The app saves wiring attempts to `wiring_attempts.json` and adds incorrect wiring question IDs to `review_list.json`.

**User Guide (Simple)**

This short manual explains how to use the Hardware Learning app. It assumes no prior technical knowledge.

1) Starting the app
- Open the folder `Basic-Storage/Hardware_Learning` on your computer.
- Run this command in a terminal or PowerShell window:
```bash
python Basic-Storage/Hardware_Learning/app.py
```
- Open your web browser and go to: `http://127.0.0.1:8000`

2) Viewing and interacting with diagrams
- The left area shows an interactive diagram. Use your mouse wheel to zoom in/out.
- Hold the Shift key and drag the mouse, or press the middle mouse button and drag, to move (pan) the diagram.
- On touch screens: drag with one finger to pan, pinch with two fingers to zoom.
- Hover a highlighted area (hotspot) to see a short tooltip. Click it to see a description and image.

3) Quiz and wiring practice
- Click `Start Quiz` to begin. The app will prompt you with a task.
- For wiring tasks: click a connector dot and drag to another connector. If your line snaps to the correct target, it will show green and record success; if incorrect, it will show red and the attempt will be saved for review.
- All wiring attempts are saved automatically to a file named `wiring_attempts.json` in the `Hardware_Learning` folder.

4) Editing diagrams and connector points (no coding required)
- Click `Diagram Editor` to open the editor panel.
- Choose a component from the dropdown to load its image.
- If the image is an SVG, connector points (small dots) can be dragged with the mouse to the correct spot.
- Press `Save Connectors` to update the app with your new connector positions.
- To replace an image, click `Choose file`, pick an image (SVG, PNG, or JPG), then `Upload`. If you upload an SVG, you can then drag connector points.

5) Restoring co-ordinates automatically
- If you replaced images and want the app to re-calculate connector positions from the SVG artwork, click `Refresh Coords From SVGs` in the editor.

6) Where files are saved
- `components.json` contains the list of components and connector coordinates.
- `wiring_attempts.json` contains all wiring attempts you made.
- `review_list.json` contains items the app marked for review.
- Uploaded images go to `static/images/real/`.

If anything seems unclear, tell me which step and I'll make the instructions more specific for your setup (Windows, Mac, or Linux).
