import QtQuick
import org.kde.kirigami as Kirigami

Item {
    id: root

    property var zones: []
    property real aspectRatio: 16 / 9
    property bool isActive: false
    property int innerGap: 3

    implicitWidth: 120
    implicitHeight: 70

    Rectangle {
        id: frame
        anchors.fill: parent
        color: Kirigami.Theme.backgroundColor
        radius: Kirigami.Units.smallSpacing
        border.color: root.isActive ? Kirigami.Theme.highlightColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.2)
        border.width: root.isActive ? 2 : 1
        clip: true

        Item {
            id: container
            anchors.fill: parent
            anchors.margins: 4

            Repeater {
                model: root.zones

                delegate: Rectangle {
                    id: zoneRect
                    required property var modelData
                    required property int index

                    readonly property real zx: modelData[0]
                    readonly property real zy: modelData[1]
                    readonly property real zw: modelData[2]
                    readonly property real zh: modelData[3]

                    x: Math.round(zx * container.width) + root.innerGap
                    y: Math.round(zy * container.height) + root.innerGap
                    width: Math.max(8, Math.round(zw * container.width) - (2 * root.innerGap))
                    height: Math.max(8, Math.round(zh * container.height) - (2 * root.innerGap))
                    radius: 3

                    color: root.isActive ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.35)
                                         : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.12)
                    border.color: root.isActive ? Kirigami.Theme.highlightColor
                                                : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.3)
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: (index + 1).toString()
                        font.pixelSize: Math.max(8, Math.min(12, Math.min(parent.width, parent.height) * 0.45))
                        font.bold: true
                        color: root.isActive ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                        opacity: 0.85
                    }
                }
            }
        }
    }
}
