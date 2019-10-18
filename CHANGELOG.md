# Changelog

## v1.4 (18-10-2019)
- Updated the main gotunl library to use unix sockets (https://github.com/pritunl/pritunl-client-electron/commit/00792956a78c3426b473fefe69982fafa2cbc5e2)

## v1.3 (11-12-2018)
- Rewritten the workflow in GoLang
- Created 'python_version' branch to keep the old version

## v1.2 (10-11-2018)
- Added rerun feature to refresh the UI every second if there's a connection with 'Connecting' status
- Added notification when connecting
- Made some changes in listConnections() to provide more connection details
- Added <cmd> key modifier to show connection information
- Fixed how pritunl adds a connection name when importing a pritunl profile and tha name is null
- Refactoring

## v1.1 (09-11-2018)
- Replaced python's request module with urllib2 to make it a bit faster

## v1.0 (07-11-2018)
- First release
