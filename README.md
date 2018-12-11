
Pritunl Manager
==================

Manage your [Pritunl][pritunl] VPN connections from [Alfred][alfred].

![Alfred-Pritunl][demo]

Installation
------------

Download the `pritunl-manager-X.X.alfredworkflow` file from the [releases][release] section and double-click on it to import it into Alfred.

**Note:** Old python version can be found under python_version branch


Build
-----
Alternatively, you can build the gotunl binary and create the package yourself:

```bash
go get ./...
make
```


Usage
-----

- `.v [<query>]` — View and filter Pritunl VPN connections.
    - `↩` — Connect/disconnect selected connection.
- `.vdisconnect` — Disconnect all connections.


Acknowledgments
----------------

This workflow is based on [awgo][aw] (also [MIT-licensed][mit]) and [gotunl][gotunl] go libraries, and inspired by [Alfred VPN Manager][alfred-vpn-manager].

The original icons are from [Font Awesome][font-awesome] ([Creative Commons License][font-awesome-license]).


[pritunl]: https://github.com/pritunl/pritunl
[demo]: https://raw.githubusercontent.com/cghdev/alfred-pritunl/master/demo.gif "Alfred-Pritunl"
[font-awesome]: http://fontawesome.io/
[alfred]: http://www.alfredapp.com/
[aw]: https://github.com/deanishe/awgo
[mit]: http://opensource.org/licenses/MIT
[font-awesome-license]: https://fontawesome.com/license
[alfred-vpn-manager]: https://github.com/deanishe/alfred-vpn-manager/
[gotunl]: https://github.com/cghdev/gotunl
[release]: https://github.com/cghdev/alfred-pritunl/releases