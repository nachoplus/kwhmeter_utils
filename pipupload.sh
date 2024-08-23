tagname='0.1.5'
git tag --delete ${tagname}
git tag ${tagname}   -m "Ajuste precios unitarios peajes de potencia para años bisiestos"
git push origin :refs/tags/${tagname}
git push --tags origin main
rm dist/*
python3 -m build
twine upload -r pypi dist/*

