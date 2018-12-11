TARGET=./build
ARCHS=amd64
LDFLAGS="-s -w"
GCFLAGS="all=-trimpath=${GOPATH}/src"
ASMFLAGS="all=-trimpath=${GOPATH}/src"
package="alfred-pritunl.alfredworkflow"

current:
	@echo "[+] Compiling gotunl..."\
	&& go build -ldflags=${LDFLAGS} -o ./src/gotunl\
	&& cd src; echo "[+] Creating ${package}..." && zip -r ../${package} *\
	&& echo "[+] Done." || echo "[!] There was an error"

clean:
	@rm -rf ${TARGET}/* ; \
	echo "Done."
