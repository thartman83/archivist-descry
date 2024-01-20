EMACS=emacs
TANGLEFILE=README.org
OPENAPIYAML=openapi.yml
OPENAPIJS=openapi.json

tangle: ${TANGLEFILE}
	${EMACS} $< --batch --eval '(org-babel-tangle-file "${TANGLEFILE}")'
	cat "${OPENAPIYAML}" | yq > "${OPENAPIJS}"
