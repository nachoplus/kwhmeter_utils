tagname='0.1.3'
git tag --delete ${tagname}
git tag ${tagname}   -m "correccion del tipo de IVA  de las tablas de coeficientes"
git push origin :refs/tags/${tagname}
git push --tags origin main
rm dist/*
python3 -m build
twine upload -r pypi dist/*

