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

        // Minimalist Window with 4 Zone Sections
        Item {
            id: iconItem
            anchors.centerIn: parent
            width: 16
            height: 16

            readonly property color baseColor: mouseArea.containsMouse
                ? Kirigami.Theme.highlightColor
                : Kirigami.Theme.textColor

            // Outer subtle window border
            Rectangle {
                anchors.fill: parent
                radius: 3
                color: "transparent"
                border.color: Qt.rgba(iconItem.baseColor.r, iconItem.baseColor.g, iconItem.baseColor.b, 0.65)
                border.width: 1
            }

            // 4 Zone Sections Grid
            Grid {
                anchors.fill: parent
                anchors.margins: 2.5
                columns: 2
                spacing: 1.5

                Repeater {
                    model: 4
                    Rectangle {
                        width: (parent.width - parent.spacing) / 2
                        height: (parent.height - parent.spacing) / 2
                        radius: 1
                        color: (index === 0)
                            ? iconItem.baseColor
                            : Qt.rgba(iconItem.baseColor.r, iconItem.baseColor.g, iconItem.baseColor.b, 0.35)
                    }
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
