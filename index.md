# DedoMouse
DedoMouse let's you control your computer mouse with your hands and a webcam.

[Download the latest release from GitHub.](https://github.com/achimmihca/DedoMouse/releases/latest)

DedoMouse is useful for
- Presentations (show next slide or image)
- Simple browsing (e.g. start movie)
- Reduced bacteria transfer (no need to touch an input device at an ATM or laboratory)
- Simple games ("point and click" adventures)
- People who cannot or do not want to use a regular mouse (e.g. because of pain due to RSI)
    - The gesture based remote control of DedoMouse allows you to take a step back from your desk
and reduce the time spent in uncomfortable positions.

## Gestures and Mouse Actions
***Tip:*** You can test these gestures in the app using the "Log" tab.
All recognized gestures are logged even if mouse control is disabled.

<table>
    <th>
        Mouse Action
    </th>
    <th>
        Description
    </th>
    <th>
        Image
    </th>
    <tr>
        <td width="20%">
            Left click
        </td>
        <td width="40%">
            Move index finger near thumb.
        </td>
        <td width="40%">
            <img src="./images/left-click.jpg" width="30%" alt="left-click image" />
        </td>
    </tr>
    <tr>
        <td width="20%">
            Right click
        </td>
        <td width="40%">
            Move middle and ring finger near thumb.
        </td>
        <td width="40%">
            <img src="./images/right-click.jpg" width="30%" alt="right-click image" />
        </td>
    </tr>
    <tr>
        <td width="20%">
            Middle click
        </td>
        <td width="40%">
            Move ring finger and pinky near thumb.
        </td>
        <td width="40%">
            <img src="./images/middle-click.jpg" width="30%" alt="middle-click image" />
        </td>
    </tr>
    <tr>
        <td width="20%">
            Scroll up
        </td>
        <td width="40%">
            Thumb up gesture.
        </td>
        <td width="40%">
            <img src="./images/scroll-up.jpg" width="30%" alt="scroll-up image" />
        </td>
    </tr>
    <tr>
        <td width="20%">
            Scroll down
        </td>
        <td width="40%">
            Thumb down gesture.
        </td>
        <td width="40%">
            <img src="./images/scroll-down.jpg" width="30%" alt="scroll-down image" />
        </td>
    </tr>
    <tr>
        <td width="20%">
            Drag and Drop
        </td>
        <td width="40%">
            Hold left click gesture for some time to start a mouse-drag.<br/>
            Release the gesture to end the mouse-drag.
        </td>
        <td width="40%">
            <img src="./images/left-click.jpg" width="30%" alt="scroll-down image" />
        </td>
    </tr>
</table>

You can close the app anytime via keyboard shortcut `Ctrl+Shift+Alt+Escape`.
All shortcuts are configurable.

## Video Streams of IP Webcam
DedoMouse supports video streams in RTSP or MJPEG format as well as an integrated webcam or USB webcam.<br />
Further, JPG images can be used directly.

Therefor, the URL must end with ".jpg" or ".mjpeg" respectively.

For example, the video stream of free [IP Webcam app](https://play.google.com/store/apps/details?id=com.pas.webcam)
for Android is compatible with DedoMouse.

## How it works
DedoMouse uses the hand and finger tracking of Google's [MediaPipe](https://google.github.io/mediapipe/solutions/hands).

## License
DedoMouse is free and open source software under [MIT license](https://github.com/achimmihca/DedoMouse/blob/main/LICENSE).

## Trivia
'Dedo' is Spanish and means 'finger'.
