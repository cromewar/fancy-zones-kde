import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
import org.kde.kquickcontrols

Kirigami.FormLayout {
    id: root

    property alias cfg_gap: gapSpin.value
    property alias cfg_margin: marginSpin.value
    property alias cfg_holdShiftToSnap: shiftCheck.checked
    property alias cfg_showOutline: outlineCheck.checked
    property alias cfg_showZoneNumbers: numbersCheck.checked

    QQC2.SpinBox {
        id: gapSpin
        Kirigami.FormData.label: i18n("Inner Zone Gap (px):")
        from: 0
        to: 64
        stepSize: 2
    }

    QQC2.SpinBox {
        id: marginSpin
        Kirigami.FormData.label: i18n("Outer Screen Margin (px):")
        from: 0
        to: 64
        stepSize: 2
    }

    QQC2.CheckBox {
        id: shiftCheck
        Kirigami.FormData.label: i18n("Snapping Trigger:")
        text: i18n("Hold Shift while dragging to snap")
    }

    QQC2.CheckBox {
        id: outlineCheck
        Kirigami.FormData.label: i18n("Visual Feedback:")
        text: i18n("Show zone outline highlight while moving")
    }

    QQC2.CheckBox {
        id: numbersCheck
        Kirigami.FormData.label: i18n("Zone Numbers:")
        text: i18n("Display zone numbers on overlay")
    }
}
