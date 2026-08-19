import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid

Item {
    id: root

    required property PlasmoidItem plasmoidItem

    Layout.minimumWidth: Kirigami.Units.iconSizes.smallMedium
    Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium
    Layout.maximumWidth: Kirigami.Units.iconSizes.smallMedium
    Layout.fillHeight: true

    implicitWidth: Kirigami.Units.iconSizes.smallMedium
    implicitHeight: Kirigami.Units.iconSizes.smallMedium

    readonly property var activeLayout: root.plasmoidItem.activeLayout
    readonly property var activeZones: (activeLayout && activeLayout.zones) ? activeLayout.zones : [[0,0,0.5,0.5],[0.5,0,0.5,0.5],[0,0.5,0.5,0.5],[0.5,0.5,0.5,0.5]]
    readonly property string shortcutNumber: (activeLayout && activeLayout.shortcut) ? activeLayout.shortcut.toString() : ""

    Rectangle {
        id: container
        anchors.centerIn: parent
        width: Kirigami.Units.iconSizes.smallMedium - 2
        height: Kirigami.Units.iconSizes.smallMedium - 2
        radius: 4
        color: mouseArea.containsMouse
            ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.2)
            : (root.plasmoidItem.expanded ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.15) : "transparent")

        Behavior on color { ColorAnimation { duration: 120 } }

        Item {
            id: iconItem
            anchors.centerIn: parent
            width: 18
            height: 18

            readonly property color baseColor: mouseArea.containsMouse
                ? Kirigami.Theme.highlightColor
                : Kirigami.Theme.textColor

            // Outer subtle window border
            Rectangle {
                anchors.fill: parent
                radius: 3
                color: "transparent"
                border.color: Qt.rgba(iconItem.baseColor.r, iconItem.baseColor.g, iconItem.baseColor.b, 0.6)
                border.width: 1
            }

            // Dynamic mini zone preview matching active layout
            Item {
                anchors.fill: parent
                anchors.margins: 2

                Repeater {
                    model: root.activeZones

                    delegate: Rectangle {
                        required property var modelData
                        required property int index

                        readonly property real zx: modelData[0]
                        readonly property real zy: modelData[1]
                        readonly property real zw: modelData[2]
                        readonly property real zh: modelData[3]

                        x: Math.round(zx * parent.width) + 0.5
                        y: Math.round(zy * parent.height) + 0.5
                        width: Math.max(2, Math.round(zw * parent.width) - 1)
                        height: Math.max(2, Math.round(zh * parent.height) - 1)
                        radius: 1
                        color: (index === 0)
                            ? iconItem.baseColor
                            : Qt.rgba(iconItem.baseColor.r, iconItem.baseColor.g, iconItem.baseColor.b, 0.4)
                    }
                }
            }

            // Shortcut number badge in bottom-right corner
            Rectangle {
                visible: root.shortcutNumber !== ""
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.rightMargin: -2
                anchors.bottomMargin: -2
                width: 10
                height: 10
                radius: 5
                color: Kirigami.Theme.highlightColor
                border.color: Kirigami.Theme.backgroundColor
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: root.shortcutNumber
                    font.pixelSize: 7
                    font.bold: true
                    color: "#ffffff"
                }
            }
        }

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.plasmoidItem.expanded = !root.plasmoidItem.expanded
        }
    }
}
