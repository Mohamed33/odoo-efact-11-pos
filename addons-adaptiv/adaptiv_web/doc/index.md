# Adaptiv Backend Theme documentation


## Installation

This theme has several additional modules which are automatically installed, depending on your installed Odoo features.
**You have to download** these additional modules (at no extra costs) and unzip them next to `adaptiv_web` to ensure a working installation:

[adaptiv_mail](https://apps.odoo.com/apps/modules/11.0/adaptiv_mail/)
Bridge module between adaptiv_web and mail.

[adaptiv_web_editor](https://apps.odoo.com/apps/modules/11.0/adaptiv_web_editor/)
Bridge module between adaptiv_web and web_editor.

[adaptiv_web_tour](https://apps.odoo.com/apps/modules/11.0/adaptiv_web_tour/)
Bridge module between adaptiv_web and web_tour.

[adaptiv_website](https://apps.odoo.com/apps/modules/11.0/adaptiv_website/)
Bridge module between adaptiv_web and website.

[adaptiv_portal](https://apps.odoo.com/apps/modules/11.0/adaptiv_portal/)
Bridge module between adaptiv_web and portal.

[adaptiv_web_settings_dashboard](https://apps.odoo.com/apps/modules/11.0/adaptiv_web_settings_dashboard/)
Bridge module between adaptiv_web and web_settings_dashboard.

[adaptiv_web_login](https://apps.odoo.com/apps/modules/11.0/adaptiv_web_login/)
Changes the Odoo login screen. Can cause problems when a custom frontend theme also modifies the login screen.

- Unzip all these modules next to eachother in your custom addons folder.
- Restart your Odoo instance.
- Install `adaptiv_web`.

### Upgrading to a newer version

If you have an existing installation of this theme, and whish to upgrade to a newer version. Follow
these instructions **CAREFULLY**.

Odoo provides 2 methods for upgrading a module:

1. Through the user interface.
2. Or through the Odoo CLI **RECOMMENDED**.

Depending on your current version and the new version you are upgrading to,
method **1** might not work. Follow the steps below to upgrade using
the CLI (command line interface).

Depending on the way you have installed Odoo, the location of the CLI script
might be different to the one described below.

- Unzip all new modules and replace the existing ones.
- Run `odoo.py -d YOUR_DB_NAME -u adaptiv_web`
- Restart your Odoo instance.

## Compatibility

Browser: Google chrome >=50, Firefox >=52, Safari >=10, IE >= 11, Edge >= 15
Odoo: 11.0 (tested against commit a0a5443e8f0606b561d2955449a690ea8a178703)
Odoo modules: All official Odoo modules. 3rd party modules with custom css might cause trouble.

### Odoo Enterprise

This theme can run on Odoo Enterprise as long as the `enterprise_web` module has been uninstalled.

## Release logs

### 11.0.1.104
- Fix critical qweb error that occured with latest builds of Odoo 11.
- Simplify theme css compilation while maintining same performance and caching features.
- Fix settings layout for Point of Sales.
- Add debrand title feature.
- Add debrand favicon feature.

### 11.0.1.103
- Correctly load and display the home action for a user (if configured).

### 11.0.1.102
- Fix style for listview delete button in newer versions of Odoo 11.

### 11.0.1.101
- Fixed missing `name` field in adaptiv_web.theme form view at `adaptiv_web`.
- Improved compatiblity with custom website themes in `adaptiv_portal`.
- Improved website top bar styles in `adaptiv_portal`.
- Improved Accounting recounciliation style compatibility in `adaptiv_web`.

### 11.0.1.100
- Added `adaptiv_web_login`

### 11.0.0.107
- Added support for Mobile kanban tabs.
- Fix an issue where the top menu did not reset after a failed action.
- Fix scrolling issue in settings dashboard.
- Align filter dropdown menu's to the right, for better mobile ux.
- Refractor responsive css for kanban views.
- Refractor manifest files.

### 11.0.0.106
- Improve calendar view colors to account for color blindness.
- Fix handling of empty fields, do not show "false" for these.
- Fix some layout issues.

### 11.0.0.105
- Fix missing custom filters in searchview favorites.
- Fix calendar view sidebar toggling.
- Fix some small layout issues.

### 11.0.0.104
- Show message/activity buttons in mobile navbar.
- Show profile button in mobile navbar.
- Fix accounting kanban cards in Firefox.
- Add support for task cover images in kanban.

### 11.0.0.103
- Fix form action bar in modal view.
- Fix text-overflow for form button box.

### 11.0.0.102
- Fix folding of statusbar buttons.

### 11.0.0.101
- Fix syntax errors for IE 11.0
- Fix menu translations
- Fix calendar avatar sizes.
- Adjust variables in compatibility.less for better colors with 3rd party styles



