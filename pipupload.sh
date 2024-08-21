tagname='0.1.1'
git tag --delete ${tagname}
git tag ${tagname}   -m "correcion para precios nulos del la compensacion del gas"
git push origin :refs/tags/${tagname}
git push --tags origin main
rm dist/*
python3 -m build
twine upload -r pypi dist/*

