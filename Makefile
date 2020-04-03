TARGET=./build
ARCHS=amd64
LDFLAGS="-s -w"
package="alfred-pritunl.alfredworkflow"

current:
	@echo "[+] Compiling gotunl..."\
	&& go build -ldflags=${LDFLAGS} -trimpath -o ./src/gotunl\
	&& cd src; echo "[+] Creating ${package}..." && zip -r ../${package} *\
	&& echo "[+] Done." || echo "[!] There was an error"

clean:
	@rm -rf ${TARGET}/* ; \
	echo "Done."
