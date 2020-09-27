=========
CHANGELOG
=========

2.3.3 (2020/09/27)
------------------
* Add new repository state REMOVE_FAILED.
* Add programming languages and state fields for repositories.
* Optimization for repositories.
* Add repository status update on failed task (add failed / remove failed).

2.3.2 (2020/09/18)
------------------
* Add websocket events to handle tasks events and send async messages to the user.
* Rework service exceptions into the custom format.

2.3.1 (2020/08/26)
------------------
* Add programming languages list view (/api/v1/programming_languages/)
* Add repositories programming languages filter.

2.3.0 (2020/08/17)
------------------
* Add github & gitlab webhooks handle for issues & repositories.

2.2.0 (2020/08/09)
------------------
* Drop private repositories & orgagnizations support.
* Drop archived repositories support.
* Add repository state instead of is_added flag.

Available states:
- initial
- adding
- added
- removing
- removed
- add_failed

2.1.1 (2020/08/02)
------------------
* Improve swagger docs.

2.1.0 (2020/08/01)
------------------
* Add gitlab & github organization & membership sync.

2.0.0 (2020/07/28)
------------------
* Full project rework.

1.0.2 (2020/04/23)
------------------
* Project files structure refactoring.
* Removed django-nose dependency.
* Config url reworked.

1.0.1 (2020/04/09)
------------------
* First project release
* Basic Gitlab & GitHub auth.
* Repositories & Issues.
