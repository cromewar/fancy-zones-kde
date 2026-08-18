import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Item {
    id: root

    property var layoutData: null
    property bool isCurrent: false
    property real screenAspect: 16 / 9

    signal clicked()

    Layout.fillWidth: true
    implicitHeight: 120

    Rectangle {
        id: bg
        anchors.fill: parent
        radius: Kirigami.Units.smallSpacing * 1.5
        color: mouseArea.containsMouse
            ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.15)
            : (root.isCurrent ? Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.08) : Kirigami.Theme.backgroundColor)

        border.color: root.isCurrent ? Kirigami.Theme.highlightColor : (mouseArea.containsMouse ? Kirigami.Theme.highlightColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.2))
        border.width: root.isCurrent ? 2 : 1

        Behavior on color { ColorAnimation { duration: 150 } }
        Behavior on border.color { ColorAnimation { duration: 150 } }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8

            // Header row with Name and Shortcut Badge
            RowLayout {
                Layout.fillWidth: true
                spacing: 6

                Kirigami.Heading {
                    level: 5
                    text: root.layoutData ? root.layoutData.name : ""
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                    font.bold: root.isCurrent
                    color: root.isCurrent ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                }

                Rectangle {
                    visible: root.layoutData && root.layoutData.shortcut !== undefined
                    implicitWidth: shortcutText.implicitWidth + 8
                    implicitHeight: 18
                    radius: 9
                    color: root.isCurrent ? Kirigami.Theme.highlightColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.12)
                    border.color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.2)
                    border.width: 1

                    Text {
                        id: shortcutText
                        anchors.centerIn: parent
                        text: root.layoutData ? "#" + root.layoutData.shortcut : ""
                        font.pixelSize: 10
                        font.bold: true
                        color: root.isCurrent ? "#ffffff" : Kirigami.Theme.textColor
                    }
                }
            }

            // Thumbnail visualization
            LayoutThumbnail {
                Layout.fillWidth: true
                Layout.fillHeight: true
                zones: root.layoutData ? root.layoutData.zones : []
                isActive: root.isCurrent
                aspectRatio: root.screenAspect
            }
        }

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.clicked()
        }
    }
}
