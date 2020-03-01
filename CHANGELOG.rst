Changelog
=========

1.1.2
-----
- Only data update

1.1.1
-----
- No code changes
- Removed daemon and client scripts since they are not yet part of the package and aren't working.
- Restructured some metadata for packaging and documentation

1.1
---
- Adding annotation automatically to the Ontology by default.
   - This should not break backwards compatibility, since all annotation data is stored in the repo itself and thus always present

1.0.1
-----
- Include data (HPO-Ontology and Annotation) directly in the repo
- Data updates:
   - HPO: hp/releases/2019-09-06
      - Added HPO terms: 14647 ==> 14831
   - Genes: Added genes 4073 ==> 4231
   - OMIM: Added diseases 7665 ==> 7677
   - OMIM excluded: Added excluded diseases 614 ==> 623

1.0
---
- First stable release