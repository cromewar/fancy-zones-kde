import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as Plasma5Support

PlasmoidItem {
    id: root

    // Executable Data Source for reliable command execution
    Plasma5Support.DataSource {
        id: execSource
        engine: "executable"
        connectedSources: []

        onNewData: function(sourceName, data) {
            disconnectSource(sourceName);
            if (sourceName.indexOf("GetActiveLayout") !== -1 && data["stdout"]) {
                var out = data["stdout"].trim();
                if (out && out !== root.activeLayoutId) {
                    root.activeLayoutId = out;
                }
            }
        }
    }

    function runCommand(cmd) {
        var uniqueCmd = cmd + " # " + Date.now();
        execSource.connectSource(uniqueCmd);
    }

    function syncActiveLayoutFromDBus() {
        var cmd = "qdbus6 org.kde.FancyZones /Manager org.kde.FancyZones.GetActiveLayout " + currentScreenName;
        execSource.connectSource(cmd);
    }

    // Refresh active layout whenever popup is opened
    onExpandedChanged: {
        if (expanded) {
            syncActiveLayoutFromDBus();
        }
    }

    // Model and State properties
    property var layoutsList: []
    property var screenList: []
    property int currentScreenIndex: 0
    property string activeLayoutId: "cols-3"
    property int gap: Plasmoid.configuration.gap !== undefined ? Plasmoid.configuration.gap : 8
    property int margin: Plasmoid.configuration.margin !== undefined ? Plasmoid.configuration.margin : 8

    // Active Screen Derived Properties
    readonly property var currentScreen: (screenList.length > currentScreenIndex && currentScreenIndex >= 0)
        ? screenList[currentScreenIndex]
        : (screenList.length > 0 ? screenList[0] : null)

    readonly property string currentScreenName: currentScreen ? (currentScreen.name || "Display") : "DP-3"
    readonly property string currentScreenResolution: currentScreen && currentScreen.geometry
        ? (currentScreen.geometry.width + "×" + currentScreen.geometry.height)
        : "5120×1440"
    readonly property string currentScreenAspectRatio: currentScreen && currentScreen.aspectRatio
        ? (currentScreen.aspectRatio.ratio || "32:9")
        : "32:9"
    readonly property string currentScreenAspectCategory: currentScreen && currentScreen.aspectRatio
        ? (currentScreen.aspectRatio.name || "Super Ultrawide")
        : "Super Ultrawide"
    readonly property real currentScreenAspectDecimal: currentScreen && currentScreen.aspectRatio && currentScreen.aspectRatio.decimal
        ? currentScreen.aspectRatio.decimal
        : 32 / 9

    // Active Layout Derived Properties
    readonly property var activeLayout: {
        for (var i = 0; i < layoutsList.length; i++) {
            if (layoutsList[i].id === activeLayoutId) {
                return layoutsList[i];
            }
        }
        return layoutsList.length > 0 ? layoutsList[0] : null;
    }

    readonly property string activeLayoutName: activeLayout ? activeLayout.name : "3 Columns"
    readonly property string activeLayoutNameShort: activeLayout ? (activeLayout.shortcut ? "#" + activeLayout.shortcut : activeLayout.name.substring(0, 3)) : "⊞"
    readonly property int currentZoneCount: activeLayout && activeLayout.zones ? activeLayout.zones.length : 3

    Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground | PlasmaCore.Types.ConfigurableBackground
    Plasmoid.icon: "fancyzones"
    Plasmoid.status: PlasmaCore.Types.ActiveStatus
    Plasmoid.title: i18n("FancyZones")

    toolTipMainText: i18n("FancyZones: %1", activeLayoutName)
    toolTipSubText: i18n("%1 (%2) • %3 zones", currentScreenName, currentScreenAspectRatio, currentZoneCount)
    toolTipTextFormat: Text.PlainText

    preferredRepresentation: Qt.application.name === "plasmawindowed"
        ? fullRepresentation
        : compactRepresentation

    compactRepresentation: CompactRepresentation {
        plasmoidItem: root
    }

    fullRepresentation: FullRepresentation {
        controller: root
    }

    // Context Menu Actions
    property PlasmaCore.Action autoArrangeAction: PlasmaCore.Action {
        text: i18n("Auto-Arrange Open Windows")
        icon.name: "view-grid"
        onTriggered: root.autoArrange()
    }

    property PlasmaCore.Action openEditorAction: PlasmaCore.Action {
        text: i18n("Open Layout Editor...")
        icon.name: "document-edit"
        onTriggered: root.openLayoutEditor()
    }

    property PlasmaCore.Action reloadAction: PlasmaCore.Action {
        text: i18n("Reload FancyZones")
        icon.name: "view-refresh"
        onTriggered: root.reloadAll()
    }

    Plasmoid.contextualActions: [
        autoArrangeAction,
        openEditorAction,
        reloadAction
    ]

    function loadBuiltinDefaults() {
        screenList = [
            {
                "id": "1",
                "name": "DP-3",
                "geometry": { "x": 0, "y": 0, "width": 5120, "height": 1440 },
                "aspectRatio": { "ratio": "32:9", "name": "Super Ultrawide", "decimal": 3.556, "badge": "32:9 Super Ultrawide" }
            }
        ];

        layoutsList = [
            {
                "id": "priority-grid",
                "name": "Priority Grid",
                "shortcut": 1,
                "zones": [[0.0, 0.0, 0.25, 1.0], [0.25, 0.0, 0.50, 1.0], [0.75, 0.0, 0.25, 1.0]]
            },
            {
                "id": "cols-3",
                "name": "3 Columns",
                "shortcut": 2,
                "zones": [[0.0, 0.0, 0.3333, 1.0], [0.3333, 0.0, 0.3334, 1.0], [0.6667, 0.0, 0.3333, 1.0]]
            },
            {
                "id": "cols-4",
                "name": "4 Columns",
                "shortcut": 3,
                "zones": [[0.0, 0.0, 0.25, 1.0], [0.25, 0.0, 0.25, 1.0], [0.50, 0.0, 0.25, 1.0], [0.75, 0.0, 0.25, 1.0]]
            },
            {
                "id": "dual-split",
                "name": "Dual 16:9 Split",
                "shortcut": 4,
                "zones": [[0.0, 0.0, 0.50, 1.0], [0.50, 0.0, 0.50, 1.0]]
            },
            {
                "id": "ultrawide-master-4",
                "name": "Master + 4 Flanks",
                "shortcut": 5,
                "zones": [[0.25, 0.0, 0.50, 1.0], [0.0, 0.0, 0.25, 0.5], [0.0, 0.5, 0.25, 0.5], [0.75, 0.0, 0.25, 0.5], [0.75, 0.5, 0.25, 0.5]]
            },
            {
                "id": "grid-3x2",
                "name": "Grid 3x2",
                "shortcut": 6,
                "zones": [[0.0, 0.0, 0.3333, 0.5], [0.3333, 0.0, 0.3334, 0.5], [0.6667, 0.0, 0.3333, 0.5], [0.0, 0.5, 0.3333, 0.5], [0.3333, 0.5, 0.3334, 0.5], [0.6667, 0.5, 0.3333, 0.5]]
            },
            {
                "id": "grid-2x2",
                "name": "Grid 2x2",
                "shortcut": 7,
                "zones": [[0.0, 0.0, 0.5, 0.5], [0.5, 0.0, 0.5, 0.5], [0.0, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5]]
            },
            {
                "id": "rows-2",
                "name": "2 Rows",
                "shortcut": 8,
                "zones": [[0.0, 0.0, 1.0, 0.5], [0.0, 0.5, 1.0, 0.5]]
            },
            {
                "id": "focus",
                "name": "Focus Zone",
                "shortcut": 9,
                "zones": [[0.20, 0.08, 0.60, 0.84]]
            }
        ];

        activeLayoutId = "cols-3";
    }

    function applyLayout(layoutId) {
        activeLayoutId = layoutId;
        Plasmoid.configuration.activeLayout = layoutId;
        Plasmoid.configuration.writeConfig();

        // 1. Update DBus Daemon and show visual highlight
        runCommand("qdbus6 org.kde.FancyZones /Manager org.kde.FancyZones.SetLayout " + currentScreenName + " " + layoutId);
        runCommand("qdbus6 org.kde.FancyZones /Manager org.kde.FancyZones.ShowZonesOverlay " + layoutId + " 500");

        // 2. Trigger shortcut in KWin for this layout
        for (var i = 0; i < layoutsList.length; i++) {
            if (layoutsList[i].id === layoutId && layoutsList[i].shortcut) {
                runCommand("qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut FancyZonesLayout" + layoutsList[i].shortcut);
                break;
            }
        }
    }

    function autoArrange() {
        runCommand("qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut FancyZonesAutoArrange");
    }

    function setGap(val) {
        gap = val;
        Plasmoid.configuration.gap = val;
        Plasmoid.configuration.writeConfig();
        var ctlPath = "/home/mrg/Developer/projects/fanzy-zones-kde/bin/fancyzones-ctl";
        runCommand("python3 " + ctlPath + " set-gap " + val);
    }

    function setMargin(val) {
        margin = val;
        Plasmoid.configuration.margin = val;
        Plasmoid.configuration.writeConfig();
        var ctlPath = "/home/mrg/Developer/projects/fanzy-zones-kde/bin/fancyzones-ctl";
        runCommand("python3 " + ctlPath + " set-margin " + val);
    }

    function snapActiveWindow(zoneNumber) {
        runCommand("qdbus6 org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.invokeShortcut FancyZonesSnapZone" + zoneNumber);
    }

    function openLayoutEditor() {
        root.expanded = false;
        runCommand("qdbus6 org.kde.FancyZones /Manager org.kde.FancyZones.OpenEditor || gio launch ~/.local/share/applications/org.kde.plasma.fancyzones.editor.desktop");
    }

    function reloadAll() {
        loadBuiltinDefaults();
        syncActiveLayoutFromDBus();
    }

    Component.onCompleted: {
        loadBuiltinDefaults();
        if (Plasmoid.configuration.activeLayout) {
            activeLayoutId = Plasmoid.configuration.activeLayout;
        }
        syncActiveLayoutFromDBus();
    }
}
