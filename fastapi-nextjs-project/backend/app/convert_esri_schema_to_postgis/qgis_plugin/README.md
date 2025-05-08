# MCP QGIS Plugin

This plugin integrates MCP functionalities into QGIS, enhancing its capabilities with new tools and features. This version adds a button to the QGIS toolbar.

## Features

-   Adds a button to the QGIS toolbar.
-   The button's icon is `icon.png`, located in the `resources` folder.
-   Integration of MCP functionalities into the QGIS environment.

## Installation

1.  **Download the plugin:** Download the plugin files to a local directory.
2.  **Copy to QGIS plugins directory:** Copy the `qgis_plugin` folder into your QGIS plugins directory. The location varies by operating system:
    -   **Windows:** `C:\Users\[Your Username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
    -   **macOS:** `/Users/[Your Username]/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
    -   **Linux:** `/home/[Your Username]/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
3.  **Enable the plugin:** Open QGIS, go to `Plugins` > `Manage and Install Plugins...`, find "MCP QGIS Plugin," and enable it.
4.  **Restart QGIS:** You might need to restart QGIS for the plugin to be fully loaded.

## Usage

Once installed and enabled, the MCP QGIS Plugin will add a new button to the QGIS toolbar. Click this button to access the plugin's functionalities.

## Project Structure

The plugin project is structured as follows:

-   **`qgis_plugin/`**: The root directory for the QGIS plugin.
    -   **`__init__.py`**:
        -   Marks the `qgis_plugin` directory as a Python package.
        -   Contains the `classFactory` function, which is the entry point for QGIS to load the plugin.
        -   Defines the loading mechanism for the `MCPPlugin` class from `main.py`.
    -   **`metadata.txt`**:
        -   Contains essential metadata about the plugin.
        -   Includes details like the plugin's name, version, compatible QGIS version, author, email, and a brief description.
    -   **`main.py`**:
        -   Contains the main plugin logic.
        -   Defines the `MCPPlugin` class, which inherits from `QgsPluginLayerRegistry`.
        -   Includes the `initGui` method to load a button into the QGIS toolbar.
        -   Includes the `unload` method to remove the button from the toolbar when the plugin is disabled.
    - **`resources/`**:
        - Contains resources used by the plugin.
        - `icon.png`: Contains the plugin icon.
    -   **`resources.qrc`**:
        -   XML file listing all the resources used by the plugin (e.g., icons, UI files).
        -   Specifies the resources that need to be compiled into a Python file.
    -   **`resources.py`**:
        -   Python file generated from `resources.qrc`.
        -   Contains the compiled resources that can be accessed by the plugin.
        - **DO NOT EDIT**. It will be overwritten by `compile.sh`.
    -   **`compile.sh`**:
        -   Shell script to compile `resources.qrc` into `resources.py`.
        -   Uses `pyrcc5` to generate the Python code from the resource definitions.
        - This file should be made executable by the user.

## Limitations of this Generated Version

This version of the plugin has some limitations due to the constraints of the development environment:

-   **Resource Compilation:** The `compile.sh` script to compile the resources is provided, but it is untested. This is because the development environment does not have access to PyQt5 `pyrcc5`. Therefore, the `resources.py` was not correctly generated. To be able to use it correctly the user must install PyQt5 and run the script again.
-   **Icon:** The code in `main.py` sets an icon for the button. A placeholder `icon.png` file is provided, but a real icon should be provided by the user.
-   **Functionality:** The plugin, in this version, does nothing except add and remove a button from the toolbar. This is because the environment does not allow us to test it. This button is a placeholder. The actual implementation of the plugin should be done by the user.
-   **Testing:** We can't test the plugin to see if it works in QGIS because we don't have QGIS in the development environment.
-   **No other QGIS library is included in the code:** The code only includes `QIcon`, `QAction`, `QgsPluginLayerRegistry` and `QToolBar`. To implement more features the user must add new QGIS librarys to the code.

## Contributing

Contributions to the MCP QGIS Plugin are welcome. If you have ideas for new features, improvements, or bug fixes, please feel free to fork the repository and submit a pull request.

## License

This project is licensed under the [License Name] - see the [LICENSE.md](LICENSE.md) file for details.