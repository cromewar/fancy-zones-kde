import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Rectangle {
    id: root

    property string ratioText: "32:9"
    property string categoryText: "Super Ultrawide"
    property string resolutionText: "5120×1440"

    implicitHeight: 28
    implicitWidth: contentLayout.implicitWidth + 16
    radius: 14
    color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.2)
    border.color: Kirigami.Theme.highlightColor
    border.width: 1

    RowLayout {
        id: contentLayout
        anchors.centerIn: parent
        spacing: 6

        Kirigami.Icon {
            source: "video-display"
            implicitWidth: 16
            implicitHeight: 16
        }

        Text {
            text: root.ratioText + " " + root.categoryText
            font.bold: true
            font.pixelSize: 11
            color: Kirigami.Theme.highlightColor
        }

        Text {
            text: "• " + root.resolutionText
            font.pixelSize: 10
            color: Kirigami.Theme.disabledTextColor
        }
    }
}
