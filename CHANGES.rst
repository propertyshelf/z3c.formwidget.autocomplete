Changelog
=========

0.2.2 (2017-07-12)
------------------

- Need to keep SourceTerms intact. Terms must be cleared out to an empty list when the value no longer exists in the vocabulary.


0.2.1 (2017-07-04)
------------------

- With z3c.form >= 3.2.10 the self.terms is no longer compatible with SourceTerms. In some cases, it results in an error trying to iterate over the terms.


0.2 (2017-04-12)
----------------

- Necessary changes to work with z3c.form >= 3.2.10. Items is now a property and the "nothing selected" term must be handled differently.


0.1.1 (2017-04-11)
------------------

- Release for z3c.form <= 2.9.0


0.1  (2015-08-24)
-----------------

- Initial release.
