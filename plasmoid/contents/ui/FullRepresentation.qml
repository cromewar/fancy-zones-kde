import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

Item {
    id: root

    required property PlasmoidItem controller

    implicitWidth: 460
    implicitHeight: 570

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        // Header Section with Minimalist 4-Zone Icon
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Item {
                implicitWidth: 22
                implicitHeight: 22

                Rectangle {
                    anchors.fill: parent
                    radius: 4
                    color: "transparent"
                    border.color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.8)
                    border.width: 1.5
                }

                Grid {
                    anchors.fill: parent
                    anchors.margins: 3.5
                    columns: 2
                    spacing: 2

                    Repeater {
                        model: 4
                        Rectangle {
                            width: (parent.width - parent.spacing) / 2
                            height: (parent.height - parent.spacing) / 2
                            radius: 1
                            color: (index === 0)
                                ? Kirigami.Theme.highlightColor
                                : Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.4)
                        }
                    }
                }
            }

            Kirigami.Heading {
                level: 3
                text: i18n("FancyZones")
                Layout.fillWidth: true
            }

            AspectRatioBadge {
                ratioText: root.controller.currentScreenAspectRatio
                categoryText: root.controller.currentScreenAspectCategory
                resolutionText: root.controller.currentScreenResolution
            }
        }

        Kirigami.Separator { Layout.fillWidth: true }

        // Action Toolbar: Auto-Arrange + Launch Editor
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            QQC2.Button {
                text: i18n("⚡ Auto-Arrange Windows")
                icon.name: "view-grid"
                Layout.fillWidth: true
                highlighted: true
                onClicked: root.controller.autoArrange()
            }

            QQC2.Button {
                text: i18n("Layout Editor")
                icon.name: "document-edit"
                onClicked: root.controller.openLayoutEditor()
            }
        }

        // Layouts Section Title
        RowLayout {
            Layout.fillWidth: true

            Kirigami.Heading {
                level: 4
                text: i18n("Layout Presets")
                Layout.fillWidth: true
            }

            QQC2.Label {
                text: i18n("Switch: Meta+Ctrl+Alt+1..9")
                font.pixelSize: 11
                color: Kirigami.Theme.disabledTextColor
            }
        }

        // Scrollable Grid of Layouts (Fills 100% of Available Width)
        QQC2.ScrollView {
            id: layoutsScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            QQC2.ScrollBar.horizontal.policy: QQC2.ScrollBar.AlwaysOff

            contentWidth: availableWidth

            GridLayout {
                width: layoutsScroll.availableWidth
                columns: 2
                columnSpacing: 10
                rowSpacing: 10

                Repeater {
                    model: root.controller.layoutsList

                    delegate: LayoutCard {
                        Layout.fillWidth: true
                        Layout.preferredWidth: (layoutsScroll.availableWidth - 10) / 2
                        Layout.preferredHeight: 120
                        layoutData: modelData
                        isCurrent: root.controller.activeLayoutId === (modelData ? modelData.id : "")
                        screenAspect: root.controller.currentScreenAspectDecimal
                        onClicked: root.controller.applyLayout(modelData.id)
                    }
                }
            }
        }

        Kirigami.Separator { Layout.fillWidth: true }

        // Quick Zone Snapping Buttons for Focused Window
        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            QQC2.Label {
                text: i18n("Snap Active Window:")
                font.bold: true
                font.pixelSize: 12
            }

            Repeater {
                model: root.controller.currentZoneCount

                delegate: QQC2.Button {
                    text: (index + 1).toString()
                    implicitWidth: 32
                    implicitHeight: 28
                    onClicked: root.controller.snapActiveWindow(index + 1)
                }
            }

            Item { Layout.fillWidth: true }
        }

        // Instructions info note
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: infoRow.implicitHeight + 10
            radius: 6
            color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.1)
            border.color: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.25)

            RowLayout {
                id: infoRow
                anchors.fill: parent
                anchors.margins: 6
                spacing: 6

                Kirigami.Icon {
                    source: "dialog-information"
                    implicitWidth: 16
                    implicitHeight: 16
                    color: Kirigami.Theme.highlightColor
                }

                QQC2.Label {
                    text: i18n("Hold Shift while dragging to snap to zones, or use Meta+Ctrl+1..9")
                    font.pixelSize: 10
                    color: Kirigami.Theme.textColor
                    Layout.fillWidth: true
                }
            }
        }

        // Sliders Row: Gaps & Margins
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                RowLayout {
                    Layout.fillWidth: true
                    QQC2.Label { text: i18n("Zone Gap:"); font.pixelSize: 11 }
                    QQC2.Label { text: root.controller.gap + "px"; font.bold: true; font.pixelSize: 11; color: Kirigami.Theme.highlightColor }
                }

                QQC2.Slider {
                    Layout.fillWidth: true
                    from: 0
                    to: 32
                    stepSize: 2
                    value: root.controller.gap
                    onMoved: root.controller.setGap(Math.round(value))
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2

                RowLayout {
                    Layout.fillWidth: true
                    QQC2.Label { text: i18n("Screen Margin:"); font.pixelSize: 11 }
                    QQC2.Label { text: root.controller.margin + "px"; font.bold: true; font.pixelSize: 11; color: Kirigami.Theme.highlightColor }
                }

                QQC2.Slider {
                    Layout.fillWidth: true
                    from: 0
                    to: 32
                    stepSize: 2
                    value: root.controller.margin
                    onMoved: root.controller.setMargin(Math.round(value))
                }
            }
        }
    }
}
