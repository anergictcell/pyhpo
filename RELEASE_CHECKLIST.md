# Release checklist

Before creating a new release, follow all the below steps:

- [ ] Create release branch from master
- [ ] Merge all feature branches into release branch
- [ ] Check if new HPO version is available
- [ ] Run all checks `make check`
- [ ] Run full test suite `make fulltests`
- [ ] Check test coverage `make coverage`
- [ ] Decide which type of version bump is required (master, minor, path)
- [ ] Update version in `pyhpo.__init__`
- [ ] Update `CHANGELOG.rst`
- [ ] Create new documentation
- [ ] Create version bump commit
- [ ] Push commit
- [ ] Crate version tag, push tag
- [ ] Merge into master

Update data:
1. Update ruff, black and mypy `pip install -U ruff mypy black`
2. pull latest changes of master
3. create new branch
4. run black and ruff fixes
5. Commit changes
6. run python script to download new data
7. Get numbers of terms, diseases etc, update integration-test