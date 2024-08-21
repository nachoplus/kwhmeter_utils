tagname='0.1.2'
git tag --delete ${tagname}
git tag ${tagname}   -m "actualizacion de las tablas de coeficientes"
git push origin :refs/tags/${tagname}
git push --tags origin main
rm dist/*
python3 -m build
twine upload -r pypi dist/*

